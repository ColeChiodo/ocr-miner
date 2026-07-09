import os
import easyocr

OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "ja").split(",")

reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)
