from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import reports

app = FastAPI(
    title="MedExtract AI - Reporting Service",
    description="Statistiques, evolution et export Excel (DEV 4)",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(reports.router)

@app.get("/")
def root():
    return {"service": "reporting-service", "docs": "/docs"}
