"""
FastAPI application with authentication and rate limiting.
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv
from loguru import logger
import time

from .auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_token,
    create_api_key,
    verify_api_key
)
from .schemas import (
    UserCreate,
    UserLogin,
    Token,
    CaptionRequest,
    CaptionResponse,
    APIKeyResponse,
    UserStats
)
from .rate_limiter import RateLimiter
from .utils import validate_image, save_upload_file
from database.database import get_db, init_db
from database.models import User, APIKey, Caption, Usage
from inference.predictor import CaptionPredictor
from .error_handlers import register_error_handlers

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Image Captioning API",
    description="Production-grade image captioning with CNN+Transformer",
    version="1.0.0"
)

# Register error handlers
register_error_handlers(app)

# CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Rate limiter
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

# Model predictor (lazy loading)
predictor = None


def get_predictor():
    """Get or initialize predictor with improved model."""
    global predictor
    if predictor is None:
        device = os.getenv('DEVICE', 'cpu')
        use_pretrained = os.getenv('USE_PRETRAINED', 'true').lower() == 'true'
        
        if use_pretrained:
            # Use improved BLIP model with optimized parameters
            try:
                logger.info("Loading improved BLIP model with optimized inference...")
                from inference.improved_predictor import get_improved_predictor
                model_name = os.getenv('PRETRAINED_MODEL', 'Salesforce/blip-image-captioning-base')
                predictor = get_improved_predictor(model_name=model_name, device=device)
                logger.info("✓ Improved model loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load improved model: {e}")
                logger.info("Trying fallback to standard pretrained model...")
                try:
                    from inference.pretrained_predictor import PretrainedPredictor
                    predictor = PretrainedPredictor(model_name=model_name, device=device)
                    logger.info("✓ Standard pre-trained model loaded")
                except Exception as e2:
                    logger.error(f"Fallback failed: {e2}")
                    logger.warning("Using demo predictor - captions will be random!")
                    from inference.demo_predictor import DemoPredictor
                    predictor = DemoPredictor()
        else:
            # Use custom trained model
            model_path = os.getenv('MODEL_CHECKPOINT_PATH', 'checkpoints/best_model.pth')
            vocab_path = os.getenv('VOCAB_PATH', 'checkpoints/vocab.json')
            
            try:
                predictor = CaptionPredictor(
                    model_path=model_path,
                    vocab_path=vocab_path,
                    device=device
                )
                logger.info("Custom model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load custom model: {e}")
                logger.info("Using demo predictor instead")
                from inference.demo_predictor import DemoPredictor
                predictor = DemoPredictor()
    
    return predictor


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Application started")


@app.get("/")
@app.head("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "version": "1.0.0",
        "message": "Image Captioning API"
    }


@app.get("/health")
async def health_check():
    """Explicit health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "image-captioning-api",
        "version": "1.0.0"
    }


