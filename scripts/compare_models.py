"""
Model Performance Comparison Script
Compares multiple models on metrics, speed, and memory usage.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import List, Dict
import torch
from PIL import Image
import numpy as np
from tabulate import tabulate

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from inference.predictor import CaptionPredictor
from training.vocabulary import Vocabulary
from training.metrics import CaptionMetrics


class ModelComparator:
    """Compare multiple image captioning models."""
    
    def __init__(self, device: str = 'cuda'):
        self.device = device
        self.results = []
    
    def load_model(self, model_path: str, vocab_path: str, name: str) -> CaptionPredictor:
        """Load a model for comparison."""
        print(f"\nLoading {name}...")
        predictor = CaptionPredictor(
            model_path=model_path,
            vocab_path=vocab_path,
            device=self.device
        )
        print(f"✅ Loaded {name}")
        return predictor
    
    def measure_inference_speed(
        self, 
        predictor: CaptionPredictor, 
        image: Image.Image,
        num_runs: int = 10,
        method: str = 'beam_search'
    ) -> Dict:
        """Measure inference speed."""
        times = []
        
        # Warmup
        for _ in range(3):
            predictor.predict(image, method=method)
        
        # Measure
        for _ in range(num_runs):
            start = time.time()
            caption = predictor.predict(image, method=method)
            elapsed = (time.time() - start) * 1000  # ms
            times.append(elapsed)
        
        return {
            'mean': np.mean(times),
            'std': np.std(times),
            'min': np.min(times),
            'max': np.max(times)
        }
    
    def measure_memory(self, predictor: CaptionPredictor) -> Dict:
        """Measure GPU memory usage."""
        if self.device == 'cuda' and torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.empty_cache()
            
            # Dummy forward pass
            dummy_image = Image.new('RGB', (224, 224))
            predictor.predict(dummy_image)
            
            allocated = torch.cuda.max_memory_allocated() / 1024**2  # MB
            reserved = torch.cuda.max_memory_reserved() / 1024**2  # MB
            
            return {
                'allocated_mb': allocated,
                'reserved_mb': reserved
            }
        else:
            return {'allocated_mb': 0, 'reserved_mb': 0}
    
    def evaluate_on_images(
        self,
        predictor: CaptionPredictor,
        image_paths: List[str],
        reference_captions: List[List[str]],
        method: str = 'beam_search'
    ) -> Dict:
        """Evaluate model on a set of images."""
        predictions = []
        
        print(f"Generating captions for {len(image_paths)} images...")
        for img_path in image_paths:
            try:
                caption = predictor.predict(img_path, method=method)
                predictions.append(caption)
            except Exception as e:
                print(f"Error on {img_path}: {e}")
                predictions.append("")
        
        # Compute metrics
        if reference_captions:
            evaluator = CaptionMetrics()
            evaluator.update(predictions, reference_captions)
            metrics = evaluator.compute_all()
        else:
            metrics = {}
        
        return {
            'predictions': predictions,
            'metrics': metrics
        }
    
    def compare_models(
        self,
        models: List[Dict],
        test_images: List[str],
        reference_captions: List[List[str]] = None,
        num_speed_runs: int = 10
    ):
        """Compare multiple models."""
        print("\n" + "="*60)
        print("MODEL COMPARISON")
        print("="*60)
        
        results = []
        
        for model_info in models:
            name = model_info['name']
            model_path = model_info['model_path']
            vocab_path = model_info['vocab_path']
            
            print(f"\n{'='*60}")
            print(f"Evaluating: {name}")
            print('='*60)
            
            # Load model
            predictor = self.load_model(model_path, vocab_path, name)
            
            # Measure speed
            print("\nMeasuring inference speed...")
            test_image = Image.open(test_images[0])
            speed_greedy = self.measure_inference_speed(
                predictor, test_image, num_speed_runs, method='greedy'
            )
            speed_beam = self.measure_inference_speed(
                predictor, test_image, num_speed_runs, method='beam_search'
            )
            
            # Measure memory
            print("Measuring memory usage...")
            memory = self.measure_memory(predictor)
            
            # Evaluate on test set
            print("Evaluating on test images...")
            eval_results = self.evaluate_on_images(
                predictor, test_images, reference_captions, method='beam_search'
            )
            
            # Get model size
            model_size = os.path.getsize(model_path) / 1024**2  # MB
            
            # Store results
            result = {
                'name': name,
                'model_size_mb': model_size,
                'speed_greedy_ms': speed_greedy['mean'],
                'speed_beam_ms': speed_beam['mean'],
                'memory_allocated_mb': memory['allocated_mb'],
                'memory_reserved_mb': memory['reserved_mb'],
                'predictions': eval_results['predictions'],
                **eval_results['metrics']
            }
            
            results.append(result)
        
        return results
    
    def print_comparison_table(self, results: List[Dict]):
        """Print comparison table."""
        print("\n" + "="*80)
        print("COMPARISON RESULTS")
        print("="*80)
        
        # Speed comparison
        print("\n📊 INFERENCE SPEED (milliseconds)")
        print("-" * 80)
        speed_table = []
        for r in results:
            speed_table.append([
                r['name'],
                f"{r['speed_greedy_ms']:.1f}",
                f"{r['speed_beam_ms']:.1f}",
                f"{r['model_size_mb']:.1f}"
            ])
        
        print(tabulate(
            speed_table,
            headers=['Model', 'Greedy (ms)', 'Beam Search (ms)', 'Size (MB)'],
            tablefmt='grid'
        ))
        
        # Memory comparison
        if any(r['memory_allocated_mb'] > 0 for r in results):
            print("\n💾 MEMORY USAGE (MB)")
            print("-" * 80)
            mem_table = []
            for r in results:
                mem_table.append([
                    r['name'],
                    f"{r['memory_allocated_mb']:.1f}",
                    f"{r['memory_reserved_mb']:.1f}"
                ])
            
            print(tabulate(
                mem_table,
                headers=['Model', 'Allocated (MB)', 'Reserved (MB)'],
                tablefmt='grid'
            ))
        
        # Metrics comparison
        if any('BLEU-4' in r for r in results):
            print("\n🎯 EVALUATION METRICS")
            print("-" * 80)
            metrics_table = []
            for r in results:
                metrics_table.append([
                    r['name'],
                    f"{r.get('BLEU-1', 0):.4f}",
                    f"{r.get('BLEU-4', 0):.4f}",
                    f"{r.get('METEOR', 0):.4f}",
                    f"{r.get('ROUGE-L', 0):.4f}"
                ])
            
            print(tabulate(
                metrics_table,
                headers=['Model', 'BLEU-1', 'BLEU-4', 'METEOR', 'ROUGE-L'],
                tablefmt='grid'
            ))
        
        # Winner summary
        print("\n🏆 SUMMARY")
        print("-" * 80)
        
        fastest_greedy = min(results, key=lambda x: x['speed_greedy_ms'])
        fastest_beam = min(results, key=lambda x: x['speed_beam_ms'])
        smallest = min(results, key=lambda x: x['model_size_mb'])
        
        print(f"Fastest (Greedy):      {fastest_greedy['name']} ({fastest_greedy['speed_greedy_ms']:.1f}ms)")
        print(f"Fastest (Beam Search): {fastest_beam['name']} ({fastest_beam['speed_beam_ms']:.1f}ms)")
        print(f"Smallest Model:        {smallest['name']} ({smallest['model_size_mb']:.1f}MB)")
        
        if any('BLEU-4' in r for r in results):
            best_bleu = max(results, key=lambda x: x.get('BLEU-4', 0))
            print(f"Best BLEU-4:           {best_bleu['name']} ({best_bleu.get('BLEU-4', 0):.4f})")
    
    def save_results(self, results: List[Dict], output_path: str):
        """Save results to JSON."""
        # Remove predictions for cleaner output
        clean_results = []
        for r in results.copy():
            clean_r = r.copy()
            if 'predictions' in clean_r:
                del clean_r['predictions']
            clean_results.append(clean_r)
        
        with open(output_path, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Compare Image Captioning Models')
    
    parser.add_argument('--models', type=str, nargs='+', required=True,
                       help='Model checkpoint paths')
    parser.add_argument('--vocabs', type=str, nargs='+', required=True,
                       help='Vocabulary paths (same order as models)')
    parser.add_argument('--names', type=str, nargs='+', required=True,
                       help='Model names (same order as models)')
    parser.add_argument('--test_images', type=str, nargs='+', required=True,
                       help='Test image paths')
    parser.add_argument('--references', type=str, default=None,
                       help='JSON file with reference captions')
    parser.add_argument('--device', type=str, default='cuda', choices=['cuda', 'cpu'])
    parser.add_argument('--num_runs', type=int, default=10,
                       help='Number of runs for speed measurement')
    parser.add_argument('--output', type=str, default='comparison_results.json',
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    # Validate inputs
    if len(args.models) != len(args.vocabs) or len(args.models) != len(args.names):
        print("❌ Error: Number of models, vocabs, and names must match")
        return
    
    # Prepare models list
    models = []
    for name, model_path, vocab_path in zip(args.names, args.models, args.vocabs):
        models.append({
            'name': name,
            'model_path': model_path,
            'vocab_path': vocab_path
        })
    
    # Load reference captions if provided
    reference_captions = None
    if args.references:
        with open(args.references, 'r') as f:
            ref_data = json.load(f)
            reference_captions = ref_data.get('captions', None)
    
    # Run comparison
    comparator = ModelComparator(device=args.device)
    results = comparator.compare_models(
        models=models,
        test_images=args.test_images,
        reference_captions=reference_captions,
        num_speed_runs=args.num_runs
    )
    
    # Print and save results
    comparator.print_comparison_table(results)
    comparator.save_results(results, args.output)


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) == 1:
        print("\nExample usage:")
        print("-" * 60)
        print("python scripts/compare_models.py \\")
        print("  --models checkpoints/coco/best_model.pth checkpoints/flickr8k/best_model.pth \\")
        print("  --vocabs checkpoints/coco/vocab.json checkpoints/flickr8k/vocab.json \\")
        print("  --names 'COCO-Transformer' 'Flickr8k-Transformer' \\")
        print("  --test_images data/test/*.jpg \\")
        print("  --device cuda \\")
        print("  --num_runs 20 \\")
        print("  --output comparison_results.json")
        print("-" * 60)
    else:
        main()
