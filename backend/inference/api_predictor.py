"""
Image Captioning using Hugging Face Inference API.
Zero memory footprint - runs entirely on HuggingFace servers for free.
Uses the new router endpoint that replaced the deprecated api-inference endpoint.
"""
import requests
import time
from loguru import logger
import os
import base64


class APIPredictor:
    """Image captioning using Hugging Face Inference API - no local model needed."""

    # Models to try in order - all free on HF Inference API
    FALLBACK_MODELS = [
        "Salesforce/blip-image-captioning-base",
        "nlpconnect/vit-gpt2-image-captioning",
        "microsoft/git-base-coco",
    ]

    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        logger.info(f"APIPredictor ready | model={model_name} | key={'yes' if self.api_key else 'no'}")

    def _call_hf_api(self, image_data: bytes, model: str, timeout: int = 60) -> requests.Response:
        """Call HF Inference API using raw binary body + Authorization header."""
        # Always re-read api_key from env at call time (in case env was set after import)
        api_key = self.api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        headers = {"Content-Type": "application/octet-stream"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        logger.info(f"HF API call → {url} | auth={'yes' if api_key else 'NO KEY SET'}")
        return requests.post(url, headers=headers, data=image_data, timeout=timeout)

    def predict(self, image_path: str, method: str = "beam_search", max_length: int = 50, beam_width: int = 5) -> dict:
        """Generate caption for an image via Hugging Face Inference API."""
        start_time = time.time()

        with open(image_path, "rb") as f:
            image_data = f.read()

        # Re-read api_key at predict time (env may have been set after startup)
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", self.api_key)
        if not self.api_key:
            raise Exception("HUGGINGFACE_API_KEY is not set. Please add it to your Render environment variables.")

        # Try primary model then fallbacks
        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for model in models_to_try:
            try:
                logger.info(f"Trying HF API with model: {model}")
                response = self._call_hf_api(image_data, model)

                # Handle model loading (503) — wait and retry once
                if response.status_code == 503:
                    logger.warning(f"Model {model} is warming up, retrying in 10s...")
                    time.sleep(10)
                    response = self._call_hf_api(image_data, model, timeout=90)

                # Skip models that are gone/unavailable
                if response.status_code in (404, 410):
                    logger.warning(f"Model {model} unavailable (HTTP {response.status_code}), trying next...")
                    last_error = f"Model {model} returned HTTP {response.status_code}"
                    continue

                # 401 means bad/missing token — raise immediately (no point trying other models)
                if response.status_code == 401:
                    raise Exception("HuggingFace API key is invalid or missing. Please check HUGGINGFACE_API_KEY in Render env vars.")

                response.raise_for_status()
                result = response.json()
                logger.info(f"HF API response from {model}: {result}")

                # Extract caption from response
                if isinstance(result, list) and len(result) > 0:
                    caption = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    caption = result.get("generated_text", "")
                else:
                    caption = str(result)

                if not caption:
                    last_error = f"Empty caption from {model}"
                    logger.warning(last_error)
                    continue

                inference_time_ms = round((time.time() - start_time) * 1000, 2)
                return {
                    "caption": caption,
                    "inference_time_ms": inference_time_ms,
                    "model_version": model,
                    "method": "huggingface_api",
                    "api_used": True,
                }

            except requests.exceptions.Timeout:
                last_error = f"Timeout for model {model}"
                logger.warning(last_error)
                continue
            except Exception as e:
                last_error = str(e)
                logger.error(f"Model {model} failed: {e}")
                raise  # Re-raise auth errors immediately

        raise Exception(f"All HuggingFace API models failed. Last error: {last_error}")
    
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
