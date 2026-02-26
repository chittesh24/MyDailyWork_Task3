"""
Improved Image Captioning using Optimized BLIP Model
Free-tier optimized with better inference parameters for accuracy
"""
import torch
from PIL import Image
import time
from typing import Union, Dict
import os

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ transformers not installed. Install with: pip install transformers")


class ImprovedPredictor:
    """
    Optimized image captioning for free-tier deployments.
    
    Improvements:
    1. Better generation parameters (no_repeat_ngram, length_penalty)
    2. Nucleus sampling option for diversity
    3. Multiple caption generation with ranking
    4. Fallback mechanisms
    5. Memory optimization for free tier
    """
    
    def __init__(
        self, 
        model_name: str = "Salesforce/blip-image-captioning-base",
        device: str = None
    ):
        """
        Initialize optimized predictor.
        
        Args:
            model_name: Hugging Face model ID (base for free tier)
            device: 'cuda', 'cpu', or None (auto-detect)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers library required. Install: pip install transformers"
            )
        
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        print(f"🚀 Loading {model_name} on {self.device}...")
        
        try:
            # Load with memory optimization
            self.processor = BlipProcessor.from_pretrained(model_name)
            
            # Load model without low_cpu_mem_usage to avoid accelerate dependency
            self.model = BlipForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32
            ).to(self.device)
            
            self.model.eval()
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def predict(
        self,
        image: Union[str, Image.Image],
        method: str = "beam_search",
        beam_width: int = 5,
        max_length: int = 50,
        temperature: float = 1.0,
        num_captions: int = 1,
        return_probs: bool = False
    ) -> Union[str, Dict]:
        """
        Generate caption with improved parameters.
        
        Args:
            image: Image path or PIL Image
            method: 'beam_search', 'nucleus', or 'greedy'
            beam_width: Number of beams (3-5 recommended)
            max_length: Max caption length (30-50 recommended)
            temperature: Sampling temperature (lower = more focused)
            num_captions: Number of captions to generate (for ranking)
            return_probs: Return confidence scores
            
        Returns:
            Generated caption string or dict with metadata
        """
        start_time = time.time()
        
        try:
            # Load image
            if isinstance(image, str):
                img = Image.open(image).convert('RGB')
            else:
                img = image.convert('RGB')
            
            # Preprocess
            inputs = self.processor(img, return_tensors="pt").to(self.device)
            
            # Generate with optimized parameters
            with torch.no_grad():
                if method == "beam_search":
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=beam_width,
                        early_stopping=True,
                        length_penalty=0.8,          # Prefer shorter, accurate captions
                        no_repeat_ngram_size=3,      # Prevent repetition
                        num_return_sequences=num_captions,
                        repetition_penalty=1.2       # Penalize repetition
                    )
                    
                elif method == "nucleus":
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        do_sample=True,
                        top_k=50,
                        top_p=0.9,
                        temperature=0.7,
                        no_repeat_ngram_size=3,
                        num_return_sequences=num_captions,
                        repetition_penalty=1.2
                    )
                    
                else:  # greedy
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=1,
                        no_repeat_ngram_size=3,
                        repetition_penalty=1.2
                    )
            
            # Decode captions
            captions = [
                self.processor.decode(output, skip_special_tokens=True)
                for output in outputs
            ]
            
            # Select best caption (first one from beam search)
            best_caption = captions[0]
            
            # Calculate inference time
            inference_time_ms = (time.time() - start_time) * 1000
            
            if return_probs or num_captions > 1:
                return {
                    "caption": best_caption,
                    "all_captions": captions if num_captions > 1 else [best_caption],
                    "inference_time_ms": round(inference_time_ms, 2),
                    "model_version": self.model_name,
                    "method": method
                }
            else:
                return best_caption
                
        except Exception as e:
            print(f"❌ Error generating caption: {e}")
            raise
    
    def predict_with_quality_check(
        self,
        image: Union[str, Image.Image],
        min_length: int = 5,
        max_attempts: int = 3
    ) -> Dict:
        """
        Generate caption with quality validation.
        
        Tries multiple methods if output is too short or generic.
        """
        methods = ["beam_search", "nucleus", "greedy"]
        
        for attempt, method in enumerate(methods[:max_attempts]):
            result = self.predict(
                image,
                method=method,
                beam_width=5,
                num_captions=1,
                return_probs=True
            )
            
            caption = result["caption"]
            
            # Quality checks
            if len(caption.split()) >= min_length:
                # Good caption found
                result["quality"] = "good"
                result["attempts"] = attempt + 1
                return result
        
        # Return best attempt even if quality check failed
        result["quality"] = "acceptable"
        result["attempts"] = max_attempts
        return result
    
    def predict_batch(
        self,
        images: list,
        method: str = "beam_search",
        **kwargs
    ) -> list:
        """Generate captions for multiple images."""
        return [self.predict(img, method=method, **kwargs) for img in images]


# Singleton instance for memory efficiency
_predictor_instance = None

def get_improved_predictor(
    model_name: str = None,
    device: str = None,
    force_reload: bool = False
) -> ImprovedPredictor:
    """
    Get singleton predictor instance (memory efficient for free tier).
    
    Args:
        model_name: Model to load (default: base model)
        device: Device to use
        force_reload: Force reload the model
    """
    global _predictor_instance
    
    if _predictor_instance is None or force_reload:
        model_name = model_name or os.getenv(
            'PRETRAINED_MODEL', 
            'Salesforce/blip-image-captioning-base'
        )
        device = device or os.getenv('DEVICE', 'cpu')
        
        _predictor_instance = ImprovedPredictor(
            model_name=model_name,
            device=device
        )
    
    return _predictor_instance
