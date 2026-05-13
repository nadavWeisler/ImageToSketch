from io import BytesIO

import cv2
import numpy as np

from app import app


def build_sample_upload(filename: str = "sample.jpg") -> tuple[BytesIO, str]:
    image = np.zeros((96, 96, 3), dtype=np.uint8)
    image[:, :] = (20, 90, 200)
    cv2.rectangle(image, (16, 16), (80, 80), (255, 255, 255), -1)
    extension = ".png" if filename.endswith(".png") else ".jpg"
    success, encoded_image = cv2.imencode(extension, image)
    assert success
    return BytesIO(encoded_image.tobytes()), filename


def test_home_page_renders():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"ImageToSketch" in response.data


def test_home_page_rejects_missing_upload():
    client = app.test_client()
    response = client.post("/", data={}, content_type="multipart/form-data")

    assert response.status_code == 200
    assert b"Choose an image to convert." in response.data


def test_home_page_converts_image_and_shows_download():
    client = app.test_client()
    response = client.post(
        "/",
        data={
            "image": build_sample_upload(),
            "scale_percent": "60",
            "blur_size": "15",
            "sharpen_amount": "1.0",
            "contrast": "1.0",
            "brightness": "0",
            "output_format": "png",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Download sample-sketch.png" in response.data


def test_api_sketch_returns_file_download():
    client = app.test_client()
    response = client.post(
        "/api/sketch",
        data={
            "image": build_sample_upload("sample.png"),
            "output_format": "png",
            "scale_percent": "60",
            "blur_size": "15",
            "sharpen_amount": "1.0",
            "contrast": "1.0",
            "brightness": "0",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert "sample-sketch.png" in response.headers["Content-Disposition"]
