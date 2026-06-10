import time
from . import image_preprocessor
from . import hindi_ocr
from core.exceptions import ImageProcessingError, OCRError
from core.logging import get_logger

logger = get_logger(__name__)

async def process_image(image_bytes: bytes) -> dict:
    """
    Orchestrates the OCR pipeline: preprocessing and text extraction.
    Returns a dictionary containing raw_text, confidence, language, and processing time.
    """
    start_time = time.time()
    
    try:
        # 1. Preprocess
        processed_image = image_preprocessor.preprocess(image_bytes)
        
        # 2. Extract Text
        result = hindi_ocr.extract_text(processed_image)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "raw_text": result["text"],
            "confidence": result["confidence"],
            "language": result["language_detected"],
            "ocr_duration_ms": duration_ms
        }
        
    except (ImageProcessingError, OCRError) as e:
        logger.error(f"OCR pipeline failed: {e.message}", extra={"error": str(e)})
        raise
    except Exception as e:
        logger.error("Unexpected error in OCR pipeline", extra={"error": str(e)})
        raise OCRError(f"Unexpected error: {e}")
