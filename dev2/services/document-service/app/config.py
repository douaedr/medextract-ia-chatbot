from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://medextract:medextract@localhost:5432/medextract"
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_MB: int = 20
    OCR_SERVICE_URL: str = "http://ocr-service:8083"
    AI_SERVICE_URL: str = "http://ai-service:8084"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
