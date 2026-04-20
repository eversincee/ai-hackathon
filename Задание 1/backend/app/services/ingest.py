import io
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

def split_pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> list[bytes]:
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    for page in doc:
        pixmap = page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pages.append(buf.getvalue())
    doc.close()
    return pages

def save_uploaded_file(data: bytes, storage_dir: Path, filename: str) -> Path:
    storage_dir = Path(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / filename
    target.write_bytes(data)
    return target
