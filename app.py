from __future__ import annotations

from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

import __data__ as data
from config import Config
from utils import (
    SketchOptions,
    build_data_uri,
    convert_image_bytes_to_sketch,
    is_supported_extension,
    normalize_output_format,
)


app = Flask(data.__app_name__)
app.config.from_object(Config)
app.config.update(prog=f"{data.__name__} v{data.__version__}", author=data.__author__)


def _default_form_values() -> dict[str, str]:
    return {
        "scale_percent": str(app.config["DEFAULT_SCALE_PERCENT"]),
        "blur_size": str(app.config["DEFAULT_BLUR_SIZE"]),
        "sharpen_amount": str(app.config["DEFAULT_SHARPEN_AMOUNT"]),
        "contrast": str(app.config["DEFAULT_CONTRAST"]),
        "brightness": str(app.config["DEFAULT_BRIGHTNESS"]),
        "output_format": app.config["DEFAULT_OUTPUT_FORMAT"],
    }


def _render_home(**context: object) -> str:
    base_context = {
        "title": data.__name__,
        "scope_label": app.config["PRODUCT_SCOPE"],
        "supported_formats": ", ".join(sorted(app.config["ALLOWED_EXTENSIONS"])),
        "max_upload_mb": app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024),
        "form_values": _default_form_values(),
        "error_message": None,
        "original_preview": None,
        "sketch_preview": None,
        "download_name": None,
        "conversion_ready": False,
    }
    base_context.update(context)
    return render_template("home.html", **base_context)


def _coerce_int(raw_value: str, field_name: str, minimum: int, maximum: int) -> int:
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")
    return value


def _coerce_float(raw_value: str, field_name: str, minimum: float, maximum: float) -> float:
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")
    return value


def _parse_sketch_options(form_data: dict[str, str]) -> SketchOptions:
    output_format = normalize_output_format(form_data.get("output_format", "jpg"))
    return SketchOptions(
        scale_percent=_coerce_int(form_data.get("scale_percent", ""), "Resize percentage", 10, 100),
        blur_size=_coerce_int(form_data.get("blur_size", ""), "Blur size", 1, 51),
        sharpen_amount=_coerce_float(
            form_data.get("sharpen_amount", ""), "Sharpen amount", 0.0, 5.0
        ),
        contrast=_coerce_float(form_data.get("contrast", ""), "Grayscale contrast", 0.5, 3.0),
        brightness=_coerce_int(form_data.get("brightness", ""), "Grayscale brightness", -100, 100),
        output_format=output_format,
    )


def _read_upload() -> tuple[bytes, str]:
    image_file = request.files.get("image")
    if image_file is None:
        raise ValueError("Choose an image to convert.")

    original_name = secure_filename(image_file.filename or "")
    if not original_name:
        raise ValueError("Choose an image to convert.")
    if not is_supported_extension(original_name, app.config["ALLOWED_EXTENSIONS"]):
        raise ValueError(
            f"Unsupported file type. Use one of: {', '.join(sorted(app.config['ALLOWED_EXTENSIONS']))}."
        )

    image_bytes = image_file.read()
    if not image_bytes:
        raise ValueError("The uploaded image is empty.")
    return image_bytes, original_name


def _guess_input_mimetype(filename: str) -> str:
    return "image/png" if Path(filename).suffix.lower() == ".png" else "image/jpeg"


def _build_download_name(filename: str, output_format: str) -> str:
    safe_name = Path(filename).stem or "sketch"
    extension = "png" if output_format == "png" else "jpg"
    return f"{safe_name}-sketch.{extension}"


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "GET":
        return _render_home()

    form_values = {key: request.form.get(key, value) for key, value in _default_form_values().items()}

    try:
        image_bytes, original_name = _read_upload()
        options = _parse_sketch_options(request.form)
        sketch_bytes, mimetype, output_format = convert_image_bytes_to_sketch(image_bytes, options)
    except ValueError as exc:
        return _render_home(form_values=form_values, error_message=str(exc))

    return _render_home(
        form_values=form_values,
        original_preview=build_data_uri(image_bytes, _guess_input_mimetype(original_name)),
        sketch_preview=build_data_uri(sketch_bytes, mimetype),
        download_name=_build_download_name(original_name, output_format),
        conversion_ready=True,
    )


@app.post("/api/sketch")
def api_sketch():
    try:
        image_bytes, original_name = _read_upload()
        options = _parse_sketch_options(request.form)
        sketch_bytes, mimetype, output_format = convert_image_bytes_to_sketch(image_bytes, options)
    except ValueError:
        return jsonify({"error": "Invalid request. Check the file type and sketch settings."}), 400
    return send_file(
        BytesIO(sketch_bytes),
        mimetype=mimetype,
        as_attachment=True,
        download_name=_build_download_name(original_name, output_format),
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "app": data.__app_name__,
            "scope": app.config["PRODUCT_SCOPE"],
            "storage": app.config["OUTPUT_STORAGE"],
        }
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(error: RequestEntityTooLarge):
    message = (
        f"Upload too large. The maximum file size is {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)} MB."
    )
    if request.path.startswith("/api/"):
        return jsonify({"error": message}), 413
    return _render_home(error_message=message), 413


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )
