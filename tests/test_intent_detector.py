import pytest
from unittest.mock import patch
from services.llm import intent_detector

@pytest.mark.asyncio
async def test_detect_receipt():
    with patch('services.llm.intent_detector.llm_client.generate') as mock_gen:
        mock_gen.return_value = "receipt"
        
        intent = await intent_detector.detect("Total: Rs 500\nMilk: 50")
        assert intent == "receipt"

@pytest.mark.asyncio
async def test_detect_deadline():
    with patch('services.llm.intent_detector.llm_client.generate') as mock_gen:
        mock_gen.return_value = "deadline_note"
        
        intent = await intent_detector.detect("Assignment due by next week Friday.")
        assert intent == "deadline_note"

@pytest.mark.asyncio
async def test_detect_blank():
    intent = await intent_detector.detect("   \n   ")
    assert intent == "blank"
    
@pytest.mark.asyncio
async def test_detect_note():
    with patch('services.llm.intent_detector.ollama_client.generate') as mock_gen:
        mock_gen.return_value = "note"
        
        intent = await intent_detector.detect("Machine learning involves training models on data.")
        assert intent == "note"
