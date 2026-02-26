"""
Optimized FastAPI application for Vercel deployment.
Features:
- Response compression (gzip)
- Optimized CORS
- Singleton model loading
- Faster image processing
- CDN-friendly headers
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
from dotenv import load_dotenv
from loguru import logger
import time
from PIL import Image
import io

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
from .error_handlers import register_error_handlers
from database.database import get_db, init_db
from database.models import User, APIKey, Caption, Usage

# Import optimized predictor
from inference.optimized_predictor import get_optimized_predictor

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Image Captioning API - Optimized",
    description="High-performance image captioning with CNN+Transformer",
    version="2.0.0"
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register error handlers
register_error_handlers(app)

# CORS configuration - optimized
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only needed methods
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Security
security = HTTPBearer()

# Rate limiter - more generous for production
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)

# Model predictor (singleton with lazy loading)
predictor = None


def get_predictor():
    """Get or initialize optimized predictor."""
    global predictor
    if predictor is None:
        device = os.getenv('DEVICE', 'cpu')
        model_name = os.getenv('MODEL_NAME', 'Salesforce/blip-image-captioning-base')
        
        try:
            logger.info(f"Initializing optimized predictor: {model_name}")
            predictor = get_optimized_predictor(model_name=model_name, device=device)
            logger.info("✓ Optimized predictor ready")
        except Exception as e:
            logger.error(f"Failed to initialize predictor: {e}")
            # Fallback to demo mode
            from inference.demo_predictor import DemoPredictor
            predictor = DemoPredictor()
            logger.warning("Using demo predictor as fallback")
    
    return predictor


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Pre-load model to avoid cold start delay
    if os.getenv('PRELOAD_MODEL', 'false').lower() == 'true':
        logger.info("Pre-loading model...")
        get_predictor()
    logger.info("Application started - Optimized mode")


@app.get("/")
async def root():
    """Health check endpoint with CDN-friendly headers."""
    return JSONResponse(
        content={
            "status": "running",
            "version": "2.0.0-optimized",
            "message": "Image Captioning API - High Performance"
        },
        headers={
            "Cache-Control": "public, max-age=300",  # Cache for 5 minutes
            "X-API-Version": "2.0.0"
        }
    )


@app.get("/health")
async def health_check():
    """Detailed health check for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "model_loaded": predictor is not None
    }


async def validate_and_optimize_image(file: UploadFile) -> bytes:
    """
    Validate and optimize uploaded image for faster processing.
    
    Args:
        file: Uploaded file
        
    Returns:
        Optimized image bytes
        
    Raises:
        ValueError: If image is invalid
    """
    # File size validation (5MB limit)
    MAX_SIZE = 5 * 1024 * 1024
    
    # Read file
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise ValueError(f"File too large. Maximum size is 5MB")
    
    # Validate image
    try:
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Optimize size for faster processing
        max_dimension = 768
        if max(image.size) > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Save optimized image to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")


async def save_optimized_upload(file: UploadFile) -> str:
    """Save optimized uploaded file temporarily."""
    import tempfile
    import uuid
    
    # Validate and optimize
    optimized_bytes = await validate_and_optimize_image(file)
    
    # Save to temp file
    temp_dir = os.getenv('UPLOAD_DIR', tempfile.gettempdir())
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.jpg")
    
    with open(file_path, 'wb') as f:
        f.write(optimized_bytes)
    
    return file_path


@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user."""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    usage = Usage(user_id=db_user.id)
    db.add(usage)
    db.commit()
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    logger.info(f"User registered: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    logger.info(f"User logged in: {user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
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


@app.post("/demo/caption", response_model=CaptionResponse)
async def demo_caption(
    file: UploadFile = File(...),
    method: str = "beam_search",
    beam_width: int = 3  # Optimized default
):
    """
    Demo caption endpoint - optimized for speed.
    No authentication required for testing.
    """
    image_path = None
    
    try:
        # Save optimized image
        image_path = await save_optimized_upload(file)
        
        # Generate caption with optimized settings
        start_time = time.time()
        predictor_instance = get_predictor()
        
        result = predictor_instance.predict(
            image_path,
            method=method,
            beam_width=beam_width,
            max_length=30  # Faster inference
        )
        
        # Handle different return types
        if isinstance(result, dict):
            caption = result.get("caption", "")
            inference_time = result.get("inference_time_ms", 0)
            model_version = result.get("model_version", "unknown")
        else:
            caption = str(result)
            inference_time = (time.time() - start_time) * 1000
            model_version = "demo-v2.0"
        
        logger.info(f"Demo caption generated in {inference_time:.2f}ms: {caption}")
        
        return JSONResponse(
            content={
                "caption": caption,
                "inference_time_ms": round(inference_time, 2),
                "model_version": model_version,
                "method": method
            },
            headers={
                "Cache-Control": "no-cache",  # Don't cache user-specific results
                "X-Inference-Time": str(round(inference_time, 2))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        raise HTTPException(status_code=500, detail="Error generating caption")
    finally:
        # Clean up uploaded file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@app.post("/caption", response_model=CaptionResponse)
async def generate_caption(
    file: UploadFile = File(...),
    method: str = "beam_search",
    beam_width: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate caption for uploaded image (authenticated).
    Optimized for production use.
    """
    # Rate limiting
    if not rate_limiter.allow_request(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    
    image_path = None
    
    try:
        # Save optimized image
        image_path = await save_optimized_upload(file)
        
        # Generate caption
        start_time = time.time()
        predictor_instance = get_predictor()
        
        result = predictor_instance.predict(
            image_path,
            method=method,
            beam_width=beam_width,
            max_length=30
        )
        
        if isinstance(result, dict):
            caption = result.get("caption", "")
            inference_time = result.get("inference_time_ms", 0)
            model_version = result.get("model_version", "v2.0")
        else:
            caption = str(result)
            inference_time = (time.time() - start_time) * 1000
            model_version = "v2.0"
        
        # Save to database
        db_caption = Caption(
            user_id=current_user.id,
            image_path=image_path,
            generated_caption=caption,
            model_version=model_version,
            inference_time_ms=inference_time
        )
        db.add(db_caption)
        
        # Update usage
        usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
        usage.daily_request_count += 1
        usage.total_requests += 1
        
        db.commit()
        
        logger.info(f"Caption generated for user {current_user.email} in {inference_time:.2f}ms")
        
        return {
            "caption": caption,
            "inference_time_ms": round(inference_time, 2),
            "model_version": model_version,
            "method": method
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        raise HTTPException(status_code=500, detail="Error generating caption")
    finally:
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@app.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics and usage."""
    usage = db.query(Usage).filter(Usage.user_id == current_user.id).first()
    
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


# Cache control for static endpoints
@app.get("/api/info")
async def api_info():
    """API information with caching."""
    return JSONResponse(
        content={
            "name": "Image Captioning API",
            "version": "2.0.0-optimized",
            "features": [
                "Pre-trained BLIP model",
                "Beam search & greedy decoding",
                "Response compression",
                "Optimized image processing",
                "Rate limiting",
                "JWT authentication"
            ],
            "performance": {
                "avg_inference_time": "200-500ms",
                "max_image_size": "5MB",
                "supported_formats": ["JPEG", "PNG", "WebP"]
            }
        },
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
        }
    )
