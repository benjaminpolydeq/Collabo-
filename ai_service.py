"""
Service d'Intelligence Artificielle pour Collabo
app/services/ai_service.py
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None
    print("⚠️  OpenAI non installé, le service IA fonctionnera en mode mock.")

class AIService:
    """Service d'analyse IA des conversations utilisant OpenAI GPT"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key and openai:
            openai.api_key = self.api_key
        else:
            print("⚠️  Pas de clé OpenAI fournie ou OpenAI non installé. Mode mock activé.")

    def analyze_conversation(self, conversation_text: str, contact_info: Dict) -> Dict:
        """Analyse une conversation et renvoie des insights"""
        if not self.api_key or not openai:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle entre un utilisateur et {contact_info.get('name', 'un contact')}.

Contexte du contact:
- Nom: {contact_info.get('name')}
- Domaine: {contact_info.get('domain')}
- Occasion de rencontre: {contact_info.get('occasion')}

Conversation:
{conversation_text}

Fournis une analyse structurée au format JSON avec:
1. "key_points": Liste des 3-5 points clés de la discussion
2. "opportunities": Opportunités de collaboration identifiées
3. "cooperation_model": Modèle de coopération suggéré
4. "credibility_score": Score de 0-10
5. "usefulness_score": Score de 0-10
6. "success_probability": Probabilité de succès (0-100%)
7. "priority_level": Niveau de priorité (low/medium/high)
8. "next_actions": 3 prochaines actions recommandées
9. "red_flags": Signaux d'alerte éventuels
10. "strengths": Points forts de cette relation

Réponds uniquement avec le JSON.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
            )
            content = response.choices[0].message.content
            # Nettoyage si nécessaire
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"Erreur d'analyse IA: {e}")
            return self._mock_analysis()

    def suggest_conversation_strategy(self, contact_info: Dict, goal: str) -> Dict:
        """Suggère une stratégie de conversation"""
        if not self.api_key or not openai:
            return self._mock_strategy()

        prompt = f"""
Crée une stratégie de conversation professionnelle pour atteindre cet objectif: {goal}

Contexte du contact:
- Nom: {contact_info.get('name')}
- Domaine: {contact_info.get('domain')}
- Sujets précédents: {contact_info.get('topics')}

Fournis au format JSON:
1. "opening": Phrase d'ouverture suggérée
2. "key_topics": 3-5 sujets à aborder
3. "questions": Questions pertinentes à poser
4. "value_propositions": Propositions de valeur à mettre en avant
5. "objections": Objections potentielles et réponses
6. "closing": Phrase de conclusion
7. "follow_up": Actions de suivi recommandées

Réponds uniquement avec le JSON.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
            )
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"Erreur de génération de stratégie: {e}")
            return self._mock_strategy()

    # -----------------------------
    # Méthodes mock pour le mode sans API
    # -----------------------------
    def _mock_analysis(self) -> Dict:
        return {
            "key_points": [
                "Discussion sur opportunités de collaboration",
                "Échange d'expertise",
                "Planification de prochaines étapes"
            ],
            "opportunities": [
                "Projet commun potentiel",
                "Partage de réseau"
            ],
            "cooperation_model": "Partenariat stratégique",
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
            "strengths": [
                "Communication claire",
                "Intérêts alignés",
                "Compétences complémentaires"
            ]
        }

    def _mock_strategy(self) -> Dict:
        return {
            "opening": "Ravi de reprendre contact. J'ai pensé à notre dernière discussion...",
            "key_topics": [
                "État d'avancement des projets",
                "Nouvelles opportunités de collaboration",
                "Mise à jour sur le secteur"
            ],
            "questions": [
                "Quels sont vos principaux défis?",
                "Comment puis-je vous aider?",
                "Quelles sont vos priorités?"
            ],
            "value_propositions": [
                "Expertise complémentaire",
                "Réseau étendu",
                "Expérience sectorielle"
            ],
            "objections": {
                "Manque de temps": "Proposer format court",
                "Budget limité": "Commencer par collaboration exploratoire"
            },
            "closing": "Excellent échange! Planifions notre prochain point dans 2 semaines?",
            "follow_up": [
                "Envoyer résumé de la conversation",
                "Partager ressources",
                "Calendrier RDV de suivi"
            ]
        }

# -----------------------------
# Helper
# -----------------------------
def get_ai_service() -> AIService:
    """Retourne une instance du service IA"""
    return AIService()