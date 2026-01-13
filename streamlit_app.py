import os
import json
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from ai_service import AIService

# =========================
# Charger variables d'environnement
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# =========================
# Stockage local (mock DB)
# =========================
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
ai_service = AIService()

# =========================
# Streamlit config
# =========================
st.set_page_config(page_title="🤝 Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - Chat Professionnel et Agenda Intelligent")

# =========================
# Session utilisateur
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# Authentification
# -------------------------
if st.session_state.user is None:
    st.subheader("Connexion / Inscription")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connexion"):
            if username in data["users"] and data["users"][username]["password"] == password:
                st.session_state.user = username
                st.success(f"Bienvenue {username}")
                st.experimental_rerun()
            else:
                st.error("Utilisateur ou mot de passe invalide")
    with col2:
        if st.button("Inscription"):
            if username.strip() != "" and username not in data["users"]:
                data["users"][username] = {"password": password, "contacts": [], "messages": []}
                save_data(data)
                st.success("Utilisateur créé ! Connectez-vous.")
            else:
                st.error("Nom d'utilisateur déjà existant ou vide")

# -------------------------
# Interface principale
# -------------------------
else:
    st.sidebar.subheader(f"Utilisateur: {st.session_state.user}")
    user_data = data["users"][st.session_state.user]

    menu = st.sidebar.radio("Menu", ["Dashboard", "Mes Contacts", "Messages"])

    # -------------------------
    # Dashboard
    # -------------------------
    if menu == "Dashboard":
        st.header("Dashboard")
        online = [c['name'] for c in user_data["contacts"] if c.get("online")]
        st.info(f"Contacts en ligne: {', '.join(online) if online else 'Aucun'}")

    # -------------------------
    # Mes Contacts
    # -------------------------
    elif menu == "Mes Contacts":
        st.header("Mes Contacts")
        for c in user_data["contacts"]:
            st.write(f"- {c['name']} | {c.get('email','')} | {c.get('domain','')} | Favori: {c.get('favori', False)}")

        st.markdown("### Ajouter un contact")
        new_name = st.text_input("Nom du contact", key="add_name")
        new_email = st.text_input("Email", key="add_email")
        new_domain = st.text_input("Domaine", key="add_domain")
        new_occasion = st.text_input("Occasion", key="add_occ")
        new_topics = st.text_input("Sujets abordés", key="add_topics")
        if st.button("Ajouter Contact"):
            if new_name.strip() != "":
                user_data["contacts"].append({
                    "name": new_name,
                    "email": new_email,
                    "domain": new_domain,
                    "occasion": new_occasion,
                    "topics": new_topics,
                    "online": True,
                    "favori": False
                })
                save_data(data)
                st.success(f"Contact {new_name} ajouté !")
                st.experimental_rerun()

    # -------------------------
    # Messages / Chat
    # -------------------------
    elif menu == "Messages":
        st.header("Messages")
        if not user_data["contacts"]:
            st.warning("Ajoutez des contacts pour discuter")
        else:
            contact_selected = st.selectbox("Choisir un contact", [c['name'] for c in user_data["contacts"]])
            msg_input = st.text_input("Votre message", key="msg_input")
            if st.button("Envoyer"):
                user_data["messages"].append({
                    "to": contact_selected,
                    "from": st.session_state.user,
                    "text": msg_input,
                    "timestamp": str(datetime.now())
                })
                save_data(data)
                st.success("Message envoyé !")
            
            # Afficher la conversation
            conversation = [m for m in user_data["messages"] if m["to"] == contact_selected or m["from"] == contact_selected]
            for m in conversation:
                st.write(f"**{m['from']}**: {m['text']} ({m['timestamp']})")
            
            # Analyse IA
            if st.button("Analyser cette conversation"):
                conversation_text = "\n".join([m['text'] for m in conversation])
                result = ai_service.analyze_conversation(conversation_text, contact_selected)
                st.json(result)