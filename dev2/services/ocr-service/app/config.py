from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://medextract:medextract@localhost:5432/medextract"
    OCR_LANG: str = "fr"          # PaddleOCR : francais
    PDF_DPI: int = 200            # resolution de conversion PDF -> image

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
