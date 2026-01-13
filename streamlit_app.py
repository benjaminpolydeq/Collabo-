# streamlit_app.py
import os
import json
import streamlit as st
from dotenv import load_dotenv
from ai_service import AIService
from user_service import UserService
from datetime import datetime

# Load env
load_dotenv()
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Network", page_icon="📱", layout="wide")

user_service = UserService()
ai_service = AIService()

# --- Authentification ---
st.sidebar.title("Connexion / Inscription")
auth_mode = st.sidebar.radio("Mode", ["Connexion", "Inscription"])

if auth_mode == "Inscription":
    username = st.sidebar.text_input("Nom")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("S'inscrire"):
        ok, msg = user_service.register_user(username, email, password)
        st.sidebar.success(msg)
else:
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Se connecter"):
        ok, user = user_service.login_user(email, password)
        if ok:
            st.session_state.user = user
            st.sidebar.success(f"Connecté: {user['username']}")
        else:
            st.sidebar.error(user)

# --- Main Interface ---
if "user" in st.session_state:
    st.title(f"📱 Network - Bienvenue {st.session_state.user['username']}")
    
    st.header("Ajouter / Analyser une conversation")
    with st.form("conversation_form"):
        contact_name = st.text_input("Nom du contact")
        contact_email = st.text_input("Email / Contact")
        contact_domain = st.text_input("Domaine")
        contact_occasion = st.text_input("Occasion")
        contact_topics = st.text_area("Sujets abordés")
        conversation_text = st.text_area("Texte de la conversation")
        meeting_datetime = st.datetime_input("Date & Heure du rendez-vous")
        submitted = st.form_submit_button("Enregistrer et analyser")

        if submitted:
            contact_info = {
                "name": contact_name,
                "email": contact_email,
                "domain": contact_domain,
                "occasion": contact_occasion,
                "topics": contact_topics,
                "meeting_datetime": str(meeting_datetime)
            }
            result = ai_service.analyze_conversation(conversation_text, contact_info)
            # Save user data
            user = st.session_state.user
            filename = f"{DATA_DIR}/{user['username']}_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump({"user": user['username'], "contact_info": contact_info,
                           "conversation": conversation_text, "analysis": result}, f, indent=2)
            st.success("Conversation enregistrée et analysée !")
            st.json(result)

    # Historique
    st.header("Historique des conversations")
    files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith(st.session_state.user['username'])],
                   reverse=True)
    for f in files:
        with open(f"{DATA_DIR}/{f}") as jf:
            data = json.load(jf)
            st.markdown(f"**{data['contact_info']['name']}** - {data['contact_info']['meeting_datetime']}")
            if st.button(f"Voir détails: {f}"):
                st.json(data)