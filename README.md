# ImageToSketch

ImageToSketch is a local-first Flask application and lightweight deployable web service for turning a single uploaded image into a pencil-sketch style result. The repository now includes a browser UI, a simple API endpoint, reusable conversion utilities, and a command-line workflow for batch processing.

## Product scope

- **Primary use case:** convert a single JPG or PNG upload into a sketch from a browser.
- **Deployment model:** works as a local utility during development and can also be deployed as a small Flask-based web service.
- **Supported input formats:** `.jpg`, `.jpeg`, `.png`
- **Supported output formats:** `.jpg`, `.png`
- **Default upload size limit:** 10 MB per image
- **Output quality controls:** resize percentage, blur size, sharpen amount, grayscale contrast, grayscale brightness
- **Storage approach:** uploads and generated previews are processed in memory; no database is required.

## Features

- Validated uploads with friendly error handling
- Adjustable sketch settings
- Original image preview before conversion
- Generated sketch preview before download
- Mobile-friendly interface
- Downloadable JPG or PNG output
- API endpoint for programmatic use
- CLI support for one or many files

## Repository examples

The repository includes sample images you can use while testing locally:

- `./1.jpg`
- `./2.jpg`
- `./3.jpeg`

## Setup

1. Create and activate a virtual environment.
2. Install runtime dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. For tests and linting, install development dependencies:

   ```bash
   python -m pip install -r requirements-dev.txt
   ```

## Run the web app

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

### Environment variables

- `HOST` - bind host (default `127.0.0.1`)
- `PORT` - bind port (default `5000`)
- `FLASK_DEBUG` - set to `1` for debug mode
- `MAX_CONTENT_LENGTH_MB` - upload limit in MB (default `10`)
- `DEFAULT_SCALE_PERCENT`
- `DEFAULT_BLUR_SIZE`
- `DEFAULT_SHARPEN_AMOUNT`
- `DEFAULT_CONTRAST`
- `DEFAULT_BRIGHTNESS`
- `DEFAULT_OUTPUT_FORMAT`
- `SECRET_KEY`

## Web workflow

1. Upload a JPG or PNG image.
2. Tune resize, blur, sharpen, contrast, brightness, and output format.
3. Review the original preview and the generated sketch preview.
4. Download the result directly from the page.

## API usage

`POST /api/sketch`

- Content type: `multipart/form-data`
- Required file field: `image`
- Optional form fields:
  - `scale_percent`
  - `blur_size`
  - `sharpen_amount`
  - `contrast`
  - `brightness`
  - `output_format`

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/sketch \
  -F "image=@1.jpg" \
  -F "output_format=png" \
  -o sketch.png
```

## CLI usage

Convert one or more files into an output directory:

```bash
python cli.py 1.jpg 2.jpg --output-dir outputs --output-format png
```

Each converted file is written as `<original-name>-sketch.<ext>`.

## Tests and linting

Run the test suite:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

## Deployment notes

- The app is configured through environment variables so development and production settings stay separate.
- `MAX_CONTENT_LENGTH` protects the service from oversized uploads.
- In-memory processing keeps the app simple for demos and low-volume deployments.
- For production, run the Flask app behind a WSGI server and a reverse proxy.
- The `/health` endpoint can be used for lightweight health checks.

## Contributor guidance

- Keep conversion logic inside `utils.py` so the web app, API, and CLI reuse the same behavior.
- Add tests for both utility changes and Flask request flows when modifying features.
- Prefer configuration through environment variables rather than hard-coded deployment values.

## Roadmap

- Add asynchronous or queued processing for larger workloads
- Add saved conversion presets
- Add drag-and-drop uploads
- Add multi-file browser uploads with zip downloads
- Add authentication and persistent storage for hosted deployments
