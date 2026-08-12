"""Base de connaissances medicales integree (RAG - etape 2).
Textes informatifs et vulgarises. AUCUN diagnostic, AUCUNE prescription.
"""
KNOWLEDGE_BASE = {
    "glycemie": (
        "La glycemie mesure le taux de sucre (glucose) dans le sang. A jeun, "
        "les valeurs normales se situent generalement entre 0.70 et 1.10 g/L. "
        "Une valeur elevee (hyperglycemie) repetee peut etre associee au "
        "diabete. L'HbA1c reflete la glycemie moyenne des 3 derniers mois."
    ),
    "cholesterol": (
        "Le cholesterol circule sous deux formes : le HDL ('bon cholesterol') "
        "et le LDL ('mauvais cholesterol'). Un LDL eleve et un HDL bas, ainsi "
        "que des triglycerides eleves, sont des facteurs de risque "
        "cardiovasculaire. Le cholesterol total normal est generalement < 2 g/L."
    ),
    "hemoglobine": (
        "L'hemoglobine transporte l'oxygene dans le sang. Les valeurs normales "
        "varient selon le sexe : environ 13-17 g/dL chez l'homme et 12-16 g/dL "
        "chez la femme. Une valeur basse peut evoquer une anemie."
    ),
    "vitamine d": (
        "La vitamine D participe a la sante des os et du systeme immunitaire. "
        "On parle d'insuffisance en dessous de 30 ng/mL et de carence en dessous "
        "de 20 ng/mL. Elle se synthetise avec l'exposition au soleil."
    ),
    "tsh": (
        "La TSH regule la thyroide. Une TSH elevee oriente vers une hypothyroidie "
        "(thyroide ralentie), une TSH basse vers une hyperthyroidie. Les normes "
        "usuelles sont d'environ 0.4 a 4.0 mUI/L."
    ),
    "creatinine": (
        "La creatinine et l'uree renseignent sur la fonction renale. Une "
        "creatinine elevee peut indiquer une baisse de la filtration des reins. "
        "On l'interprete avec le debit de filtration glomerulaire (DFG)."
    ),
    "uree": (
        "L'uree est un dechet elimine par les reins. Elle est interpretee avec la "
        "creatinine pour evaluer la fonction renale."
    ),
}

# Mots-cles -> cle de la base
KEYWORDS = {
    "glycemie": "glycemie", "glucose": "glycemie", "sucre": "glycemie",
    "diabete": "glycemie", "hba1c": "glycemie",
    "cholesterol": "cholesterol", "hdl": "cholesterol", "ldl": "cholesterol",
    "triglyceride": "cholesterol", "cardiovasculaire": "cholesterol",
    "hemoglobine": "hemoglobine", "anemie": "hemoglobine",
    "vitamine d": "vitamine d", "carence": "vitamine d",
    "tsh": "tsh", "thyroide": "tsh", "hypothyroidie": "tsh", "hyperthyroidie": "tsh",
    "creatinine": "creatinine", "renale": "creatinine", "rein": "creatinine",
    "uree": "uree",
}

def search_knowledge(query: str) -> list[str]:
    q = query.lower()
    found = []
    for kw, key in KEYWORDS.items():
        if kw in q and KNOWLEDGE_BASE[key] not in found:
            found.append(KNOWLEDGE_BASE[key])
    return found
