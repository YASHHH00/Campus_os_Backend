from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.logging import setup_logging
from api.middleware.request_id import RequestIDMiddleware
from api.middleware.rate_limiter import limiter

from api.routes import ocr, deadline, receipt, search, health
from services.webrtc.connection_manager import start_webrtc_listener

# Setup structured logging
setup_logging()

app = FastAPI(
    title="Campus OS Backend",
    version="1.0.0",
    description="Local AI server for Campus OS app"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(RequestIDMiddleware)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

# Include Routers
app.include_router(health.router, tags=["Health"])
app.include_router(ocr.router, tags=["OCR Pipeline"])
app.include_router(deadline.router, tags=["Deadline"])
app.include_router(receipt.router, tags=["Receipt"])
app.include_router(search.router, tags=["Search"])

@app.on_event("startup")
async def startup_event():
    start_webrtc_listener()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
