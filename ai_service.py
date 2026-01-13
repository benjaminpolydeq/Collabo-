import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 2000))

openai.api_key = OPENAI_API_KEY

class AIService:
    """Service IA pour analyser les conversations et générer stratégie"""

    def analyze_conversation(self, text, contact_name):
        if not AI_ANALYSIS_ENABLED or not OPENAI_API_KEY:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}:
{text}

Retourne un JSON avec:
- key_points
- opportunities
- cooperation_model
- credibility_score
- usefulness_score
- success_probability
- priority_level
- next_actions
- red_flags
- strengths
"""
        try:
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=AI_MAX_TOKENS
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("{"):
                return json.loads(content)
            return {"raw": content}
        except Exception as e:
            return {"error": str(e)}

    def _mock_analysis(self):
        return {
            "key_points": ["Discussion sur opportunités", "Échange d'expertise"],
            "opportunities": ["Projet commun potentiel"],
            "cooperation_model": "Partenariat stratégique",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Planifier suivi", "Partager documents"],
            "red_flags": [],
            "strengths": ["Communication claire"]
        }