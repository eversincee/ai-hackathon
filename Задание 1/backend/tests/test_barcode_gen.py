from app.services.barcode_gen import generate_code128_png, generate_label_pdf

def test_generate_code128_png_returns_bytes():
    png = generate_code128_png("paspt-abc123")
    assert isinstance(png, bytes)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"

def test_generate_label_pdf_returns_bytes():
    pdf = generate_label_pdf(
        barcode_payload="paspt-abc123",
        title="\u0422\u0420\u042d\u0418 \u041c1201\u0415",
        subtitle="\u0417\u0430\u0432\u043e\u0434\u0441\u043a\u043e\u0439 \u043d\u043e\u043c\u0435\u0440: G4M0821",
    )
    assert isinstance(pdf, bytes)
    assert pdf[:4] == b"%PDF"
