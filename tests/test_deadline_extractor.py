import pytest
from unittest.mock import patch
from services.llm import deadline_extractor

@pytest.mark.asyncio
async def test_extract_deadline_success():
    mock_json = """
    {
        "events": [
            {"title": "Assignment", "datetime_iso": "2024-12-01T10:00:00+05:30", "confidence": 0.9}
        ]
    }
    """
    with patch('services.llm.deadline_extractor.llm_client.generate') as mock_gen:
        mock_gen.return_value = mock_json
        
        deadlines = await deadline_extractor.extract("Assignment due on 1st Dec 2024 at 10 AM")
        
        assert len(deadlines) == 1
        assert deadlines[0].title == "Assignment"
        assert "2024-12-01" in deadlines[0].datetime_iso

@pytest.mark.asyncio
async def test_extract_deadline_hindi_numerals():
    mock_json = """
    {
        "events": [
            {"title": "Exam", "datetime_iso": "2024-10-12T00:00:00+05:30", "confidence": 0.8}
        ]
    }
    """
    with patch('services.llm.deadline_extractor.ollama_client.generate') as mock_gen:
        mock_gen.return_value = mock_json
        
        deadlines = await deadline_extractor.extract("Exam on १२ Oct")
        
        # Check if the prompt got normalized ASCII
        prompt_used = mock_gen.call_args[1]['prompt']
        assert "12" in prompt_used
        assert "१२" not in prompt_used
        
        assert len(deadlines) == 1
