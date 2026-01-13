"""
Service d'Intelligence Artificielle pour Collabo
Multi-utilisateur, Claude + GPT, mode mock si API absente
app/services/ai_service.py
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

import streamlit as st  # pour logs et warnings

# Helper pour extraire JSON même s'il est encadré par ``` ou ```json
def _extract_json(content: str) -> str:
    if "```json" in content:
        return content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return content.strip()


class AIService:
    """Service IA multi-utilisateur pour Collabo"""

    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None, model_type: str = "anthropic"):
        """
        Args:
            api_key: clé API pour Claude ou OpenAI
            user_id: identifiant de l'utilisateur (pour multi-utilisateur)
            model_type: 'anthropic' ou 'openai'
        """
        self.user_id = user_id or "default_user"
        self.model_type = model_type.lower()

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") if model_type == "anthropic" else os.getenv("OPENAI_API_KEY")

        self.client = None

        if self.model_type == "anthropic":
            try:
                import anthropic
                if self.api_key:
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                else:
                    st.warning("⚠️ Clé API Anthropic manquante. Mode mock activé.")
            except ImportError:
                st.error("Package 'anthropic' non installé. Mode mock activé.")
        elif self.model_type == "openai":
            try:
                import openai
                if self.api_key:
                    openai.api_key = self.api_key
                    self.client = openai
                else:
                    st.warning("⚠️ Clé API OpenAI manquante. Mode mock activé.")
            except ImportError:
                st.error("Package 'openai' non installé. Mode mock activé.")
        else:
            st.warning(f"⚠️ Modèle inconnu '{model_type}'. Mode mock activé.")

    # -----------------------------------
    # Méthodes principales
    # -----------------------------------

    def analyze_conversation(self, conversation_text: str, contact_info: Dict) -> Dict:
        """Analyse la conversation et retourne un JSON structuré"""
        if not self.client:
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
1. "key_points": Liste des 3-5 points clés
2. "opportunities": Opportunités de collaboration
3. "cooperation_model": Modèle de coopération suggéré
4. "credibility_score": 0-10
5. "usefulness_score": 0-10
6. "success_probability": 0-100%
7. "priority_level": low/medium/high
8. "next_actions": 3 prochaines actions
9. "red_flags": Signaux d'alerte éventuels
10. "strengths": Points forts
Réponds uniquement avec le JSON.
"""

        try:
            if self.model_type == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:  # openai GPT
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                content = response.choices[0].message.content

            analysis = json.loads(_extract_json(content))
            return analysis
        except Exception as e:
            st.error(f"Erreur IA analyze_conversation: {e}")
            return self._mock_analysis()

    def suggest_conversation_strategy(self, contact_info: Dict, goal: str) -> Dict:
        """Suggère une stratégie de conversation"""
        if not self.client:
            return self._mock_strategy()

        prompt = f"""
Crée une stratégie de conversation professionnelle pour atteindre cet objectif: {goal}

Contexte du contact:
- Nom: {contact_info.get('name')}
- Domaine: {contact_info.get('domain')}
- Sujets précédents: {contact_info.get('topics')}

Fournis un JSON:
1. "opening"
2. "key_topics"
3. "questions"
4. "value_propositions"
5. "objections"
6. "closing"
7. "follow_up"
Réponds uniquement avec JSON.
"""

        try:
            if self.model_type == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500
                )
                content = response.choices[0].message.content

            return json.loads(_extract_json(content))
        except Exception as e:
            st.error(f"Erreur IA suggest_conversation_strategy: {e}")
            return self._mock_strategy()

    def extract_action_items(self, conversation_text: str) -> List[Dict]:
        """Extrait les actions à réaliser d'une conversation"""
        if not self.client:
            return self._mock_actions()

        prompt = f"""
Extrais toutes les actions à réaliser de cette conversation:

{conversation_text}

Pour chaque action, fournis un JSON avec:
- "action", "responsible", "deadline", "priority", "status"
Réponds uniquement avec un array JSON.
"""

        try:
            if self.model_type == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                content = response.choices[0].message.content

            return json.loads(_extract_json(content))
        except Exception as e:
            st.error(f"Erreur IA extract_action_items: {e}")
            return self._mock_actions()

    def generate_meeting_summary(self, conversation_text: str, contact_name: str) -> str:
        """Génère un résumé professionnel de réunion"""
        if not self.client:
            return self._mock_summary(contact_name)

        prompt = f"""
Crée un résumé professionnel de cette conversation avec {contact_name}:

{conversation_text}

Inclure:
1. Contexte de la rencontre
2. Principaux sujets
3. Décisions
4. Actions convenues
5. Prochaines étapes

Format: texte structuré professionnel.
"""

        try:
            if self.model_type == "anthropic":
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                content = response.choices[0].message.content

            return content
        except Exception as e:
            st.error(f"Erreur IA generate_meeting_summary: {e}")
            return self._mock_summary(contact_name)

    # -----------------------------------
    # Méthodes mock pour fonctionnement offline
    # -----------------------------------

    def _mock_analysis(self) -> Dict:
        return {
            "key_points": ["Discussion sur opportunités de collaboration", "Échange d'expertise", "Planification prochaines étapes"],
            "opportunities": ["Projet commun potentiel", "Partage de réseau"],
            "cooperation_model": "Partenariat stratégique",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Planifier un appel", "Partager documents", "Introduire contacts clés"],
            "red_flags": [],
            "strengths": ["Communication claire", "Intérêts alignés", "Compétences complémentaires"]
        }

    def _mock_strategy(self) -> Dict:
        return {
            "opening": "Ravi de reprendre contact...",
            "key_topics": ["Avancement projets", "Nouvelles opportunités", "Mise à jour secteur"],
            "questions": ["Défis actuels?", "Comment puis-je aider?", "Priorités prochains mois?"],
            "value_propositions": ["Expertise complémentaire", "Réseau étendu", "Expérience"],
            "objections": {"Manque de temps": "Proposer format court", "Budget limité": "Commencer exploratoire"},
            "closing": "Excellent échange! Planifions prochain point",
            "follow_up": ["Envoyer résumé", "Partager ressources", "Calendrier RDV"]
        }

    def _mock_actions(self) -> List[Dict]:
        return [
            {"action": "Envoyer présentation", "responsible": "user", "deadline": "3 jours", "priority": "high", "status": "pending"},
            {"action": "Organiser réunion", "responsible": "both", "deadline": "1 semaine", "priority": "medium", "status": "pending"}
        ]

    def _mock_summary(self, contact_name: str) -> str:
        return f"""
Résumé de la Conversation avec {contact_name}

**Contexte:**
Réunion exploratoire pour discuter d'opportunités de collaboration.

**Sujets Principaux:**
- Présentation des activités respectives
- Identification synergies potentielles
- Discussion défis du secteur

**Décisions Prises:**
- Poursuivre échanges réguliers
- Explorer opportunités projet commun

**Actions Convenues:**
- Partage documentation
- Planification prochain point

**Prochaines Étapes:**
Maintenir dynamique d'échange et concrétiser pistes identifiées.
"""

# -----------------------------------
# Helper pour obtenir le service IA
# -----------------------------------
def get_ai_service(user_id: Optional[str] = None, model_type: str = "anthropic") -> AIService:
    return AIService(user_id=user_id, model_type=model_type)