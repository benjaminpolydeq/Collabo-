# streamlit_app.py (à la racine du dépôt)

import os
import json
import streamlit as st
from dotenv import load_dotenv
import openai

# ==============================
# Charger les variables d'environnement
# ==============================
load_dotenv()  # charge le fichier .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# Configurer l’API OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==============================
# Service IA
# ==============================
class AIService:
    """Service d'analyse IA des conversations"""

    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY

    def _mock_analysis(self):
        return {
            "key_points": [
                "Discussion sur opportunités de collaboration",
                "Échange d'expertise",
                "Planification des prochaines étapes"
            ],
            "opportunities": ["Projet commun potentiel", "Partage de réseau"],
            "cooperation_model": "Partenariat stratégique basé sur expertise",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": [
                "Planifier un appel de suivi",
                "Partager documents pertinents",
                "Introduire aux contacts clés"
            ],
            "red_flags": [],
            "strengths": ["Communication claire", "Intérêts alignés", "Compétences complémentaires"]
        }

    def analyze_conversation(self, conversation_text: str, contact_name: str):
        if not AI_ANALYSIS_ENABLED or not self.api_key:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}.

Conversation:
{conversation_text}

Fournis une analyse structurée en JSON avec:
1. key_points: 3-5 points clés
2. opportunities: opportunités identifiées
3. cooperation_model: modèle de coopération
4. credibility_score: 0-10
5. usefulness_score: 0-10
6. success_probability: 0-100%
7. priority_level: low/medium/high
8. next_actions: 3 prochaines actions
9. red_flags: signaux d'alerte
10. strengths: points forts

Réponds uniquement en JSON, sans texte additionnel.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            
            # Nettoyer si le JSON est dans un code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            print(f"Erreur API OpenAI: {e}")
            return self._mock_analysis()

# ==============================
# Streamlit Interface
# ==============================
st.set_page_config(page_title="Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - AI Conversation Analysis")

# Initialiser le service IA
ai = AIService()

# Input utilisateur
contact_name = st.text_input("Nom du contact")
conversation_text = st.text_area("Texte de la conversation")

if st.button("Analyser la conversation"):
    if conversation_text.strip() == "" or contact_name.strip() == "":
        st.warning("Veuillez entrer le nom du contact et le texte de la conversation.")
    else:
        with st.spinner("Analyse en cours..."):
            result = ai.analyze_conversation(conversation_text, contact_name)
        st.success("Analyse terminée !")
        st.json(result)