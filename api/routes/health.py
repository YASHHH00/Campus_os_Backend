from fastapi import APIRouter
from pydantic import BaseModel
from services.llm.llm_client import llm_client

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    openrouter: str
    chromadb: str
    webrtc: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    # Check OpenRouter
    openrouter_status = "connected" if await llm_client.is_available() else "disconnected"
    
    # ChromaDB is locally embedded, mostly "ok" if we got this far
    chroma_status = "ok" 
    
    return HealthResponse(
        status="ok",
        openrouter=openrouter_status,
        chromadb=chroma_status,
        webrtc="listening", # Placeholder, assuming signaling is up
        version="1.0.0"
    )
