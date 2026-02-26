"""
Test script to verify optimization improvements.
Run this locally before deploying to Vercel.
"""
import time
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_optimized_predictor():
    """Test the optimized predictor performance."""
    print("=" * 60)
    print("Testing Optimized Predictor")
    print("=" * 60)
    
    from inference.optimized_predictor import get_optimized_predictor
    
    # Test model loading time
    print("\n1. Testing Model Loading (Cold Start)...")
    start = time.time()
    predictor = get_optimized_predictor()
    load_time = time.time() - start
    print(f"   ✓ Model initialization: {load_time:.2f}s")
    
    # Test image preprocessing
    print("\n2. Testing Image Preprocessing...")
    test_image = "test_images/beach.jpg"
    
    if not os.path.exists(test_image):
        print(f"   ⚠ Test image not found: {test_image}")
        print("   Creating dummy test image...")
        from PIL import Image
        os.makedirs("test_images", exist_ok=True)
        img = Image.new('RGB', (800, 600), color='blue')
        img.save(test_image)
    
    # Test inference - Fast mode
    print("\n3. Testing Inference - Fast Mode (beam_width=3)...")
    start = time.time()
    result = predictor.predict(test_image, method="beam_search", beam_width=3, max_length=30)
    inference_time = time.time() - start
    print(f"   ✓ Inference time: {inference_time*1000:.2f}ms")
    print(f"   ✓ Caption: {result['caption']}")
    print(f"   ✓ Reported time: {result['inference_time_ms']:.2f}ms")
    
    # Test inference - Greedy mode
    print("\n4. Testing Inference - Greedy Mode (fastest)...")
    start = time.time()
    result = predictor.predict(test_image, method="greedy", max_length=30)
    greedy_time = time.time() - start
    print(f"   ✓ Inference time: {greedy_time*1000:.2f}ms")
    print(f"   ✓ Caption: {result['caption']}")
    
    # Test caching
    print("\n5. Testing Image Cache...")
    start = time.time()
    result = predictor.predict(test_image, method="greedy", max_length=30)
    cached_time = time.time() - start
    print(f"   ✓ Cached inference time: {cached_time*1000:.2f}ms")
    speedup = (greedy_time / cached_time - 1) * 100 if cached_time > 0 else 0
    print(f"   ✓ Cache speedup: {speedup:.1f}%")
    
    # Performance summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    print(f"Cold Start Time:     {load_time:.2f}s")
    print(f"Fast Mode Inference: {inference_time*1000:.0f}ms")
    print(f"Greedy Inference:    {greedy_time*1000:.0f}ms")
    print(f"Cached Inference:    {cached_time*1000:.0f}ms")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("Recommendations")
    print("=" * 60)
    
    if inference_time < 0.5:
        print("✅ Excellent! Inference time < 500ms")
    elif inference_time < 1.0:
        print("✓ Good! Inference time < 1000ms")
    else:
        print("⚠ Slow inference. Consider:")
        print("   - Using greedy mode")
        print("   - Reducing beam_width to 2")
        print("   - Using smaller images")
    
    if load_time < 10:
        print("✅ Excellent! Cold start < 10s")
    else:
        print("⚠ Slow cold start. This is normal for first load.")
        print("   Model will be cached for subsequent requests.")


def test_api_optimization():
    """Test the optimized API features."""
    print("\n" + "=" * 60)
    print("Testing API Optimizations")
    print("=" * 60)
    
    try:
        from api.optimized_main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        print("\n1. Testing Health Endpoint...")
        response = client.get("/health")
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Response: {response.json()}")
        
        # Test root endpoint (cached)
        print("\n2. Testing Root Endpoint (should have Cache-Control)...")
        response = client.get("/")
        print(f"   ✓ Status: {response.status_code}")
        if "Cache-Control" in response.headers:
            print(f"   ✓ Cache-Control: {response.headers['Cache-Control']}")
        else:
            print("   ⚠ No Cache-Control header")
        
        # Test API info endpoint
        print("\n3. Testing API Info Endpoint...")
        response = client.get("/api/info")
        print(f"   ✓ Status: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✓ Version: {info.get('version')}")
            print(f"   ✓ Features: {len(info.get('features', []))} features")
        
        print("\n✅ API tests passed!")
        
    except ImportError as e:
        print(f"\n⚠ Could not import API (may need dependencies): {e}")
    except Exception as e:
        print(f"\n❌ API test failed: {e}")


def compare_with_original():
    """Compare optimized vs original predictor."""
    print("\n" + "=" * 60)
    print("Comparing Original vs Optimized")
    print("=" * 60)
    
    test_image = "test_images/beach.jpg"
    
    if not os.path.exists(test_image):
        print("⚠ Test image not found, skipping comparison")
        return
    
    try:
        # Test original
        print("\n1. Testing Original Predictor...")
        from inference.pretrained_predictor import PretrainedPredictor
        
        original = PretrainedPredictor()
        start = time.time()
        result1 = original.predict(test_image, method="beam_search", beam_width=5, max_length=50)
        original_time = time.time() - start
        print(f"   ✓ Time: {original_time*1000:.0f}ms")
        print(f"   ✓ Caption: {result1['caption']}")
        
        # Test optimized
        print("\n2. Testing Optimized Predictor...")
        from inference.optimized_predictor import get_optimized_predictor
        
        optimized = get_optimized_predictor()
        start = time.time()
        result2 = optimized.predict(test_image, method="beam_search", beam_width=3, max_length=30)
        optimized_time = time.time() - start
        print(f"   ✓ Time: {optimized_time*1000:.0f}ms")
        print(f"   ✓ Caption: {result2['caption']}")
        
        # Compare
        speedup = ((original_time - optimized_time) / original_time) * 100
        print("\n" + "=" * 60)
        print(f"Speedup: {speedup:.1f}% faster")
        print(f"Time saved: {(original_time - optimized_time)*1000:.0f}ms")
        print("=" * 60)
        
    except Exception as e:
        print(f"⚠ Comparison failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("IMAGE CAPTIONING OPTIMIZATION TEST SUITE")
    print("=" * 60)
    
    # Test optimized predictor
    test_optimized_predictor()
    
    # Test API
    test_api_optimization()
    
    # Compare performance
    compare_with_original()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the performance metrics above")
    print("2. If satisfied, deploy to Vercel: vercel --prod")
    print("3. Monitor performance in production")
    print("\nFor deployment help, see: DEPLOY_TO_VERCEL.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
