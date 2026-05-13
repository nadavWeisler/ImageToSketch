from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


SUPPORTED_INPUT_EXTENSIONS = {"jpg", "jpeg", "png"}
SUPPORTED_OUTPUT_FORMATS = {
    "jpg": {"extension": ".jpg", "encode_extension": ".jpg", "mimetype": "image/jpeg"},
    "png": {"extension": ".png", "encode_extension": ".png", "mimetype": "image/png"},
}


class ValidationError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass(frozen=True, slots=True)
class SketchOptions:
    scale_percent: int = 60
    blur_size: int = 15
    sharpen_amount: float = 1.0
    contrast: float = 1.0
    brightness: int = 0
    output_format: str = "jpg"


def dodge_v2(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return cv2.divide(image, 255 - mask, scale=256)


def normalize_output_format(output_format: str) -> str:
    normalized = (output_format or "jpg").strip().lower()
    if normalized not in SUPPORTED_OUTPUT_FORMATS:
        raise ValidationError("Output format must be jpg or png.")
    return normalized


def normalize_blur_size(blur_size: int) -> int:
    if blur_size < 1:
        raise ValidationError("Blur size must be at least 1.")
    return blur_size if blur_size % 2 == 1 else blur_size + 1


def is_supported_extension(filename: str, allowed_extensions: set[str] | tuple[str, ...]) -> bool:
    extension = Path(filename).suffix.lower().lstrip(".")
    return extension in {value.lower() for value in allowed_extensions}


def _decode_image(image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise ValidationError("The uploaded image is empty.")
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    decoded_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if decoded_image is None:
        raise ValidationError("The uploaded file is not a valid image.")
    return decoded_image


def _sharpen_kernel(amount: float) -> np.ndarray:
    # Keep the kernel sum at 1 so sharpening boosts edges without shifting overall brightness.
    return np.array(
        [[0.0, -amount, 0.0], [-amount, 1.0 + (4.0 * amount), -amount], [0.0, -amount, 0.0]],
        dtype=np.float32,
    )


def _scaled_dimension(original_size: int, scale_percent: int) -> int:
    return max(1, int(original_size * scale_percent / 100))


def create_sketch(image: np.ndarray, options: SketchOptions) -> np.ndarray:
    if image is None or image.size == 0:
        raise ValidationError("Image data is missing.")

    scale_percent = max(10, min(100, int(options.scale_percent)))
    width = _scaled_dimension(image.shape[1], scale_percent)
    height = _scaled_dimension(image.shape[0], scale_percent)
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    if options.sharpen_amount > 0:
        resized = cv2.filter2D(resized, -1, _sharpen_kernel(float(options.sharpen_amount)))

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=float(options.contrast), beta=int(options.brightness))
    inverted = 255 - gray
    blur_size = normalize_blur_size(int(options.blur_size))
    blurred = cv2.GaussianBlur(inverted, ksize=(blur_size, blur_size), sigmaX=0, sigmaY=0)
    return dodge_v2(gray, blurred)


def encode_image(image: np.ndarray, output_format: str) -> tuple[bytes, str]:
    normalized_output_format = normalize_output_format(output_format)
    format_details = SUPPORTED_OUTPUT_FORMATS[normalized_output_format]
    success, encoded_image = cv2.imencode(format_details["encode_extension"], image)
    if not success:
        raise ValidationError("Unable to encode the converted sketch.")
    return encoded_image.tobytes(), format_details["mimetype"]


def convert_image_bytes_to_sketch(
    image_bytes: bytes, options: SketchOptions | None = None
) -> tuple[bytes, str, str]:
    sketch_options = options or SketchOptions()
    decoded_image = _decode_image(image_bytes)
    sketch = create_sketch(decoded_image, sketch_options)
    encoded_image, mimetype = encode_image(sketch, sketch_options.output_format)
    return encoded_image, mimetype, normalize_output_format(sketch_options.output_format)


def build_data_uri(image_bytes: bytes, mimetype: str) -> str:
    return f"data:{mimetype};base64,{b64encode(image_bytes).decode('ascii')}"


def pic_to_sketch(file_path: str | Path, options: SketchOptions | None = None) -> np.ndarray:
    source_path = Path(file_path)
    image = cv2.imread(str(source_path))
    if image is None:
        raise ValidationError(f"Unable to read image: {source_path}")
    return create_sketch(image, options or SketchOptions())


def convert_pic_to_sketch(
    file_path: str | Path,
    output_path: str | Path | None = None,
    options: SketchOptions | None = None,
) -> Path:
    sketch_options = options or SketchOptions()
    source_path = Path(file_path)
    normalized_output_format = normalize_output_format(sketch_options.output_format)
    output_extension = SUPPORTED_OUTPUT_FORMATS[normalized_output_format]["extension"]
    target_path = (
        Path(output_path)
        if output_path
        else source_path.with_name(f"{source_path.stem}-sketch{output_extension}")
    )
    sketch = pic_to_sketch(source_path, sketch_options)
    encoded_image, _ = encode_image(sketch, sketch_options.output_format)
    target_path.write_bytes(encoded_image)
    return target_path


if __name__ == "__main__":
    source_name = input("Enter file name: ").strip()
    output_file = convert_pic_to_sketch(source_name)
    print(output_file)
