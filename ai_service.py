import os
import json
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

class AIService:
    """Service IA pour analyser les conversations"""

    def analyze_conversation(self, conversation_text, contact_name):
        if not AI_ANALYSIS_ENABLED or not OPENAI_API_KEY:
            return {"mock": "Analyse IA désactivée"}

        prompt = f"""
Analyse cette conversation avec {contact_name}.

Conversation:
{conversation_text}

Fournis une analyse structurée en JSON avec:
- key_points: points clés
- opportunities: opportunités
- cooperation_model: modèle de coopération
- credibility_score: 0-10
- usefulness_score: 0-10
- success_probability: 0-100%
- priority_level: low/medium/high
- next_actions: prochaines actions
- red_flags: signaux d'alerte
- strengths: points forts

Réponds uniquement en JSON.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()

            # Nettoyer si JSON dans un bloc
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}