from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "minimax/minimax-01"
    openrouter_api_key: str = ""
    llm_timeout: float = 30.0
    chromadb_path: str = "./data/chromadb"
    max_image_size_mb: float = 10.0
    ocr_confidence_threshold: float = 0.6
    supabase_url: str = "https://zodonxxsapwbirmnrnwo.supabase.co"
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvZG9ueHhzYXB3YmlybW5ybndvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA2Nzc2MjksImV4cCI6MjA5NjI1MzYyOX0.EzkZBVEhF16P-CHQMNWUVmunChme0452eOiZ2RwQ2ss"
    webrtc_enabled: bool = True
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
