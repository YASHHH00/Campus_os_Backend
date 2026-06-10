import json
from datetime import datetime
import pytz
from .llm_client import llm_client
from core.models import DeadlineInfo
from core.logging import get_logger

logger = get_logger(__name__)

async def extract(text: str) -> list[DeadlineInfo]:
    """
    Extracts datetimes from text using LLM. Resolves relative dates to IST.
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Normalize Hindi numerals to ASCII before passing
    hindi_to_ascii = str.maketrans('०१२३४५६७८९', '0123456789')
    normalized_text = text.translate(hindi_to_ascii)

    prompt = (
        "You are a deadline extraction assistant for Indian college students.\n"
        "Extract all deadlines/due dates from the following text.\n"
        "Text may be in Hindi, English, or Hinglish.\n"
        f"Current date and time (IST): {current_datetime}\n\n"
        "Return ONLY valid JSON, no explanation:\n"
        '{"events": [{"title": "...", "datetime_iso": "2024-...", "confidence": 0.9}]}\n\n'
        'If no deadline found, return: {"events": []}\n\n'
        f"Text: {normalized_text}"
    )

    try:
        response = await llm_client.generate(prompt=prompt)
        
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            json_str = response[start_idx:end_idx+1]
            data = json.loads(json_str)
            
            events = data.get("events", [])
            deadlines = []
            
            for event in events:
                title = event.get("title", "Event")
                dt_str = event.get("datetime_iso")
                conf = float(event.get("confidence", 0.5))
                
                if dt_str:
                    try:
                        # Validate ISO parsing
                        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                        # Keep it as ISO string
                        deadlines.append(DeadlineInfo(
                            title=str(title),
                            datetime_iso=dt.isoformat(),
                            confidence=conf
                        ))
                    except ValueError:
                        logger.warning(f"Could not parse datetime_iso: {dt_str}")
            
            # Sort by confidence descending
            deadlines.sort(key=lambda x: x.confidence, reverse=True)
            return deadlines
            
        return []

    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error in deadline extraction: {e}")
        return []
    except Exception as e:
        logger.error(f"Deadline extraction failed: {e}")
        return []
