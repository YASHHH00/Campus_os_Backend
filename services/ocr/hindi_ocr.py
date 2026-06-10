import easyocr
import cv2
import numpy as np
from core.exceptions import OCRError
from core.logging import get_logger

logger = get_logger(__name__)

# Initialize reader globally so it's loaded once
try:
    reader = easyocr.Reader(['en', 'hi'], gpu=True)
except Exception:
    logger.warning("Failed to initialize EasyOCR with GPU, falling back to CPU.")
    reader = easyocr.Reader(['en', 'hi'], gpu=False)

def extract_text(image: np.ndarray, max_dim: int = 1920) -> dict:
    """
    Extract text using EasyOCR.
    Handles potential OOM by resizing and retrying once.
    """
    def do_ocr(img_array: np.ndarray):
        results = reader.readtext(img_array)
        text_segments = []
        confidences = []
        
        for (bbox, text, prob) in results:
            if text.strip():
                text_segments.append(text)
                confidences.append(prob)
                
        raw_text = " ".join(text_segments)
        avg_confidence = float(sum(confidences) / len(confidences)) if confidences else 0.0
        
        return {
            "text": raw_text,
            "confidence": avg_confidence,
            "language_detected": "en,hi"
        }

    try:
        return do_ocr(image)
    except RuntimeError as e:
        if "out of memory" in str(e).lower() or "oom" in str(e).lower():
            logger.warning("EasyOCR OOM detected, attempting to resize and retry.")
            h, w = image.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / float(max(h, w))
                resized = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                return do_ocr(resized)
            else:
                raise OCRError(f"OOM error, but image is already smaller than max_dim: {e}")
        else:
            raise OCRError(f"EasyOCR RuntimeError: {e}")
    except Exception as e:
        raise OCRError(f"Failed to extract text: {e}")
