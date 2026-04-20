from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db

init_db()

client = TestClient(app)


def test_create_assembly():
    response = client.post("/assemblies", json={
        "name": "Шкаф САУ ГПА",
        "kind": "шкаф",
        "items": [
            {"position": 1, "document_name": "МФК 1500 DO32P", "factory_number": "042401184530", "has_certificate": True},
        ],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Шкаф САУ ГПА"
    assert body["barcode_payload"].startswith("asm-")


def test_list_assemblies():
    response = client.get("/assemblies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
