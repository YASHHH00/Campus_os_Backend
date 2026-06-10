import pytest
from unittest.mock import patch
from services.llm import flashcard_generator

@pytest.mark.asyncio
async def test_generate_flashcards_success():
    mock_json = """
    ```json
    [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"}
    ]
    ```
    """
    with patch('services.llm.flashcard_generator.llm_client.generate') as mock_gen:
        mock_gen.return_value = mock_json
        
        cards = await flashcard_generator.generate("Some text long enough to trigger flashcards. This text needs to be more than 30 characters.")
        
        assert len(cards) == 2
        assert cards[0].question == "Q1"
        assert cards[1].answer == "A2"

@pytest.mark.asyncio
async def test_generate_flashcards_malformed_json():
    mock_json = "This is not json"
    with patch('services.llm.flashcard_generator.llm_client.generate') as mock_gen:
        mock_gen.return_value = mock_json
        
        cards = await flashcard_generator.generate("Some text long enough to trigger flashcards. This text needs to be more than 30 characters.")
        
        assert len(cards) == 0

@pytest.mark.asyncio
async def test_generate_flashcards_short_text():
    cards = await flashcard_generator.generate("Too short")
    assert len(cards) == 0
