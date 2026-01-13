import os
import json
import streamlit as st
from dotenv import load_dotenv
import openai
from datetime import datetime

# ==============================
# Charger les variables d'environnement
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# Configurer l’API OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==============================
# Service IA
# ==============================
class AIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY

    def _mock_analysis(self):
        return {"key_points": ["Discussion sur opportunités de collaboration"],
                "opportunities": ["Projet commun potentiel"],
                "cooperation_model": "Partenariat stratégique",
                "credibility_score": 8,
                "usefulness_score": 7,
                "success_probability": 75,
                "priority_level": "medium",
                "next_actions": ["Planifier un appel", "Partager documents", "Introduire contacts"],
                "red_flags": [],
                "strengths": ["Communication claire"]}

    def analyze_conversation(self, conversation_text, contact_name):
        if not AI_ANALYSIS_ENABLED or not self.api_key:
            return self._mock_analysis()
        prompt = f"Analyse cette conversation avec {contact_name}: {conversation_text}"
        # Ici, pour simplifier, on retourne mock
        return self._mock_analysis()

# ==============================
# Messages en mémoire (mock base)
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []  # {"from":username,"to":username,"text":...,"timestamp":...}

if "last_checked" not in st.session_state:
    st.session_state.last_checked = datetime.now()

# ==============================
# Streamlit Interface
# ==============================
st.set_page_config(page_title="Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - Chat & Analyse IA")

# ==============================
# Connexion / Utilisateur
# ==============================
if "username" not in st.session_state:
    st.session_state.username = st.text_input("Nom d'utilisateur pour cette session")
username = st.session_state.username

# ==============================
# Ajouter un nouveau message
# ==============================
st.subheader("Envoyer un message")
to_user = st.text_input("Destinataire")
msg_text = st.text_area("Message à envoyer")

if st.button("Envoyer"):
    if to_user.strip() and msg_text.strip():
        st.session_state.messages.append({
            "from": username,
            "to": to_user,
            "text": msg_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"Message envoyé à {to_user} ✅")
        msg_text = ""

# ==============================
# Afficher les messages entrants
# ==============================
st.subheader("Messages reçus")
for msg in st.session_state.messages:
    if msg["to"] == username:
        st.info(f"De {msg['from']} à {msg['to']} ({msg['timestamp']}): {msg['text']}")

# ==============================
# Notification visuelle de nouveaux messages
# ==============================
from streamlit_autorefresh import st_autorefresh

# Rafraîchir toutes les 5 secondes pour check nouveaux messages
count = st_autorefresh(interval=5000, key="refresh")

new_messages = [m for m in st.session_state.messages 
                if m["to"] == username and datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M:%S") > st.session_state.last_checked]

if new_messages:
    st.balloons()  # animation Streamlit fun
    st.toast(f"📩 {len(new_messages)} nouveau(x) message(s) reçu(s)!")  # Streamlit 1.29+ supporte st.toast
    st.session_state.last_checked = datetime.now()
