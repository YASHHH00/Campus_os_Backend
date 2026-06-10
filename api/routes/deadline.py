from fastapi import APIRouter, Request
from pydantic import BaseModel
import uuid
from core.models import DeadlineInfo
from core.logging import get_logger
from services.llm import deadline_extractor

logger = get_logger(__name__)
router = APIRouter()

class ExtractDeadlineRequest(BaseModel):
    text: str

class ExtractDeadlineResponse(BaseModel):
    events: list[DeadlineInfo]
    request_id: str

@router.post("/extract_deadline", response_model=ExtractDeadlineResponse)
async def extract_deadline(payload: ExtractDeadlineRequest, request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    deadlines = await deadline_extractor.extract(payload.text)
    
    return ExtractDeadlineResponse(
        events=deadlines,
        request_id=request_id
    )
