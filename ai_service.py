# ai_service.py
import os
import json
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AIService:
    """Service d'analyse IA"""

    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key

    def _mock_analysis(self):
        return {
            "key_points": ["Point clé 1", "Point clé 2", "Point clé 3"],
            "opportunities": ["Opportunité 1", "Opportunité 2"],
            "cooperation_model": "Partenariat stratégique",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Suivi 1", "Suivi 2"],
            "red_flags": [],
            "strengths": ["Communication claire", "Compétences alignées"]
        }

    def analyze_conversation(self, conversation_text: str, contact_name: str):
        if not conversation_text.strip() or not self.api_key:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}.

Conversation:
{conversation_text}

Fournis une analyse structurée en JSON avec:
1. key_points: 3-5 points clés
2. opportunities: opportunités
3. cooperation_model
4. credibility_score: 0-10
5. usefulness_score: 0-10
6. success_probability: 0-100%
7. priority_level: low/medium/high
8. next_actions: 3 prochaines actions
9. red_flags: signaux d'alerte
10. strengths

Réponds uniquement en JSON.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"Erreur API OpenAI: {e}")
            return self._mock_analysis()