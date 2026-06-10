from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import uuid
from core.models import ReceiptInfo
from core.logging import get_logger
from services.ocr import ocr_service
from services.receipt import receipt_parser

logger = get_logger(__name__)
router = APIRouter()

class ParseReceiptResponse(BaseModel):
    receipt: ReceiptInfo
    request_id: str

@router.post("/parse_receipt", response_model=ParseReceiptResponse)
async def parse_receipt(
    request: Request,
    text: str | None = Form(None),
    image: UploadFile | None = File(None)
):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    raw_text = ""
    
    if image:
        try:
            image_bytes = await image.read()
            ocr_res = await ocr_service.process_image(image_bytes)
            raw_text = ocr_res["raw_text"]
        except Exception as e:
            logger.error(f"OCR failed for receipt image: {e}")
            raise HTTPException(status_code=422, detail="Failed to extract text from receipt image")
    elif text:
        raw_text = text
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'text' or 'image'")
        
    receipt_info = receipt_parser.parse(raw_text)
    
    return ParseReceiptResponse(
        receipt=receipt_info,
        request_id=request_id
    )
