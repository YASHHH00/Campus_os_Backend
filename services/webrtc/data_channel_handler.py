import base64
import time
from services.ocr import ocr_service
from services.vector.chroma_service import chroma_service
from core.logging import get_logger

logger = get_logger(__name__)

async def handle_message(message: dict) -> dict:
    """
    Handle incoming messages from Flutter phone app via WebRTC DataChannel.
    """
    msg_type = message.get("type")
    payload = message.get("payload", {})
    request_id = payload.get("requestId", "unknown")

    try:
        if msg_type == "ocr_request":
            logger.info(f"Received WebRTC ocr_request, id: {request_id}")
            image_b64 = payload.get("imageBase64")
            if not image_b64:
                return {"type": "error", "payload": {"message": "Missing imageBase64", "requestId": request_id}}
                
            image_bytes = base64.b64decode(image_b64)
            # Route to OCR pipeline
            result = await ocr_service.process_image(image_bytes)
            
            return {
                "type": "ocr_response", 
                "payload": {**result, "requestId": request_id}
            }

        elif msg_type == "note_sync":
            logger.info(f"Received WebRTC note_sync, id: {request_id}")
            notes = payload.get("notes", [])
            
            if notes:
                # Store in ChromaDB
                await chroma_service.upsert_notes(notes)
            
            synced_ids = [n.get("id") for n in notes if n.get("id") is not None]
            
            return {
                "type": "sync_ack", 
                "payload": {"syncedIds": synced_ids, "requestId": request_id}
            }

        elif msg_type == "ping":
            return {
                "type": "pong", 
                "payload": {"timestamp": time.time(), "requestId": request_id}
            }
            
        elif msg_type == "extract_deadline":
            logger.info(f"Received WebRTC extract_deadline, id: {request_id}")
            # The WebRTC client handles the direct LLM call logic or delegates here
            # For brevity, returning ack. 
            # In a full setup, this would call deadline_extractor.extract(text)
            return {
                "type": "extract_deadline_ack",
                "payload": {"status": "received", "requestId": request_id}
            }

        else:
            logger.warning(f"Unknown WebRTC message type: {msg_type}")
            return {
                "type": "error", 
                "payload": {"message": f"Unknown type: {msg_type}", "requestId": request_id}
            }

    except Exception as e:
        logger.error(f"Error handling WebRTC message {msg_type}: {e}")
        return {
            "type": "error",
            "payload": {"message": str(e), "requestId": request_id}
        }
