import io
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db

init_db()

client = TestClient(app)

CSV = """receipt_doc_number,receipt_date,position_code,nomenclature,type_brand,nomenclature_code_su,unit,price,qty_declared,qty_actual
K00006964,2026-01-29,5421289,УЗИП СПС-Д-2-110,Y0000944,ПП000826177,шт,4366.15,200,200"""


def test_import_receipts_csv():
    files = {"file": ("receipts.csv", io.BytesIO(CSV.encode("utf-8")), "text/csv")}
    response = client.post("/receipts/import", files=files)
    assert response.status_code == 200
    assert response.json()["imported"] == 1


def test_list_receipts():
    response = client.get("/receipts")
    assert response.status_code == 200
