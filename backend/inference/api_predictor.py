"""
Image Captioning using External API (Hugging Face Inference API)
Zero memory footprint - no model loading required!
"""
import requests
import time
from loguru import logger
import os


class APIPredictor:
    """Image captioning using Hugging Face Inference API - NO local model needed!"""
    
    def __init__(self, model_name: str = "nlpconnect/vit-gpt2-image-captioning", api_key: str = None):
        """
        Initialize API predictor.
        
        Args:
            model_name: Hugging Face model identifier
            api_key: Hugging Face API key (optional, can use free tier)
        """
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"API Predictor initialized: {model_name}")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Using API Key: {'Yes' if self.api_key else 'No (rate limited)'}")
    
    def predict(self, image_path: str, method: str = "beam_search", max_length: int = 50, beam_width: int = 5) -> dict:
        """
        Generate caption for an image using Hugging Face API.
        
        Args:
            image_path: Path to the image file
            method: Generation method (ignored for API)
            max_length: Maximum caption length (ignored for API)
            
        Returns:
            Dictionary with caption, inference_time_ms, model_version, and method
        """
        start_time = time.time()
        
        try:
            # Read image file
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            logger.info(f"Sending request to Hugging Face API: {self.api_url}")
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=image_data,
                timeout=30
            )
            
            # Check for errors
            if response.status_code == 503:
                logger.warning("Model is loading on Hugging Face servers, retrying...")
                # Model is loading, wait and retry
                time.sleep(5)
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    data=image_data,
                    timeout=30
                )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            logger.info(f"API Response: {result}")
            
            # Extract caption
            if isinstance(result, list) and len(result) > 0:
                caption = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                caption = result.get("generated_text", "")
            else:
                caption = str(result)
            
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "caption": caption,
                "inference_time_ms": round(inference_time, 2),
                "model_version": self.model_name,
                "method": "huggingface_api",
                "api_used": True
            }
            
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            raise Exception("Image captioning service timeout - please try again")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Image captioning service error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Failed to generate caption: {str(e)}")
    
    def batch_predict(self, image_paths: list, method: str = "beam_search", max_length: int = 50) -> list:
        """
        Generate captions for multiple images.
        
        Args:
            image_paths: List of image file paths
            method: Generation method (ignored for API)
            max_length: Maximum caption length (ignored for API)
            
        Returns:
            List of dictionaries with captions and metadata
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path, method, max_length)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")
                results.append({
                    "caption": "",
                    "error": str(e),
                    "model_version": self.model_name
                })
        return results
