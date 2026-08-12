from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import documents

app = FastAPI(
    title="MedExtract AI - Document Service",
    description="Upload, stockage et gestion des documents medicaux (DEV 2)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(documents.router)

@app.get("/")
def root():
    return {"service": "document-service", "docs": "/docs"}
