"""
Collabo - Application de Networking Intelligent
app/streamlit_app.py
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import os

# Import AI Service depuis la racine
from ai_service import AIService

# Configuration de la page
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé (reste inchangé, je l’ai conservé pour la lisibilité)
st.markdown("""
<style>
    :root { --primary-color: #2E3440; --secondary-color: #5E81AC; --accent-color: #88C0D0; --background-color: #ECEFF4; --card-background: #FFFFFF; --text-color: #2E3440; --success-color: #A3BE8C; --warning-color: #EBCB8B; --danger-color: #BF616A; }
    .main { background-color: var(--background-color); }
    .stApp { max-width: 1400px; margin: 0 auto; }
    .professional-card { background: var(--card-background); border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 4px solid var(--secondary-color); }
    .app-header { background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .app-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 8px; }
    .app-subtitle { font-size: 1.1rem; opacity: 0.95; }
    .status-badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin: 4px; }
    .badge-high { background-color: #BF616A20; color: #BF616A; }
    .badge-medium { background-color: #EBCB8B20; color: #D08770; }
    .badge-low { background-color: #A3BE8C20; color: #A3BE8C; }
    .contact-card { background: white; border-radius: 10px; padding: 20px; margin: 10px 0; border: 1px solid #E5E9F0; transition: all 0.3s ease; }
    .contact-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
    .contact-name { font-size: 1.3rem; font-weight: 600; color: var(--primary-color); margin-bottom: 8px; }
    .contact-detail { font-size: 0.95rem; color: #4C566A; margin: 4px 0; }
    .stButton>button { border-radius: 8px; font-weight: 500; transition: all 0.3s ease; }
    .message-bubble { padding: 12px 16px; border-radius: 12px; margin: 8px 0; max-width: 70%; }
    .message-sent { background: linear-gradient(135deg, #5E81AC 0%, #81A1C1 100%); color: white; margin-left: auto; }
    .message-received { background: #ECEFF4; color: var(--text-color); }
    .metric-card { background: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: var(--secondary-color); }
    .metric-label { font-size: 0.95rem; color: #4C566A; margin-top: 8px; }
    .css-1d391kg { background-color: var(--primary-color); }
    .alert-info { background-color: #88C0D020; border-left: 4px solid #88C0D0; padding: 16px; border-radius: 8px; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# Services
ai_service = AIService()  # instance de ton service IA

# Gestion du stockage (local JSON chiffré)
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

CONTACTS_FILE = DATA_DIR / "contacts.json"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

def load_json(file_path):
    if file_path.exists():
        return json.loads(file_path.read_text())
    return [] if "contacts" in str(file_path) else {}

def save_json(file_path, data):
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

# Initialisation session state
if "contacts" not in st.session_state:
    st.session_state.contacts = load_json(CONTACTS_FILE)
if "conversations" not in st.session_state:
    st.session_state.conversations = load_json(CONVERSATIONS_FILE)
if "current_contact" not in st.session_state:
    st.session_state.current_contact = None

# ---------------------
# UI Principal
# ---------------------
st.markdown("""
<div class="app-header">
    <div class="app-title">🤝 Collabo</div>
    <div class="app-subtitle">Plateforme de Networking Intelligent & Sécurisée</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📱 Navigation")
    page = st.radio(
        "",
        ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
        label_visibility="collapsed"
    )

# ---------------------
# Pages
# ---------------------
if page == "🏠 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    st.info("Dashboard en construction...")

elif page == "👥 Contacts":
    st.markdown("## 👥 Gestion des Contacts")
    st.info("Contacts en construction...")

elif page == "💬 Conversations":
    st.markdown("## 💬 Messagerie Sécurisée")
    st.info("Messagerie en construction...")

elif page == "📊 Analytics":
    st.markdown("## 📊 Analyses & Insights")
    st.info("Analytics en construction...")

elif page == "⚙️ Paramètres":
    st.markdown("## ⚙️ Paramètres")
    st.info("Paramètres en construction...")