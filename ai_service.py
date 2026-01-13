"""
Service d'Intelligence Artificielle pour Collabo
app/services/ai_service.py
"""

import anthropic
import os
from typing import Dict, List, Optional
import json

class AIService:
    """Service d'analyse IA des conversations"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
    
    def analyze_conversation(self, conversation_text: str, contact_info: Dict) -> Dict:
        """
        Analyse une conversation et extrait les insights clés
        
        Args:
            conversation_text: Texte de la conversation
            contact_info: Informations sur le contact
            
        Returns:
            Dictionnaire contenant l'analyse complète
        """
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
1. "key_points": Liste des 3-5 points clés de la discussion
2. "opportunities": Opportunités de collaboration identifiées
3. "cooperation_model": Modèle de coopération suggéré
4. "credibility_score": Score de 0-10 sur la crédibilité
5. "usefulness_score": Score de 0-10 sur l'utilité
6. "success_probability": Probabilité de succès (0-100%)
7. "priority_level": Niveau de priorité (low/medium/high)
8. "next_actions": 3 prochaines actions recommandées
9. "red_flags": Signaux d'alerte éventuels
10. "strengths": Points forts de cette relation

Réponds uniquement avec le JSON, sans texte additionnel.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            # Nettoyer le JSON si nécessaire
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            print(f"Erreur d'analyse IA: {e}")
            return self._mock_analysis()
    
    def suggest_conversation_strategy(self, contact_info: Dict, goal: str) -> Dict:
        """
        Suggère une stratégie de conversation
        
        Args:
            contact_info: Informations du contact
            goal: Objectif de la conversation
            
        Returns:
            Stratégie de conversation suggérée
        """
        if not self.client:
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
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Erreur de génération de stratégie: {e}")
            return self._mock_strategy()
    
    def extract_action_items(self, conversation_text: str) -> List[Dict]:
        """
        Extrait les actions à réaliser d'une conversation
        
        Args:
            conversation_text: Texte de la conversation
            
        Returns:
            Liste des actions avec priorités
        """
        if not self.client:
            return self._mock_actions()
        
        prompt = f"""
Extrais toutes les actions à réaliser de cette conversation:

{conversation_text}

Pour chaque action, fournis un JSON avec:
- "action": Description de l'action
- "responsible": Qui doit la faire (user/contact/both)
- "deadline": Délai suggéré
- "priority": high/medium/low
- "status": pending

Réponds avec un array JSON d'actions.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Erreur d'extraction d'actions: {e}")
            return self._mock_actions()
    
    def generate_meeting_summary(self, conversation_text: str, contact_name: str) -> str:
        """
        Génère un résumé professionnel de réunion
        
        Args:
            conversation_text: Texte de la conversation
            contact_name: Nom du contact
            
        Returns:
            Résumé formaté
        """
        if not self.client:
            return self._mock_summary(contact_name)
        
        prompt = f"""
Crée un résumé professionnel de cette conversation avec {contact_name}:

{conversation_text}

Le résumé doit inclure:
1. Contexte de la rencontre
2. Principaux sujets abordés
3. Décisions prises
4. Actions convenues
5. Prochaines étapes

Format: texte structuré professionnel, concis mais complet.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Erreur de génération de résumé: {e}")
            return self._mock_summary(contact_name)
    
    def classify_contact_importance(self, contact_info: Dict, interactions: List) -> Dict:
        """
        Classifie l'importance d'un contact basé sur les interactions
        
        Args:
            contact_info: Informations du contact
            interactions: Historique des interactions
            
        Returns:
            Classification et recommandations
        """
        score = 0
        factors = []
        
        # Analyse du domaine
        important_domains = ['technologie', 'finance', 'santé', 'éducation']
        if any(d in contact_info.get('domain', '').lower() for d in important_domains):
            score += 20
            factors.append("Domaine stratégique")
        
        # Fréquence des interactions
        if len(interactions) > 10:
            score += 30
            factors.append("Interactions fréquentes")
        elif len(interactions) > 5:
            score += 20
            factors.append("Interactions régulières")
        
        # Qualité des conversations
        long_conversations = sum(1 for i in interactions if len(str(i)) > 500)
        if long_conversations > 3:
            score += 25
            factors.append("Conversations approfondies")
        
        # Opportunités mentionnées
        if 'opportunité' in str(interactions).lower() or 'projet' in str(interactions).lower():
            score += 25
            factors.append("Opportunités de collaboration")
        
        # Classification
        if score >= 70:
            level = "high"
            recommendation = "Contact hautement prioritaire - maintenir contact régulier"
        elif score >= 40:
            level = "medium"
            recommendation = "Contact important - suivre périodiquement"
        else:
            level = "low"
            recommendation = "Contact à cultiver selon opportunités"
        
        return {
            "importance_score": score,
            "priority_level": level,
            "factors": factors,
            "recommendation": recommendation
        }
    
    # Méthodes mock pour fonctionnement sans API
    def _mock_analysis(self) -> Dict:
        return {
            "key_points": [
                "Discussion sur opportunités de collaboration",
                "Échange d'expertise dans le domaine",
                "Planification de prochaines étapes"
            ],
            "opportunities": [
                "Projet commun potentiel",
                "Partage de réseau professionnel"
            ],
            "cooperation_model": "Partenariat stratégique basé sur expertise complémentaire",
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
                "État d'avancement des projets actuels",
                "Nouvelles opportunités de collaboration",
                "Mise à jour sur le secteur"
            ],
            "questions": [
                "Quels sont vos principaux défis actuellement?",
                "Comment puis-je vous aider?",
                "Quelles sont vos priorités pour les prochains mois?"
            ],
            "value_propositions": [
                "Expertise complémentaire",
                "Réseau professionnel étendu",
                "Expérience dans le domaine"
            ],
            "objections": {
                "Manque de temps": "Proposer format court et ciblé",
                "Budget limité": "Commencer par collaboration exploratoire"
            },
            "closing": "Excellent échange! Planifions notre prochain point dans 2 semaines?",
            "follow_up": [
                "Envoyer résumé de la conversation",
                "Partager ressources mentionnées",
                "Calendrier RDV de suivi"
            ]
        }
    
    def _mock_actions(self) -> List[Dict]:
        return [
            {
                "action": "Envoyer présentation du projet",
                "responsible": "user",
                "deadline": "3 jours",
                "priority": "high",
                "status": "pending"
            },
            {
                "action": "Organiser réunion avec l'équipe",
                "responsible": "both",
                "deadline": "1 semaine",
                "priority": "medium",
                "status": "pending"
            }
        ]
    
    def _mock_summary(self, contact_name: str) -> str:
        return f"""
Résumé de la Conversation avec {contact_name}

**Contexte:**
Réunion exploratoire pour discuter d'opportunités de collaboration professionnelle.

**Sujets Principaux:**
- Présentation des activités respectives
- Identification de synergies potentielles
- Discussion sur les défis du secteur

**Décisions Prises:**
- Poursuivre les échanges sur base régulière
- Explorer opportunités de projet commun

**Actions Convenues:**
- Partage de documentation pertinente
- Planification d'un prochain point dans 2 semaines

**Prochaines Étapes:**
Maintenir la dynamique d'échange et concrétiser les pistes identifiées.
"""


# Fonction helper pour utiliser le service
def get_ai_service() -> AIService:
    """Retourne une instance du service IA"""
    return AIService()