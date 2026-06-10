from typing import Literal
from .llm_client import llm_client
from core.logging import get_logger

logger = get_logger(__name__)

async def detect(text: str) -> Literal["note", "receipt", "deadline_note", "blank"]:
    """
    Detects if the text is a note, a receipt, or a note with a deadline.
    Returns "blank" if the text is empty or very short.
    """
    if not text or len(text.strip()) < 5:
        return "blank"

    system_prompt = (
        "You are a smart text classifier. Classify the following text into exactly one of these three categories:\n"
        "1. 'receipt' : The text looks like a bill, invoice, or receipt (contains prices, items, total amount, taxes).\n"
        "2. 'deadline_note' : The text looks like an assignment, syllabus, notice or note that mentions a specific due date, deadline, exam date, or submission date.\n"
        "3. 'note' : Any other handwritten or printed text, study material, general notes, etc.\n"
        "Reply ONLY with the category name ('receipt', 'deadline_note', or 'note') and nothing else. Do not add any punctuation."
    )

    try:
        response = await llm_client.generate(prompt=text, system=system_prompt)
        intent = response.strip().lower()
        
        # Clean up in case LLM adds extra text
        if "receipt" in intent:
            return "receipt"
        elif "deadline" in intent:
            return "deadline_note"
        else:
            return "note"
            
    except Exception as e:
        logger.error(f"Intent detection failed: {e}. Defaulting to 'note'.")
        return "note"
