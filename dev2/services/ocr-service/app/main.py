from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ocr

app = FastAPI(
    title="MedExtract AI - OCR Service",
    description="Extraction de texte et positions via PaddleOCR (DEV 2)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(ocr.router)

@app.get("/")
def root():
    return {"service": "ocr-service", "docs": "/docs"}
