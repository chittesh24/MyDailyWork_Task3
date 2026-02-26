"""
Optimized Pre-trained Image Captioning for Vercel Serverless Deployment
Features:
- Lazy model loading with singleton pattern
- Model caching to avoid reloading
- Lightweight dependencies
- Fast inference with optimized settings
"""
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import time
from loguru import logger
from functools import lru_cache
import os


class OptimizedPredictor:
    """Optimized image captioning for serverless environments."""
    
    _instance = None
    _model = None
    _processor = None
    _device = None
    
    def __new__(cls):
        """Singleton pattern to ensure model is loaded only once."""
        if cls._instance is None:
            cls._instance = super(OptimizedPredictor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", device: str = None):
        """
        Initialize the optimized predictor with lazy loading.
        
        Args:
            model_name: Hugging Face model identifier
            device: Device to run on ('cuda' or 'cpu'). Auto-detected if None.
        """
        # Only initialize once
        if self._model is not None:
            return
            
        self._device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        logger.info(f"Initializing optimized predictor on {self._device}")
    
    def _load_model(self):
        """Lazy load model only when needed."""
        if self._model is None:
            logger.info(f"Loading model: {self.model_name}")
            try:
                # Load processor with caching
                self._processor = BlipProcessor.from_pretrained(
                    self.model_name,
                    cache_dir=os.getenv('TRANSFORMERS_CACHE', None)
                )
                
                # Load model with memory optimization
                self._model = BlipForConditionalGeneration.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32 if self._device == 'cpu' else torch.float16,
                    low_cpu_mem_usage=True,
                    cache_dir=os.getenv('TRANSFORMERS_CACHE', None)
                ).to(self._device)
                
                # Optimize for inference
                self._model.eval()
                
                # Disable gradient computation globally for this model
                for param in self._model.parameters():
                    param.requires_grad = False
                
                logger.info("✓ Model loaded and optimized for inference")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    @lru_cache(maxsize=100)
    def _preprocess_image_cached(self, image_path: str):
        """Cache preprocessed images to avoid redundant processing."""
        image = Image.open(image_path).convert('RGB')
        # Resize to optimal size for faster processing
        max_size = 384  # BLIP base model optimal size
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return image
    
    def predict(
        self, 
        image_path: str, 
        method: str = "beam_search", 
        max_length: int = 30,  # Reduced from 50 for faster inference
        beam_width: int = 3,   # Reduced from 5 for faster inference
        **kwargs
    ) -> dict:
        """
        Generate caption for an image with optimized settings.
        
        Args:
            image_path: Path to the image file
            method: Generation method ('beam_search' or 'greedy')
            max_length: Maximum caption length (default 30 for speed)
            beam_width: Beam width (default 3 for speed)
            
        Returns:
            Dictionary with caption, inference_time_ms, model_version, and method
        """
        # Ensure model is loaded
        self._load_model()
        
        start_time = time.time()
        
        try:
            # Load and preprocess image with caching
            image = self._preprocess_image_cached(image_path)
            
            # Process image
            inputs = self._processor(image, return_tensors="pt").to(self._device)
            
            # Generate caption with no gradient computation
            with torch.no_grad():
                if method == "beam_search":
                    outputs = self._model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=beam_width,
                        early_stopping=True,
                        num_return_sequences=1,
                        use_cache=True  # Enable KV cache for faster generation
                    )
                else:  # greedy
                    outputs = self._model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=1,
                        do_sample=False,
                        use_cache=True
                    )
            
            # Decode caption
            caption = self._processor.decode(outputs[0], skip_special_tokens=True)
            
            # Calculate inference time
            inference_time_ms = (time.time() - start_time) * 1000
            
            return {
                "caption": caption,
                "inference_time_ms": round(inference_time_ms, 2),
                "model_version": f"{self.model_name}-optimized",
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise
        finally:
            # Clear GPU cache if using CUDA
            if self._device == 'cuda':
                torch.cuda.empty_cache()
    
    def predict_batch(
        self, 
        image_paths: list, 
        method: str = "beam_search", 
        max_length: int = 30,
        beam_width: int = 3
    ) -> list:
        """
        Generate captions for multiple images with batch processing.
        
        Args:
            image_paths: List of image file paths
            method: Generation method
            max_length: Maximum caption length
            beam_width: Beam width for beam search
            
        Returns:
            List of caption dictionaries
        """
        # Ensure model is loaded
        self._load_model()
        
        results = []
        
        # Process in batches for better performance
        batch_size = 4
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i+batch_size]
            
            try:
                # Load images
                images = [self._preprocess_image_cached(path) for path in batch_paths]
                
                # Process batch
                start_time = time.time()
                inputs = self._processor(images, return_tensors="pt", padding=True).to(self._device)
                
                with torch.no_grad():
                    if method == "beam_search":
                        outputs = self._model.generate(
                            **inputs,
                            max_length=max_length,
                            num_beams=beam_width,
                            early_stopping=True,
                            use_cache=True
                        )
                    else:
                        outputs = self._model.generate(
                            **inputs,
                            max_length=max_length,
                            num_beams=1,
                            use_cache=True
                        )
                
                # Decode captions
                captions = self._processor.batch_decode(outputs, skip_special_tokens=True)
                inference_time_ms = (time.time() - start_time) * 1000
                
                # Create results
                for caption in captions:
                    results.append({
                        "caption": caption,
                        "inference_time_ms": round(inference_time_ms / len(captions), 2),
                        "model_version": f"{self.model_name}-optimized",
                        "method": method
                    })
                    
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                # Add error results for failed batch
                for path in batch_paths:
                    results.append({
                        "caption": f"Error: {str(e)}",
                        "inference_time_ms": 0,
                        "model_version": self.model_name,
                        "method": method
                    })
        
        return results
    
    def clear_cache(self):
        """Clear the image preprocessing cache."""
        self._preprocess_image_cached.cache_clear()
        logger.info("Image cache cleared")


# Global singleton instance
_predictor_instance = None

def get_optimized_predictor(model_name: str = "Salesforce/blip-image-captioning-base", device: str = None):
    """
    Get or create the optimized predictor singleton.
    
    Args:
        model_name: Hugging Face model identifier
        device: Device to run on
        
    Returns:
        OptimizedPredictor instance
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = OptimizedPredictor(model_name=model_name, device=device)
    return _predictor_instance
