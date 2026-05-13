from pathlib import Path

import cv2
import numpy as np

from utils import SketchOptions, build_data_uri, convert_image_bytes_to_sketch, convert_pic_to_sketch


def build_sample_image_bytes(extension: str = ".jpg") -> bytes:
    image = np.zeros((120, 120, 3), dtype=np.uint8)
    image[:, :] = (30, 120, 220)
    cv2.circle(image, (60, 60), 24, (255, 255, 255), -1)
    success, encoded_image = cv2.imencode(extension, image)
    assert success
    return encoded_image.tobytes()


def test_convert_image_bytes_to_png_sketch():
    sketch_bytes, mimetype, output_format = convert_image_bytes_to_sketch(
        build_sample_image_bytes(),
        SketchOptions(output_format="png", blur_size=11, scale_percent=70),
    )

    assert sketch_bytes
    assert mimetype == "image/png"
    assert output_format == "png"


def test_convert_pic_to_sketch_writes_file(tmp_path: Path):
    source = tmp_path / "input.jpg"
    source.write_bytes(build_sample_image_bytes())

    target = convert_pic_to_sketch(source, tmp_path / "output.png", SketchOptions(output_format="png"))

    assert target.exists()
    assert target.suffix == ".png"


def test_build_data_uri():
    data_uri = build_data_uri(b"abc", "image/png")
    assert data_uri.startswith("data:image/png;base64,")
