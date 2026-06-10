class CampusOSError(Exception):
    """Base exception for all Campus OS backend errors."""
    def __init__(self, message: str, code: str = "internal_error", fallback_available: bool = False, fallback_data: dict | None = None):
        self.message = message
        self.code = code
        self.fallback_available = fallback_available
        self.fallback_data = fallback_data
        super().__init__(self.message)

class LLMUnavailableError(CampusOSError):
    def __init__(self, message: str = "LLM service unavailable", fallback_data: dict | None = None):
        super().__init__(message, code="llm_unavailable", fallback_available=bool(fallback_data), fallback_data=fallback_data)

class LLMTimeoutError(CampusOSError):
    def __init__(self, message: str = "LLM service timeout", fallback_data: dict | None = None):
        super().__init__(message, code="llm_timeout", fallback_available=bool(fallback_data), fallback_data=fallback_data)

class OCRError(CampusOSError):
    def __init__(self, message: str = "OCR processing failed"):
        super().__init__(message, code="ocr_failed")

class ImageProcessingError(CampusOSError):
    def __init__(self, message: str = "Failed to process image"):
        super().__init__(message, code="image_processing_failed")

class ValidationErrorCode(CampusOSError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, code="validation_failed")
