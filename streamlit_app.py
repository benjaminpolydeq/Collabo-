# streamlit_app.py
import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ai_service import AIService

# ==============================
# Charger les variables d'environnement
# ==============================
load_dotenv()  # charge .env

DATA_FILE = "data.json"
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# ==============================
# Helper pour charger et sauver data.json
# ==============================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==============================
# Authentification
# ==============================
def login_user(username, password):
    data = load_data()
    user = data["users"].get(username)
    if user and user["password"] == password:
        return user
    return None

def register_user(username, password, name, email, domain):
    data = load_data()
    if username in data["users"]:
        return False
    data["users"][username] = {
        "username": username,
        "password": password,
        "name": name,
        "email": email,
        "domain": domain,
        "contacts": [],
        "favorites": [],
        "messages": {},
        "appointments": []
    }
    save_data(data)
    return True

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - Réseau Professionnel Sécurisé")

if "username" not in st.session_state:
    st.session_state.username = None

# --- Connexion / Inscription ---
if st.session_state.username is None:
    st.subheader("Connexion")
    username = st.text_input("Utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        user = login_user(username, password)
        if user:
            st.session_state.username = username
            st.success(f"Connecté en tant que {user['name']}")
        else:
            st.error("Utilisateur ou mot de passe incorrect")

    st.markdown("---")
    st.subheader("Inscription")
    reg_username = st.text_input("Nouvel utilisateur", key="reg_user")
    reg_password = st.text_input("Mot de passe", type="password", key="reg_pass")
    reg_name = st.text_input("Nom complet", key="reg_name")
    reg_email = st.text_input("Email", key="reg_email")
    reg_domain = st.text_input("Domaine", key="reg_domain")
    if st.button("S'inscrire"):
        if register_user(reg_username, reg_password, reg_name, reg_email, reg_domain):
            st.success("Inscription réussie ! Connectez-vous ci-dessus.")
        else:
            st.error("Nom d'utilisateur déjà utilisé")

# --- Dashboard principal ---
else:
    data = load_data()
    user = data["users"][st.session_state.username]
    ai_service = AIService()

    st.sidebar.title(f"Bienvenue, {user['name']}")
    menu = st.sidebar.radio("Menu", ["Contacts", "Messages", "Agenda", "Analyse IA", "Déconnexion"])

    # -----------------------------
    # Contacts
    # -----------------------------
    if menu == "Contacts":
        st.header("Contacts")
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader("Liste de contacts")
            for contact_username in user["contacts"]:
                contact = data["users"][contact_username]
                online = st.checkbox("En ligne", value=True, key=f"online_{contact_username}", disabled=True)
                st.write(f"{contact['name']} ({contact['domain']})")
        with col2:
            st.subheader("Ajouter contact")
            new_contact = st.text_input("Nom utilisateur à ajouter")
            if st.button("Ajouter"):
                if new_contact in data["users"] and new_contact not in user["contacts"]:
                    user["contacts"].append(new_contact)
                    data["users"][st.session_state.username] = user
                    save_data(data)
                    st.success(f"{new_contact} ajouté à vos contacts")
                else:
                    st.error("Utilisateur inexistant ou déjà contact")

    # -----------------------------
    # Messages
    # -----------------------------
    elif menu == "Messages":
        st.header("Messagerie")
        selected_contact = st.selectbox("Choisir un contact", user["contacts"])
        if selected_contact:
            messages = user["messages"].get(selected_contact, [])
            for msg in messages:
                st.write(f"{msg['timestamp']} - **{msg['sender']}**: {msg['content']}")
            
            new_msg = st.text_area("Nouveau message")
            if st.button("Envoyer"):
                timestamp = datetime.now().isoformat(timespec="minutes")
                msg_dict = {"sender": st.session_state.username, "content": new_msg, "timestamp": timestamp, "read": False}
                messages.append(msg_dict)
                user["messages"][selected_contact] = messages
                data["users"][st.session_state.username] = user

                # Ajouter le message au contact aussi
                contact_user = data["users"][selected_contact]
                contact_messages = contact_user["messages"].get(st.session_state.username, [])
                contact_messages.append(msg_dict)
                contact_user["messages"][st.session_state.username] = contact_messages
                data["users"][selected_contact] = contact_user

                save_data(data)
                st.success("Message envoyé !")

    # -----------------------------
    # Agenda
    # -----------------------------
    elif menu == "Agenda":
        st.header("Agenda")
        for appt in user["appointments"]:
            st.write(f"{appt['datetime']} - {appt['title']} avec {appt['with']} (Rappel {appt['reminder_minutes']} min avant)")
        st.subheader("Ajouter rendez-vous")
        appt_title = st.text_input("Titre")
        appt_with = st.selectbox("Avec", user["contacts"])
        appt_datetime = st.datetime_input("Date et heure")
        appt_reminder = st.number_input("Rappel (minutes avant)", min_value=1, max_value=120, value=30)
        if st.button("Ajouter rendez-vous", key="add_appt"):
            user["appointments"].append({
                "title": appt_title,
                "with": appt_with,
                "datetime": appt_datetime.isoformat(),
                "reminder_minutes": appt_reminder
            })
            data["users"][st.session_state.username] = user
            save_data(data)
            st.success("Rendez-vous ajouté !")

    # -----------------------------
    # Analyse IA
    # -----------------------------
    elif menu == "Analyse IA":
        st.header("Analyse de conversation")
        contact_for_analysis = st.selectbox("Choisir un contact pour analyser la discussion", user["contacts"])
        conversation_text = st.text_area("Coller la conversation à analyser")
        if st.button("Analyser"):
            if conversation_text.strip():
                result = ai_service.analyze_conversation(conversation_text, contact_for_analysis)
                st.json(result)
            else:
                st.warning("Veuillez coller une conversation à analyser")

    # -----------------------------
    # Déconnexion
    # -----------------------------
    elif menu == "Déconnexion":
        st.session_state.username = None
        st.experimental_rerun()