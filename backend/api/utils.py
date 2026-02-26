"""
Utility functions for API.
"""

import os
import aiofiles
from fastapi import UploadFile
from PIL import Image
import io

# Configuration
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '5'))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/jpg'}
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')


def validate_image(file: UploadFile):
    """
    Validate uploaded image file.
    
    Security checks:
    - File size limit
    - MIME type validation
    - Image format verification
    
    Raises:
        ValueError: If validation fails
    """
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Invalid file type: {file.content_type}. "
            f"Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # File size will be checked during upload
    # Additional validation can be done on file content


async def save_upload_file(file: UploadFile) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        file: Uploaded file
        
    Returns:
        filepath: Path to saved file
        
    Raises:
        ValueError: If file too large or invalid
    """
    # Create upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    import uuid
    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Read and validate file size
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File too large: {len(contents) / 1024 / 1024:.2f}MB. "
            f"Maximum size: {MAX_FILE_SIZE_MB}MB"
        )
    
    # Verify it's a valid image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    return filepath


def cleanup_old_uploads(max_age_hours: int = 24):
    """
    Clean up old uploaded files.
    
    Args:
        max_age_hours: Maximum age of files to keep
    """
    import time
    
    if not os.path.exists(UPLOAD_DIR):
        return
    
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if os.path.isfile(filepath):
            age = now - os.path.getmtime(filepath)
            
            if age > max_age_seconds:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
