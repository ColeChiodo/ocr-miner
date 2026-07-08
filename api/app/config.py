import os

OCR_URL = os.getenv("OCR_URL", "http://ocr:5000")
DATA_DIR = os.getenv("DATA_DIR", "/data")
CAPTURES_DIR = os.path.join(DATA_DIR, "captures")
