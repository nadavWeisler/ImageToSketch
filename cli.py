from __future__ import annotations

import argparse
from pathlib import Path

from utils import SketchOptions, convert_pic_to_sketch, normalize_output_format


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert one or more images into sketch-style outputs.")
    parser.add_argument("inputs", nargs="+", help="One or more input image files.")
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for converted files when processing one or more inputs.",
    )
    parser.add_argument("--scale-percent", type=int, default=60, help="Resize percentage between 10 and 100.")
    parser.add_argument("--blur-size", type=int, default=15, help="Gaussian blur size between 1 and 51.")
    parser.add_argument("--sharpen-amount", type=float, default=1.0, help="Sharpen amount between 0 and 5.")
    parser.add_argument("--contrast", type=float, default=1.0, help="Grayscale contrast between 0.5 and 3.")
    parser.add_argument("--brightness", type=int, default=0, help="Grayscale brightness between -100 and 100.")
    parser.add_argument("--output-format", default="jpg", help="Output format: jpg or png.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    options = SketchOptions(
        scale_percent=args.scale_percent,
        blur_size=args.blur_size,
        sharpen_amount=args.sharpen_amount,
        contrast=args.contrast,
        brightness=args.brightness,
        output_format=normalize_output_format(args.output_format),
    )

    for raw_input in args.inputs:
        source_path = Path(raw_input)
        target_path = output_dir / f"{source_path.stem}-sketch.{options.output_format}"
        convert_pic_to_sketch(source_path, target_path, options)
        print(target_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
