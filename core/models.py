from pydantic import BaseModel
from typing import Literal

class FlashCard(BaseModel):
    question: str
    answer: str

class DeadlineInfo(BaseModel):
    title: str
    datetime_iso: str
    confidence: float

class ReceiptItem(BaseModel):
    name: str
    amount: float

class ReceiptInfo(BaseModel):
    total: float
    currency: str
    items: list[ReceiptItem]
    suggested_split: dict[str, float]
    estimated_total: bool = False

class OcrResponse(BaseModel):
    request_id: str
    raw_text: str
    confidence: float
    language: str
    intent: Literal["note", "receipt", "deadline_note", "blank"]
    summary: str | None = None
    flashcards: list[FlashCard] | None = None
    deadline: DeadlineInfo | None = None
    receipt: ReceiptInfo | None = None
    processing_time_ms: int
    warning: str | None = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str
    fallback_available: bool
    fallback_data: dict | None = None

class SearchResult(BaseModel):
    id: str
    text: str
    distance: float
    metadata: dict
