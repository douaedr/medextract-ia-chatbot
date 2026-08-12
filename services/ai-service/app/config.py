from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://medextract:medextract@localhost:5432/medextract"
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    OCR_SERVICE_URL: str = "http://ocr-service:8083"
    MODEL_DIR: str = "/app/model/layoutlmv3-medical"
    REGEX_CONFIDENCE: float = 0.70   # confiance fixe pour l'extraction par regles

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
