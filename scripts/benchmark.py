"""
Quick benchmarking script for a single model.
Tests speed, memory, and generates sample outputs.
"""

import sys
import time
from pathlib import Path
import torch
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from inference.predictor import CaptionPredictor


def benchmark_model(model_path: str, vocab_path: str, test_image: str, device: str = 'cuda'):
    """Benchmark a single model."""
    
    print("\n" + "="*60)
    print("MODEL BENCHMARK")
    print("="*60)
    print(f"\nModel: {model_path}")
    print(f"Device: {device}")
    
    # Load model
    print("\nLoading model...")
    start = time.time()
    predictor = CaptionPredictor(model_path, vocab_path, device)
    load_time = time.time() - start
    print(f"✅ Model loaded in {load_time:.2f}s")
    
    # Load test image
    print(f"\nLoading test image: {test_image}")
    image = Image.open(test_image)
    print(f"Image size: {image.size}")
    
    # Warmup
    print("\nWarming up...")
    for _ in range(3):
        predictor.predict(image, method='greedy')
    
    # Benchmark greedy decoding
    print("\n" + "-"*60)
    print("GREEDY DECODING")
    print("-"*60)
    
    times_greedy = []
    for i in range(10):
        start = time.time()
        caption = predictor.predict(image, method='greedy')
        elapsed = (time.time() - start) * 1000
        times_greedy.append(elapsed)
        
        if i == 0:
            print(f"Caption: {caption}")
    
    print(f"\nSpeed:")
    print(f"  Mean: {np.mean(times_greedy):.1f} ms")
    print(f"  Std:  {np.std(times_greedy):.1f} ms")
    print(f"  Min:  {np.min(times_greedy):.1f} ms")
    print(f"  Max:  {np.max(times_greedy):.1f} ms")
    
    # Benchmark beam search
    print("\n" + "-"*60)
    print("BEAM SEARCH (width=5)")
    print("-"*60)
    
    times_beam = []
    for i in range(10):
        start = time.time()
        caption = predictor.predict(image, method='beam_search', beam_width=5)
        elapsed = (time.time() - start) * 1000
        times_beam.append(elapsed)
        
        if i == 0:
            print(f"Caption: {caption}")
    
    print(f"\nSpeed:")
    print(f"  Mean: {np.mean(times_beam):.1f} ms")
    print(f"  Std:  {np.std(times_beam):.1f} ms")
    print(f"  Min:  {np.min(times_beam):.1f} ms")
    print(f"  Max:  {np.max(times_beam):.1f} ms")
    
    # Memory usage
    if device == 'cuda' and torch.cuda.is_available():
        print("\n" + "-"*60)
        print("MEMORY USAGE")
        print("-"*60)
        
        torch.cuda.reset_peak_memory_stats()
        predictor.predict(image, method='beam_search')
        
        allocated = torch.cuda.max_memory_allocated() / 1024**2
        reserved = torch.cuda.max_memory_reserved() / 1024**2
        
        print(f"  Allocated: {allocated:.1f} MB")
        print(f"  Reserved:  {reserved:.1f} MB")
    
    # Generate multiple captions with different beam widths
    print("\n" + "-"*60)
    print("DIFFERENT BEAM WIDTHS")
    print("-"*60)
    
    for width in [1, 3, 5, 10]:
        caption = predictor.predict(image, method='beam_search', beam_width=width)
        print(f"\nBeam width {width}: {caption}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Greedy:      {np.mean(times_greedy):.1f} ms")
    print(f"Beam (w=5):  {np.mean(times_beam):.1f} ms")
    print(f"Speedup:     {np.mean(times_beam) / np.mean(times_greedy):.2f}x slower")
    
    if device == 'cuda':
        print(f"GPU Memory:  {allocated:.1f} MB")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark image captioning model')
    parser.add_argument('--model', type=str, required=True, help='Model checkpoint')
    parser.add_argument('--vocab', type=str, required=True, help='Vocabulary file')
    parser.add_argument('--image', type=str, required=True, help='Test image')
    parser.add_argument('--device', type=str, default='cuda', choices=['cuda', 'cpu'])
    
    args = parser.parse_args()
    
    benchmark_model(args.model, args.vocab, args.image, args.device)
