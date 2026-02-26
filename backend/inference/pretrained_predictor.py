"""
Pre-trained Image Captioning using Hugging Face Transformers
Supports multiple models: BLIP, ViT-GPT2, etc.
"""
import torch
from PIL import Image
import time
from loguru import logger

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    BLIP_AVAILABLE = True
except ImportError:
    BLIP_AVAILABLE = False

try:
    from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
    VIT_GPT2_AVAILABLE = True
except ImportError:
    VIT_GPT2_AVAILABLE = False


class PretrainedPredictor:
    """Image captioning using pre-trained BLIP model from Hugging Face with lazy loading."""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", device: str = None):
        """
        Initialize the pre-trained model (lazy loading for memory efficiency).
        
        Args:
            model_name: Hugging Face model identifier
            device: Device to run on ('cuda' or 'cpu'). Auto-detected if None.
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.processor = None
        self.model = None
        logger.info(f"Predictor initialized (lazy loading). Model: {model_name}, Device: {self.device}")
    
    def _load_model(self):
        """Load model on first use (lazy loading) to save memory."""
        if self.model is not None:
            return  # Already loaded
        
        logger.info(f"Loading {self.model_name} on {self.device}...")
        
        try:
            # Detect model type and load accordingly
            if "vit-gpt2" in self.model_name.lower():
                # ViT-GPT2 model (smaller, ~300MB)
                if not VIT_GPT2_AVAILABLE:
                    raise ImportError("VisionEncoderDecoderModel not available")
                
                self.model = VisionEncoderDecoderModel.from_pretrained(
                    self.model_name,
                    low_cpu_mem_usage=True
                ).to(self.device)
                self.processor = ViTImageProcessor.from_pretrained(self.model_name)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.is_vit_gpt2 = True
                
            else:
                # BLIP model (default)
                if not BLIP_AVAILABLE:
                    raise ImportError("BLIP model not available")
                
                self.processor = BlipProcessor.from_pretrained(self.model_name)
                self.model = BlipForConditionalGeneration.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                    low_cpu_mem_usage=True,
                ).to(self.device)
                self.is_vit_gpt2 = False
            
            # Set to eval mode for inference
            self.model.eval()
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
        # Load model on first use
        self._load_model()
        
        start_time = time.time()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Process based on model type
            if hasattr(self, 'is_vit_gpt2') and self.is_vit_gpt2:
                # ViT-GPT2 processing
                pixel_values = self.processor(image, return_tensors="pt").pixel_values.to(self.device)
                
                # Generate caption
                if method == "beam_search":
                    outputs = self.model.generate(
                        pixel_values,
                        max_length=max_length,
                        num_beams=beam_width,
                        early_stopping=True,
                    )
                else:  # greedy
                    outputs = self.model.generate(
                        pixel_values,
                        max_length=max_length,
                    )
                
                # Decode caption
                caption = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                # BLIP processing
                inputs = self.processor(image, return_tensors="pt").to(self.device)
                
                # Generate caption with improved parameters
                if method == "beam_search":
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=beam_width,
                        early_stopping=True,
                        length_penalty=1.0,
                        no_repeat_ngram_size=3,
                        temperature=1.0
                    )
                else:  # greedy
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=1,
                        no_repeat_ngram_size=3
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
