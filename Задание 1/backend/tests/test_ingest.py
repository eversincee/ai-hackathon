from pathlib import Path
from app.services.ingest import split_pdf_to_images, save_uploaded_file

FIXTURE = Path(__file__).parent / "fixtures" / "sample_2pages.pdf"

def test_split_pdf_to_images_returns_pages():
    pages = split_pdf_to_images(FIXTURE.read_bytes(), dpi=150)
    assert len(pages) >= 1
    assert all(isinstance(p, bytes) for p in pages)
    assert all(len(p) > 1000 for p in pages)
    # Verify PNG magic bytes
    assert all(p[:8] == b"\x89PNG\r\n\x1a\n" for p in pages)

def test_save_uploaded_file(tmp_path):
    target = save_uploaded_file(b"hello world", tmp_path, "test.pdf")
    assert target.exists()
    assert target.read_bytes() == b"hello world"
