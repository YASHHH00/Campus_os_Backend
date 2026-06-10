import pytest
from unittest.mock import patch, MagicMock
from services.ocr import ocr_service
from core.exceptions import ImageProcessingError

@pytest.mark.asyncio
async def test_process_image_success():
    # Mock preprocessor and easyocr
    with patch('services.ocr.image_preprocessor.preprocess') as mock_preprocess, \
         patch('services.ocr.hindi_ocr.extract_text') as mock_extract:
        
        mock_preprocess.return_value = "dummy_numpy_array"
        mock_extract.return_value = {
            "text": "mocked text from ocr",
            "confidence": 0.95,
            "language_detected": "en,hi"
        }
        
        result = await ocr_service.process_image(b"fake image bytes")
        
        assert result["raw_text"] == "mocked text from ocr"
        assert result["confidence"] == 0.95
        assert result["language"] == "en,hi"
        assert "ocr_duration_ms" in result
        
        mock_preprocess.assert_called_once_with(b"fake image bytes")
        mock_extract.assert_called_once_with("dummy_numpy_array")

@pytest.mark.asyncio
async def test_process_image_preprocessing_failure():
    with patch('services.ocr.image_preprocessor.preprocess') as mock_preprocess:
        mock_preprocess.side_effect = ImageProcessingError("Corrupt image")
        
        with pytest.raises(ImageProcessingError):
            await ocr_service.process_image(b"corrupt bytes")
