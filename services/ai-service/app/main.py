from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai
from .extraction import layoutlm_extractor

app = FastAPI(
    title="MedExtract AI - AI Service",
    description="Extraction d'entites medicales : regles regex + LayoutLMv3 (DEV 3)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(ai.router)

@app.on_event("startup")
def startup():
    # Charge le modele LayoutLMv3 s'il a ete entraine, sinon mode regex.
    if layoutlm_extractor.load_model():
        print("[ai] LayoutLMv3 charge -> extraction par modele")
    else:
        print("[ai] Aucun modele -> extraction par regles regex (confiance 0.70)")

@app.get("/")
def root():
    return {"service": "ai-service", "docs": "/docs"}
