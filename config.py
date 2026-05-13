from __future__ import annotations

import os


def _get_int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _get_float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    PRODUCT_SCOPE = (
        "A local-first Flask app and lightweight deployable web service for turning single uploads "
        "into pencil-sketch style images."
    )
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    MAX_CONTENT_LENGTH = _get_int_env("MAX_CONTENT_LENGTH_MB", 10) * 1024 * 1024
    DEFAULT_SCALE_PERCENT = _get_int_env("DEFAULT_SCALE_PERCENT", 60)
    DEFAULT_BLUR_SIZE = _get_int_env("DEFAULT_BLUR_SIZE", 15)
    DEFAULT_SHARPEN_AMOUNT = _get_float_env("DEFAULT_SHARPEN_AMOUNT", 1.0)
    DEFAULT_CONTRAST = _get_float_env("DEFAULT_CONTRAST", 1.0)
    DEFAULT_BRIGHTNESS = _get_int_env("DEFAULT_BRIGHTNESS", 0)
    DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "jpg").lower()
    OUTPUT_STORAGE = "in-memory previews and downloads"
    SECRET_KEY = os.getenv("SECRET_KEY", "image-to-sketch-dev-key")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = _get_int_env("PORT", 5000)
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
