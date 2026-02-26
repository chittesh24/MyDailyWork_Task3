"""
Pre-trained Image Captioning using Hugging Face Transformers
Uses BLIP (Bootstrapped Language-Image Pre-training) for high-quality captions
"""
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import time
from loguru import logger


class PretrainedPredictor:
    """Image captioning using pre-trained BLIP model from Hugging Face."""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", device: str = None):
        """
        Initialize the pre-trained model.
        
        Args:
            model_name: Hugging Face model identifier
            device: Device to run on ('cuda' or 'cpu'). Auto-detected if None.
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Loading pre-trained model: {model_name} on {self.device}")
        
        try:
            # Load processor and model with memory optimization
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                low_cpu_mem_usage=True      # Optimize for low memory
            ).to(self.device)
            
            # Set to eval mode for inference
            self.model.eval()
            self.model_name = model_name
            logger.info("✓ Pre-trained model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load pre-trained model: {e}")
            raise
    
    def predict(self, image_path: str, method: str = "beam_search", max_length: int = 50, beam_width: int = 5) -> dict:
        """
        Generate caption for an image.
        
        Args:
            image_path: Path to the image file
            method: Generation method ('beam_search' or 'greedy')
            max_length: Maximum caption length
            
        Returns:
            Dictionary with caption, inference_time_ms, model_version, and method
        """
        start_time = time.time()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Process image
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption
            if method == "beam_search":
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=beam_width,
                    early_stopping=True
                )
            else:  # greedy
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=1
                )
            
            # Decode caption
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Calculate inference time
            inference_time_ms = (time.time() - start_time) * 1000
            
            return {
                "caption": caption,
                "inference_time_ms": round(inference_time_ms, 2),
                "model_version": self.model_name,
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise
    
    def predict_batch(self, image_paths: list, method: str = "beam_search", max_length: int = 50) -> list:
        """
        Generate captions for multiple images.
        
        Args:
            image_paths: List of image file paths
            method: Generation method
            max_length: Maximum caption length
            
        Returns:
            List of caption dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path, method, max_length)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results.append({
                    "caption": f"Error: {str(e)}",
                    "inference_time_ms": 0,
                    "model_version": self.model_name,
                    "method": method
                })
        
        return results


# Alternative: Smaller, faster model
class PretrainedPredictorLarge:
    """Image captioning using larger BLIP model for better quality."""
    
    def __init__(self, device: str = None):
        from inference.pretrained_predictor import PretrainedPredictor
        super().__init__(model_name="Salesforce/blip-image-captioning-large", device=device)
