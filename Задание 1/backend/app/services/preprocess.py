import io
from PIL import Image


def auto_rotate_image(image_bytes: bytes) -> bytes:
    """Basic auto-rotate. Without tesseract, just returns the image as-is.
    When tesseract is available, use OSD for orientation detection."""
    # For now, pass-through. VLM handles rotated text well enough.
    return image_bytes
