# ai_service.py
import os
import json
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

class AIService:

    def analyze_conversation(self, conversation_text: str, contact_info: dict):
        if not AI_ANALYSIS_ENABLED or not OPENAI_API_KEY:
            return self._mock_analysis()
        prompt = f"""
Analyse la conversation avec {contact_info.get('name')}:
{conversation_text}

Réponds uniquement en JSON avec:
- key_points, opportunities, cooperation_model
- credibility_score, usefulness_score, success_probability
- priority_level, next_actions, red_flags, strengths
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
            print(f"Erreur IA: {e}")
            return self._mock_analysis()

    def _mock_analysis(self):
        return {"key_points": ["Discussion"], "opportunities": [], "cooperation_model": "",
                "credibility_score": 7, "usefulness_score": 7, "success_probability": 70,
                "priority_level": "medium", "next_actions": [], "red_flags": [], "strengths": []}
