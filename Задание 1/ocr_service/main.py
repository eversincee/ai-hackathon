# Surya OCR Service — compatible with surya-ocr >= 0.17
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Surya OCR Service")

# Lazy-load models on first request to avoid import-time overhead
_predictors = {}

LANGUAGES = ["ru", "en"]


def _get_predictors():
    if not _predictors:
        from surya.foundation import FoundationPredictor
        from surya.recognition import RecognitionPredictor
        from surya.detection import DetectionPredictor

        logger.info("Loading Surya models (first request)...")
        foundation = FoundationPredictor()
        _predictors["recognition"] = RecognitionPredictor(foundation)
        _predictors["detection"] = DetectionPredictor()
        logger.info("Surya models loaded.")
    return _predictors


def _polygon_to_bbox(polygon):
    """Convert polygon [[x1,y1],[x2,y2],...] to [x_min, y_min, x_max, y_max]."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


@app.get("/health")
def health():
    return {"status": "ok", "languages": LANGUAGES}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    p = _get_predictors()
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    predictions = p["recognition"](
        [image],
        det_predictor=p["detection"],
    )

    result = predictions[0]  # OCRResult for the single image
    return {
        "text_lines": [
            {
                "text": line.text,
                "bbox": _polygon_to_bbox(line.polygon) if line.polygon else [0, 0, 0, 0],
                "confidence": getattr(line, "confidence", 0.0),
            }
            for line in result.text_lines
        ],
    }
