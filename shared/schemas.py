from pydantic import BaseModel
from typing import List, Optional

class OCRWord(BaseModel):
    text: str
    bbox: List[List[float]]
    confidence: float

class OCRResult(BaseModel):
    words: List[OCRWord]
    error: Optional[str] = None

class CaptureStatus(BaseModel):
    id: str
    ready: bool
    word_count: int = 0
