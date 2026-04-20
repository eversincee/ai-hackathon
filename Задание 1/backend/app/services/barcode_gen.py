import io
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import A7
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_code128_png(payload: str) -> bytes:
    buf = io.BytesIO()
    Code128(payload, writer=ImageWriter()).write(buf, options={"write_text": False})
    return buf.getvalue()

def generate_label_pdf(barcode_payload: str, title: str, subtitle: str = "") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A7)
    width, height = A7
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5, height - 15, title[:40])
    if subtitle:
        c.setFont("Helvetica", 7)
        c.drawString(5, height - 27, subtitle[:50])

    barcode_png = generate_code128_png(barcode_payload)
    img = ImageReader(io.BytesIO(barcode_png))
    c.drawImage(img, 5, 20, width=width - 10, height=height - 60, preserveAspectRatio=True)

    c.setFont("Helvetica", 6)
    c.drawCentredString(width / 2, 10, barcode_payload)

    c.save()
    return buf.getvalue()
