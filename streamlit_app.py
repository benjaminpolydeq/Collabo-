# streamlit_app.py
import os
import streamlit as st
from ai_service import AIService

# ==============================
# Configuration Streamlit
# ==============================
st.set_page_config(page_title="Network - Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Network - Collabo (Agenda & IA)")

# ==============================
# Initialiser le service IA
# ==============================
ai = AIService()

# ==============================
# Formulaire de contact + conversation
# ==============================
st.sidebar.header("Nouvelle conversation")
contact_name = st.sidebar.text_input("Nom du contact")
contact_email = st.sidebar.text_input("Email")
contact_domain = st.sidebar.text_input("Domaine")
contact_occassion = st.sidebar.text_input("Occasion")
contact_topics = st.sidebar.text_area("Sujets abordés")
conversation_text = st.sidebar.text_area("Texte de la discussion")
meeting_datetime = st.sidebar.datetime_input("Date et heure du rendez-vous")

if st.sidebar.button("Analyser & Sauvegarder"):
    if contact_name.strip() == "" or conversation_text.strip() == "":
        st.warning("Veuillez renseigner le nom du contact et le texte de la conversation.")
    else:
        contact = {
            "name": contact_name,
            "email": contact_email,
            "domain": contact_domain,
            "occasion": contact_occassion,
            "topics": contact_topics,
            "meeting_datetime": meeting_datetime.isoformat() if meeting_datetime else None
        }
        with st.spinner("Analyse IA en cours..."):
            analysis = ai.analyze_conversation(conversation_text, contact_name)
            ai.save_conversation(contact, conversation_text, analysis)
        st.success("Analyse terminée et conversation sauvegardée !")
        st.json(analysis)

# ==============================
# Historique des conversations
# ==============================
st.header("Historique des conversations")
conversations = ai.load_conversations()
for entry in reversed(conversations):
    st.subheader(entry["contact"].get("name", "Contact inconnu"))
    st.write("**Email:**", entry["contact"].get("email", ""))
    st.write("**Domaine:**", entry["contact"].get("domain", ""))
    st.write("**Occasion:**", entry["contact"].get("occasion", ""))
    st.write("**Sujets abordés:**", entry["contact"].get("topics", ""))
    st.write("**Rendez-vous:**", entry["contact"].get("meeting_datetime", ""))
    st.write("**Conversation:**", entry["conversation"])
    st.write("**Analyse IA:**")
    st.json(entry["analysis"])