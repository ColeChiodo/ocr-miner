import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import CAPTURES_DIR
from app.routers import health, captures

app = FastAPI(title="OCR Miner")

os.makedirs(CAPTURES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")
app.mount("/captures-files", StaticFiles(directory=CAPTURES_DIR), name="captures")

app.include_router(health.router)
app.include_router(captures.router)
