"""Etape 4 du RAG : appel du LLM Mistral via Ollama (local et gratuit)."""
import httpx
from ..config import settings

SYSTEM_PROMPT = (
    "Tu es un assistant medical informatif pour la plateforme MedExtract AI. "
    "Tu expliques des analyses biologiques de facon simple et pedagogique. "
    "REGLES ABSOLUES : ne jamais poser de diagnostic, ne jamais prescrire de "
    "medicament ni de dose, ne jamais dire au patient ce qu'il 'a'. En cas de "
    "doute, oriente vers un medecin. Reponds en francais, de maniere concise."
)


async def ask_llm(patient_context: str, knowledge: str, question: str) -> str:
    context_block = ""
    if patient_context:
        context_block += f"\n\nAnalyses du patient :\n{patient_context}"
    if knowledge:
        context_block += f"\n\nConnaissances medicales :\n{knowledge}"

    prompt = (f"{SYSTEM_PROMPT}\n{context_block}\n\n"
              f"Question du patient : {question}\n\nReponse informative :")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt,
                      "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
    except Exception as e:
        # Repli si Ollama indisponible : reponse basee uniquement sur la base
        print(f"[llm] Ollama indisponible : {e}")
        if knowledge:
            return knowledge
        return ("Je ne parviens pas a contacter le moteur de langage pour le "
                "moment. Voici ce que je peux dire de general : consultez votre "
                "medecin pour interpreter vos resultats.")
