# streamlit_app.py

import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from ai_service import AIService
from streamlit_autorefresh import st_autorefresh

# ==============================
# Charger les variables d'environnement
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# ==============================
# Initialiser le service IA
# ==============================
ai = AIService(api_key=OPENAI_API_KEY)

# ==============================
# Fichier de données
# ==============================
DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "contacts": [], "messages": []}, f, indent=4)

with open(DATA_FILE, "r") as f:
    data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==============================
# Fonctions utilitaires
# ==============================
def get_user(username):
    return next((u for u in data["users"] if u["username"] == username), None)

def get_contacts(username):
    return [c for c in data["contacts"] if c["owner"] == username]

def get_messages(user1, user2):
    return [m for m in data["messages"]
            if (m["sender"] == user1 and m["receiver"] == user2)
            or (m["sender"] == user2 and m["receiver"] == user1)]

# ==============================
# Authentification
# ==============================
st.sidebar.header("Connexion / Inscription")
auth_mode = st.sidebar.radio("Mode", ["Connexion", "Inscription"])
username = st.sidebar.text_input("Utilisateur")
password = st.sidebar.text_input("Mot de passe", type="password")

if auth_mode == "Inscription" and st.sidebar.button("S'inscrire"):
    if get_user(username):
        st.sidebar.warning("Utilisateur déjà existant !")
    else:
        data["users"].append({"username": username, "password": password})
        save_data()
        st.sidebar.success("Inscription réussie !")

elif auth_mode == "Connexion" and st.sidebar.button("Se connecter"):
    user = get_user(username)
    if user and user["password"] == password:
        st.session_state["username"] = username
        st.sidebar.success("Connecté !")
    else:
        st.sidebar.error("Utilisateur ou mot de passe incorrect !")

# ==============================
# Dashboard utilisateur
# ==============================
if "username" in st.session_state:
    current_user = st.session_state["username"]
    st.header(f"Bienvenue {current_user} !")

    # ------------------------------
    # Ajouter contact
    # ------------------------------
    st.subheader("Contacts")
    new_contact = st.text_input("Ajouter un contact (nom)", key="add_contact")
    if st.button("Ajouter Contact", key="btn_add_contact"):
        if new_contact.strip() != "" and not any(c["contact_name"]==new_contact and c["owner"]==current_user for c in data["contacts"]):
            data["contacts"].append({
                "owner": current_user,
                "contact_name": new_contact,
                "created_at": str(datetime.now()),
                "favorite": False,
                "online": True
            })
            save_data()
            st.success(f"{new_contact} ajouté !")

    # Liste contacts
    contacts = get_contacts(current_user)
    st.write("Vos contacts :", [c["contact_name"] for c in contacts])

    # ------------------------------
    # Sélection contact pour discussion
    # ------------------------------
    if contacts:
        st.subheader("Discussion avec un contact")
        selected_contact = st.selectbox("Choisir un contact", [c["contact_name"] for c in contacts], key="chat_contact")
        conversation_text = st.text_area("Message à envoyer", key="msg_text")
        if st.button("Envoyer message", key="send_msg"):
            if conversation_text.strip() != "":
                data["messages"].append({
                    "sender": current_user,
                    "receiver": selected_contact,
                    "text": conversation_text,
                    "timestamp": str(datetime.now())
                })
                save_data()
                st.success("Message envoyé !")

    # ------------------------------
    # Afficher conversation
    # ------------------------------
    st.subheader("Vos conversations")
    for c in contacts:
        st.markdown(f"**Conversation avec {c['contact_name']}**")
        msgs = get_messages(current_user, c["contact_name"])
        for m in msgs:
            st.write(f"{m['timestamp']} - {m['sender']}: {m['text']}")

    # ------------------------------
    # Analyse IA conversation
    # ------------------------------
    if contacts:
        st.subheader("Analyse IA d'une conversation")
        contact_for_analysis = st.selectbox("Choisir un contact pour analyser", [c["contact_name"] for c in contacts], key="analysis_contact")
        msgs_to_analyze = get_messages(current_user, contact_for_analysis)
        full_text = "\n".join([m["text"] for m in msgs_to_analyze])
        if st.button("Analyser cette conversation", key="analyze_btn"):
            with st.spinner("Analyse en cours..."):
                result = ai.analyze_conversation(full_text, contact_for_analysis)
            st.json(result)

    # ------------------------------
    # Notifications simples
    # ------------------------------
    st_autorefresh(interval=5000, key="autorefresh")
    new_msgs = [m for m in data["messages"] if m["receiver"]==current_user]
    if new_msgs:
        st.info(f"💬 Vous avez {len(new_msgs)} nouveau(x) message(s) !")