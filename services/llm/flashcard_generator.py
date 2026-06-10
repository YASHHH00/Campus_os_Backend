import json
from .llm_client import llm_client
from core.models import FlashCard
from core.logging import get_logger

logger = get_logger(__name__)

async def generate(text: str) -> list[FlashCard]:
    """
    Generates Q&A flashcards from the text.
    """
    if not text or len(text.strip()) < 30:
        return []

    system_prompt = (
        "You are an educational assistant. Extract key facts from the text and create 3 to 5 question-answer flashcards. "
        "Return ONLY a valid JSON list of objects, where each object has 'question' and 'answer' string keys. "
        "Do not wrap the JSON in markdown code blocks. Example: "
        '[{"question": "What is X?", "answer": "X is Y."}, {"question": "Why Z?", "answer": "Because W."}]'
    )

    try:
        response = await llm_client.generate(prompt=text, system=system_prompt)
        
        # Clean potential markdown or extra text
        # The ollama_client already strips markdown fences, but let's be safe
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        
        start_idx = response.find('[')
        end_idx = response.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            json_str = response[start_idx:end_idx+1]
            data = json.loads(json_str)
            
            flashcards = []
            for item in data:
                if "question" in item and "answer" in item:
                    flashcards.append(FlashCard(
                        question=str(item["question"]),
                        answer=str(item["answer"])
                    ))
            return flashcards
            
        logger.warning(f"Failed to parse flashcards JSON from response: {response}")
        return []

    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error in flashcard generation: {e}")
        # Could implement a retry here with a stricter prompt, but for now return empty
        return []
    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        return []
