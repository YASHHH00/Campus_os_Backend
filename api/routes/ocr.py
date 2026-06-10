from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Response, status
from fastapi.responses import JSONResponse
import uuid
import time
from config import settings
from core.models import OcrResponse, ErrorResponse
from core.logging import get_logger
from core.exceptions import LLMTimeoutError, LLMUnavailableError, OCRError, ImageProcessingError

from services.ocr import ocr_service
from services.llm import intent_detector, summarizer, flashcard_generator, deadline_extractor
from services.receipt import receipt_parser
from services.vector.chroma_service import chroma_service

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/ocr", response_model=OcrResponse)
async def process_ocr(request: Request, response: Response, image: UploadFile = File(...)):
    start_time = time.time()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    try:
        # 1. Validate
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported media type. Allowed: {ALLOWED_TYPES}")
            
        image_bytes = await image.read()
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > settings.max_image_size_mb:
            raise HTTPException(status_code=413, detail=f"Image too large: {size_mb:.2f}MB > {settings.max_image_size_mb}MB")
            
        # 2 & 3. Preprocess and Extract OCR
        ocr_res = await ocr_service.process_image(image_bytes)
        raw_text = ocr_res["raw_text"]
        confidence = ocr_res["confidence"]
        language = ocr_res["language"]
        
        warning = None
        
        # Check if blank
        if not raw_text or len(raw_text.strip()) < 5:
            duration_ms = int((time.time() - start_time) * 1000)
            return OcrResponse(
                request_id=request_id,
                raw_text=raw_text,
                confidence=confidence,
                language=language,
                intent="blank",
                processing_time_ms=duration_ms,
                warning="Text too short or blank image"
            )
            
        # 4. Confidence warning
        if confidence < settings.ocr_confidence_threshold:
            warning = "low_confidence_ocr"
            response.status_code = status.HTTP_206_PARTIAL_CONTENT
            
        # 5. Detect Intent
        try:
            intent = await intent_detector.detect(raw_text)
        except (LLMTimeoutError, LLMUnavailableError) as e:
            logger.warning(f"LLM failure during intent detection: {e.message}")
            intent = "note"
            warning = "llm_unavailable_for_intent"
            
        summary = None
        flashcards = None
        deadline_info = None
        receipt_info = None
        
        # 6. Branch on intent
        try:
            if intent == "receipt":
                receipt_info = receipt_parser.parse(raw_text)
                
            elif intent == "deadline_note":
                summary = await summarizer.summarize(raw_text)
                deadlines = await deadline_extractor.extract(raw_text)
                if deadlines:
                    deadline_info = deadlines[0] # Just return the top confidence one
                    
            else: # note
                summary = await summarizer.summarize(raw_text)
                flashcards = await flashcard_generator.generate(raw_text)
                
        except LLMTimeoutError:
            warning = "llm_timeout"
        except LLMUnavailableError:
            warning = "llm_unavailable"
        except Exception as e:
            logger.error(f"Error during intent specific processing: {e}")
            
        # 7. Store in ChromaDB
        note_id = str(uuid.uuid4())
        await chroma_service.upsert_note(
            note_id=note_id,
            text=raw_text,
            metadata={
                "intent": intent,
                "confidence": confidence
            }
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 8. Return structured response
        return OcrResponse(
            request_id=request_id,
            raw_text=raw_text,
            confidence=confidence,
            language=language,
            intent=intent,
            summary=summary,
            flashcards=flashcards,
            deadline=deadline_info,
            receipt=receipt_info,
            processing_time_ms=duration_ms,
            warning=warning
        )

    except HTTPException:
        raise
    except (ImageProcessingError, OCRError) as e:
        logger.error(f"OCR Pipeline error: {e}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=e.code,
                message=e.message,
                request_id=request_id,
                fallback_available=False
            ).model_dump()
        )
    except Exception as e:
        logger.error(f"Unexpected error in /ocr: {e}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred processing the image",
                request_id=request_id,
                fallback_available=False
            ).model_dump()
        )
