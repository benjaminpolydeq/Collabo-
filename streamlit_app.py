"""
Collabo - Application de Networking Intelligent
Version Multi-utilisateur + IA
app/main.py
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

from services.ai_service import get_ai_service

# -----------------------------------
# Configuration page
# -----------------------------------
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# Data storage
# -----------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CONTACTS_FILE = DATA_DIR / "contacts.json"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

def load_json(file_path, default):
    if file_path.exists():
        return json.loads(file_path.read_text())
    return default

def save_json(file_path, data):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# Initialisation session
if 'contacts' not in st.session_state:
    st.session_state.contacts = load_json(CONTACTS_FILE, [])

if 'conversations' not in st.session_state:
    st.session_state.conversations = load_json(CONVERSATIONS_FILE, {})

if 'current_contact' not in st.session_state:
    st.session_state.current_contact = None

if 'current_user' not in st.session_state:
    st.session_state.current_user = "user_1"  # par défaut, gestion multi-user

# -----------------------------------
# Sidebar: navigation + utilisateur
# -----------------------------------
with st.sidebar:
    st.markdown("### 👤 Utilisateur")
    user_id = st.text_input("ID Utilisateur", value=st.session_state.current_user)
    st.session_state.current_user = user_id

    st.markdown("### 📱 Navigation")
    page = st.radio(
        "",
        ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
        label_visibility="collapsed"
    )

# -----------------------------------
# Header
# -----------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #2E3440 0%, #5E81AC 100%);
            color:white; padding:20px; border-radius:12px;">
    <h1>🤝 Collabo</h1>
    <p>Plateforme de Networking Intelligent & Sécurisée</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# AI Service Instance
# -----------------------------------
ai_service = get_ai_service(user_id=st.session_state.current_user, model_type="anthropic")

# -----------------------------------
# Dashboard
# -----------------------------------
if page == "🏠 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    st.markdown(f"- Nombre de contacts : {len(st.session_state.contacts)}")
    st.markdown(f"- Nombre de conversations : {len(st.session_state.conversations)}")

# -----------------------------------
# Contacts
# -----------------------------------
elif page == "👥 Contacts":
    st.markdown("## 👥 Gestion des Contacts")
    tab1, tab2 = st.tabs(["📋 Liste des Contacts", "➕ Ajouter un Contact"])

    with tab1:
        for idx, contact in enumerate(st.session_state.contacts):
            with st.expander(f"{contact['name']} ({contact.get('domain', 'N/A')})"):
                st.write(f"📧 {contact.get('email', '')} | 📱 {contact.get('phone', '')}")
                st.write(f"Occasion: {contact.get('occasion', '')}")
                st.write(f"Topics: {contact.get('topics', '')}")
                if st.button("🗑️ Supprimer", key=f"del_{idx}"):
                    st.session_state.contacts.pop(idx)
                    save_json(CONTACTS_FILE, st.session_state.contacts)
                    st.experimental_rerun()

    with tab2:
        with st.form("add_contact"):
            name = st.text_input("Nom complet*")
            email = st.text_input("Email")
            phone = st.text_input("Téléphone")
            domain = st.text_input("Domaine*")
            occasion = st.text_input("Occasion*")
            topics = st.text_area("Sujets abordés*")
            priority = st.selectbox("Priorité", ["low", "medium", "high"])
            submitted = st.form_submit_button("✅ Ajouter")

            if submitted:
                if name and domain and occasion and topics:
                    new_contact = {
                        "id": datetime.now().isoformat(),
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "domain": domain,
                        "occasion": occasion,
                        "topics": topics,
                        "priority": priority,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.contacts.append(new_contact)
                    save_json(CONTACTS_FILE, st.session_state.contacts)
                    st.success("Contact ajouté!")
                    st.experimental_rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")

# -----------------------------------
# Conversations
# -----------------------------------
elif page == "💬 Conversations":
    st.markdown("## 💬 Messagerie Sécurisée")

    if not st.session_state.contacts:
        st.info("Ajoutez des contacts pour commencer")
    else:
        col1, col2 = st.columns([1, 3])

        with col1:
            contact_names = [c['name'] for c in st.session_state.contacts]
            selected_contact_name = st.radio("Contacts", contact_names)
            contact = next(c for c in st.session_state.contacts if c['name'] == selected_contact_name)
            st.session_state.current_contact = contact

        with col2:
            contact_id = contact['id']
            if contact_id not in st.session_state.conversations:
                st.session_state.conversations[contact_id] = []

            # Affichage des messages
            for msg in st.session_state.conversations[contact_id]:
                align = "👉" if msg['sender'] == 'user' else "💬"
                st.write(f"{align} {msg['text']} ({msg['timestamp']})")

            # Envoi message
            with st.form("send_msg", clear_on_submit=True):
                message = st.text_area("Votre message", height=100)
                if st.form_submit_button("📤 Envoyer") and message:
                    msg_obj = {
                        "sender": "user",
                        "text": message,
                        "timestamp": datetime.now().strftime("%H:%M")
                    }
                    st.session_state.conversations[contact_id].append(msg_obj)
                    save_json(CONVERSATIONS_FILE, st.session_state.conversations)
                    st.experimental_rerun()

            # Bouton IA pour analyser la conversation
            if st.button("🤖 Analyser la conversation avec IA"):
                conversation_text = "\n".join([m['text'] for m in st.session_state.conversations[contact_id]])
                with st.spinner("Analyse en cours..."):
                    analysis = ai_service.analyze_conversation(conversation_text, contact)
                    st.markdown("### 📌 Insights IA")
                    st.json(analysis)

                    st.markdown("### 📝 Résumé de réunion")
                    summary = ai_service.generate_meeting_summary(conversation_text, contact['name'])
                    st.text(summary)

# -----------------------------------
# Analytics
# -----------------------------------
elif page == "📊 Analytics":
    st.markdown("## 📊 Analytics")
    st.info("Fonctionnalités d'analyse multi-utilisateur en préparation")

# -----------------------------------
# Paramètres
# -----------------------------------
elif page == "⚙️ Paramètres":
    st.markdown("## ⚙️ Paramètres")
    st.markdown(f"- Utilisateur actif : {st.session_state.current_user}")
    st.markdown("- Chiffrement des données locales et stockage sécurisé (bientôt intégré)")