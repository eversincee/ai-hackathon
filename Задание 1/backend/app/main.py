from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db
from app.api import passports, assemblies, receipts, barcodes, lookup, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    Path(settings.scan_storage_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Passport Digitization API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passports.router)
app.include_router(assemblies.router)
app.include_router(receipts.router)
app.include_router(barcodes.router)
app.include_router(lookup.router)
app.include_router(export.router)

Path(settings.scan_storage_dir).mkdir(parents=True, exist_ok=True)
app.mount("/scans", StaticFiles(directory=settings.scan_storage_dir), name="scans")


@app.get("/health")
def health():
    return {"status": "ok"}
