"""
Standalone inference script for testing.
"""

import argparse
from predictor import CaptionPredictor


def main():
    parser = argparse.ArgumentParser(description='Generate image captions')
    parser.add_argument('--image', type=str, required=True, help='Path to image')
    parser.add_argument('--model', type=str, required=True, help='Path to model checkpoint')
    parser.add_argument('--vocab', type=str, required=True, help='Path to vocabulary')
    parser.add_argument('--method', type=str, default='beam_search', choices=['greedy', 'beam_search'])
    parser.add_argument('--beam_width', type=int, default=5)
    parser.add_argument('--max_length', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda')
    parser.add_argument('--export_torchscript', type=str, default=None, help='Export to TorchScript')
    parser.add_argument('--export_onnx', type=str, default=None, help='Export to ONNX')
    
    args = parser.parse_args()
    
    # Create predictor
    predictor = CaptionPredictor(
        model_path=args.model,
        vocab_path=args.vocab,
        device=args.device
    )
    
    # Generate caption
    print(f"Generating caption for: {args.image}")
    caption = predictor.predict(
        args.image,
        method=args.method,
        beam_width=args.beam_width,
        max_length=args.max_length
    )
    
    print(f"\nGenerated Caption: {caption}")
    
    # Export if requested
    if args.export_torchscript:
        predictor.export_torchscript(args.export_torchscript)
    
    if args.export_onnx:
        predictor.export_onnx(args.export_onnx)


if __name__ == '__main__':
    main()
