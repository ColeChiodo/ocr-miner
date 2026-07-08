from fastapi import FastAPI, UploadFile, File
from PIL import Image
import numpy as np
from io import BytesIO

from app.processor import reader
from app.preprocess import preprocess

app = FastAPI(title="OCR Service")


@app.post("/ocr")
async def ocr(image: UploadFile = File(...)):
    contents = await image.read()
    img = Image.open(BytesIO(contents))
    img_np = np.array(img)

    processed, offset_x, offset_y = preprocess(img_np)

    results = reader.readtext(processed)

    words = []
    for bbox, text, confidence in results:
        words.append({
            "text": text,
            "bbox": [[float(x + offset_x) / 2.0, float(y + offset_y) / 2.0] for x, y in bbox],
            "confidence": float(confidence),
        })

    return {"words": words}
