from .llm_client import llm_client
from core.logging import get_logger

logger = get_logger(__name__)

async def summarize(text: str) -> str:
    """
    Generates a concise summary of the provided text.
    """
    if not text or len(text.strip()) < 20:
        return "Text too short to summarize."

    system_prompt = (
        "You are an AI assistant that helps students summarize their notes. "
        "Provide a clear, concise summary of the following text in a few bullet points. "
        "Keep it brief and focus on the main concepts."
    )

    try:
        summary = await llm_client.generate(prompt=text, system=system_prompt)
        return summary.strip()
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "Summary could not be generated."
