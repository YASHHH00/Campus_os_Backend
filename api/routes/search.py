from fastapi import APIRouter, Request
from pydantic import BaseModel
import uuid
from core.models import SearchResult
from core.logging import get_logger
from services.vector.chroma_service import chroma_service

logger = get_logger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: list[SearchResult]
    request_id: str

@router.post("/search_notes", response_model=SearchResponse)
async def search_notes(payload: SearchRequest, request: Request):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    results = await chroma_service.search(query=payload.query, top_k=payload.top_k)
    
    return SearchResponse(
        results=results,
        request_id=request_id
    )
