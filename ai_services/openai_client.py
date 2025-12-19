import openai
from django.conf import settings

# Placeholder - ideally API key is in settings.py from env
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def correct_and_structure_note(text):
    """
    Uses GPT-4o to correct, structure, and check truthfulness of the note.
    Returns a dictionary with 'content', 'truth_score', 'issues'.
    """
    if not OPENAI_API_KEY:
        return {
            "content": f"Simulation (Pas de clé API): Note structurée pour: {text[:50]}...",
            "truth_score": 85,
            "issues": ["Simulation: Vérification impossible sans clé API."]
        }
        
    prompt = f"""
    Agis comme un assistant pédagogique expert. Analyse la note suivante:
    "{text}"
    
    1. Corrige les fautes d'orthographe et de grammaire.
    2. Structure le contenu de manière élégante et hiérarchisée :
       - Utilise un Titre principal (Markdown `#`).
       - Utilise des Sous-titres (Markdown `##`) pour les sections.
       - Utilise des listes à puces pour les énumérations.
       - GÉNÈRE AUTOMATIQUEMENT DES TABLEAUX Markdown si le contenu contient des statistiques, des comparaisons ou des données chiffrées.
    3. Détecte les fausses informations potentielles.
    
    Réponds EXCLUSIVEMENT au format JSON suivant:
    {{
        "title": "un titre court et accrocheur (max 5-6 mots)",
        "corrected_content": "le contenu en markdown",
        "truth_score": 0-100 (int),
        "issues": ["liste des fausses informations ou imprécisions détectées"]
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un assistant éducatif noteo."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        import json
        return json.loads(content)
    except Exception as e:
        return {
            "content": text,
            "truth_score": 0,
            "issues": [f"Erreur IA: {str(e)}"]
        }

def verify_answer_accuracy(question, answer):
    """
    Checks the veracity of an answer given a question.
    Returns a dictionary with 'truth_score' and 'ai_feedback'.
    """
    if not OPENAI_API_KEY:
        return {
            "truth_score": 75,
            "ai_feedback": "Simulation: L'IA estime que cette réponse est cohérente mais n'a pas pu vérifier les faits sans clé API."
        }

    prompt = f"""
    En tant qu'expert en éducation, évalue la véracité et la pertinence de la réponse suivante à la question donnée.
    
    QUESTION: "{question}"
    RÉPONSE: "{answer}"
    
    1. Attribue un score de véracité de 0 à 100.
    2. Donne un feedback court (2 phrases) expliquant le score ou corrigeant une erreur mineure.
    
    Réponds EXCLUSIVEMENT au format JSON suivant:
    {{
        "truth_score": 0-100 (int),
        "ai_feedback": "ton feedback ici"
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un évaluateur de contenu éducatif précis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "truth_score": 0,
            "ai_feedback": f"Erreur lors de la vérification IA: {str(e)}"
        }

def verify_publication_accuracy(content):
    """
    Checks the veracity of a community publication.
    """
    if not OPENAI_API_KEY:
        return {
            "truth_score": 90,
            "ai_feedback": "Simulation: Information semble fiable."
        }

    prompt = f"""
    Analyse la véracité de cette publication éducative/informative :
    "{content}"
    
    1. Attribue un score de fiabilité de 0 à 100.
    2. Donne un feedback très court (1-2 phrases).
    
    Réponds EXCLUSIVEMENT au format JSON :
    {{
        "truth_score": 0-100 (int),
        "ai_feedback": "ton feedback ici"
    }}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en vérification de faits."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"truth_score": 0, "ai_feedback": str(e)}

import json # Ensure json is imported