@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user.
    
    Security:
    - Password hashed with bcrypt
    - Email validation
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create usage record
    usage = Usage(user_id=db_user.id)
    db.add(usage)
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    logger.info(f"User registered: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user.
    
    Returns JWT token for authentication.
    """
    # Get user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    logger.info(f"User logged in: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    
    Security:
    - Validates JWT signature
    - Checks token expiration
    """
    token = credentials.credentials
    user_id = decode_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@app.post("/api-keys/generate", response_model=APIKeyResponse)
async def generate_api_key(
    name: str = "Default Key",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate new API key for user.
    
    Security:
    - API key shown only once
    - Stored as hashed value
    - Cannot retrieve original key
    """
    # Generate key
    api_key, hashed_key = create_api_key()
    
    # Store in database
    db_key = APIKey(
        user_id=current_user.id,
        hashed_key=hashed_key,
        name=name
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    logger.info(f"API key generated for user {current_user.email}")
    
    return {
        "api_key": api_key,
        "name": name,
        "created_at": db_key.created_at,
        "message": "Save this key securely. It won't be shown again."
    }


@app.get("/api-keys/list")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys for user (without revealing actual keys)."""
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    
    return [
        {
            "id": key.id,
            "name": key.name,
            "created_at": key.created_at,
            "last_used": key.last_used,
            "is_active": bool(key.is_active)
        }
        for key in keys
    ]


@app.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = 0
    db.commit()
    
    logger.info(f"API key {key_id} revoked for user {current_user.email}")
    
    return {"message": "API key revoked successfully"}


async def verify_api_key_auth(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify API key authentication.
    
    Security:
    - Compares hashed values
    - Checks if key is active
    - Updates last_used timestamp
    """
    api_key = credentials.credentials
    
    # Verify key
    user_id = verify_api_key(api_key, db)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@app.post("/caption", response_model=CaptionResponse)
async def generate_caption(
    file: UploadFile = File(...),
    method: str = "beam_search",
    beam_width: int = 5,
    current_user: User = Depends(verify_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    Generate caption for uploaded image.
    
    Security:
    - File size validation (max 5MB)
    - MIME type validation
    - Rate limiting
    - API key authentication
    """
    # Rate limiting
    if not rate_limiter.allow_request(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    
    # Validate image
    try:
        validate_image(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Save file temporarily
    try:
        image_path = await save_upload_file(file)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error processing image")
    
    # Generate caption
    try:
        start_time = time.time()
        
        predictor = get_predictor()
        
        # Use improved prediction with quality check
        result = predictor.predict(
            image_path,
            method=method,
            beam_width=beam_width,
            max_length=50,
            temperature=1.0,
            return_probs=True
        )
        
        # Handle different return types
        if isinstance(result, dict):
            caption = result.get("caption", "")
        else:
            caption = str(result)
        
        inference_time = (time.time() - start_time) * 1000  # ms
        
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail="Error generating caption")
    
    # Save to database
    db_caption = Caption(
        user_id=current_user.id,
        image_path=image_path,
        generated_caption=caption,
        model_version="v1.0",
        inference_time_ms=inference_time
    )
    db.add(db_caption)
    
    # Update usage
    usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
    usage.daily_request_count += 1
    usage.total_requests += 1
    
    db.commit()
    
    logger.info(f"Caption generated for user {current_user.email}: {caption}")
    
    return {
        "caption": caption,
        "inference_time_ms": inference_time,
        "model_version": "v1.0",
        "method": method
    }


@app.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics and usage."""
    usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
    
    # Get recent captions
    recent_captions = db.query(Caption).filter(
        Caption.user_id == current_user.id
    ).order_by(Caption.timestamp.desc()).limit(10).all()
    
    return {
        "email": current_user.email,
        "daily_requests": usage.daily_request_count if usage else 0,
        "total_requests": usage.total_requests if usage else 0,
        "recent_captions": [
            {
                "caption": c.generated_caption,
                "timestamp": c.timestamp,
                "inference_time_ms": c.inference_time_ms
            }
            for c in recent_captions
        ]
    }


@app.get("/history")
async def get_caption_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get caption history for user."""
    captions = db.query(Caption).filter(
        Caption.user_id == current_user.id
    ).order_by(Caption.timestamp.desc()).limit(limit).offset(offset).all()
    
    total = db.query(Caption).filter(Caption.user_id == current_user.id).count()
    
    return {
        "total": total,
        "captions": [
            {
                "id": c.id,
                "caption": c.generated_caption,
                "timestamp": c.timestamp,
                "model_version": c.model_version,
                "inference_time_ms": c.inference_time_ms
            }
            for c in captions
        ]
    }


@app.post("/demo/caption", response_model=CaptionResponse)
async def demo_caption(
    file: UploadFile = File(...),
    method: str = "beam_search",
    beam_width: int = 5
):
    """
    Demo caption endpoint - no authentication required.
    
    For testing purposes only. Use /caption with API key for production.
    """
    # Validate image
    try:
        validate_image(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Save file temporarily
    try:
        image_path = await save_upload_file(file)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error processing image")
    
    # Generate caption
    try:
        predictor = get_predictor()
        result = predictor.predict(
            image_path,
            method=method,
            beam_width=beam_width
        )
        
        # Handle different return types (dict or string)
        if isinstance(result, dict):
            caption = result.get("caption", "")
            inference_time = result.get("inference_time_ms", 0)
            model_version = result.get("model_version", "unknown")
        else:
            caption = str(result)
            inference_time = 0
            model_version = "demo-v1.0"
        
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        # Clean up
        if os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)
    
    logger.info(f"Demo caption generated: {caption}")
    
    return {
        "caption": caption,
        "inference_time_ms": inference_time,
        "model_version": model_version,
        "method": method
    }
