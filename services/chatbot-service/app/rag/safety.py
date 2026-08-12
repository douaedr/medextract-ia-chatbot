"""Regles de securite absolues du chatbot medical."""
import re

DISCLAIMER = ("Cette reponse est informative et ne remplace pas l'avis d'un "
              "professionnel de sante.")

# Mots interdits dans la reponse du modele (filtrage de sortie)
FORBIDDEN = ["diagnostic", "vous avez", "prenez", "medicament", "posologie",
             "prescris", "prescription", "dosage", "traitement"]

# Motifs de question demandant un diagnostic / une prescription
DIAGNOSTIC_QUESTION = re.compile(
    r"\b(j'?ai\s+(le|la|un|une)|est[- ]ce que j'?ai|suis[- ]je|"
    r"quel\s+(medicament|traitement)|que\s+(dois|puis)[- ]je\s+prendre|"
    r"quelle?\s+(posologie|dose))\b", re.I)


def is_diagnostic_request(message: str) -> bool:
    return bool(DIAGNOSTIC_QUESTION.search(message))


def refusal_answer() -> str:
    return ("Je ne peux pas poser de diagnostic ni recommander de traitement. "
            "Ces analyses doivent etre interpretees par un medecin qui connait "
            "votre situation complete. Je vous invite a consulter un "
            "professionnel de sante.\n\n" + DISCLAIMER)


def sanitize_output(text: str) -> str:
    """Neutralise tout contenu de type diagnostic/prescription dans la reponse."""
    cleaned = text
    for word in FORBIDDEN:
        # remplace le mot par une formulation neutre
        cleaned = re.sub(rf"\b{re.escape(word)}\b", "[information a valider avec un medecin]",
                         cleaned, flags=re.I)
    return cleaned


def ensure_disclaimer(text: str) -> str:
    if DISCLAIMER.lower() not in text.lower():
        text = text.rstrip() + "\n\n" + DISCLAIMER
    return text
