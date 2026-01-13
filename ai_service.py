# ai_service.py
import os
import json
from datetime import datetime
import openai

# Charger la clé OpenAI depuis l'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

DATA_FILE = "./data/conversations.json"

# Créer le répertoire data si n'existe pas
os.makedirs("./data", exist_ok=True)

class AIService:
    """Service IA pour analyser les conversations et générer des insights"""

    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY

    def _mock_analysis(self):
        """Analyse fictive si l'IA n'est pas activée"""
        return {
            "key_points": ["Discussion sur opportunités", "Échange d'expertise", "Planification"],
            "opportunities": ["Projet commun potentiel"],
            "cooperation_model": "Partenariat stratégique basé sur expertise",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Appel de suivi", "Partager documents", "Introduire contacts clés"],
            "red_flags": [],
            "strengths": ["Communication claire", "Intérêts alignés"]
        }

    def analyze_conversation(self, conversation_text: str, contact_name: str):
        """Analyse la conversation via GPT ou mode mock"""
        if not AI_ANALYSIS_ENABLED or not self.api_key:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}.
Conversation: {conversation_text}

Retourne un JSON avec:
1. key_points: 3-5 points clés
2. opportunities: opportunités
3. cooperation_model: modèle de coopération
4. credibility_score: 0-10
5. usefulness_score: 0-10
6. success_probability: 0-100%
7. priority_level: low/medium/high
8. next_actions: 3 prochaines actions
9. red_flags: signaux d'alerte
10. strengths: points forts
Réponds uniquement en JSON.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()

            # Nettoyer si JSON est dans un code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            print(f"Erreur API OpenAI: {e}")
            return self._mock_analysis()

    def save_conversation(self, contact: dict, conversation_text: str, analysis: dict):
        """Sauvegarde la conversation localement"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "contact": contact,
            "conversation": conversation_text,
            "analysis": analysis
        }

        all_data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    all_data = json.load(f)
                except:
                    all_data = []

        all_data.append(entry)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

    def load_conversations(self):
        """Charge toutes les conversations"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []