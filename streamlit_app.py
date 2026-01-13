import streamlit as st
from ai_service import AIService
from datetime import datetime
import json
import os

# ==============================
# Configuration Streamlit
# ==============================
st.set_page_config(page_title="Network", page_icon="📇", layout="wide")
st.title("📇 Network - Agenda & IA Conversation Analysis")

ai = AIService()

# Inputs utilisateur
contact_name = st.text_input("Nom du contact")
contact_domain = st.text_input("Domaine")
meeting_context = st.text_input("Occasion de rencontre")
topics = st.text_area("Sujets abordés")
conversation_text = st.text_area("Texte complet de la conversation")
meeting_time = st.date_input("Rendez-vous")
meeting_hour = st.time_input("Heure du rendez-vous")

if st.button("Analyser & Enregistrer"):
    if not contact_name or not conversation_text:
        st.warning("Nom du contact et conversation obligatoires.")
    else:
        with st.spinner("Analyse en cours..."):
            analysis = ai.analyze_conversation(conversation_text, contact_name)

        st.success("Analyse terminée !")
        st.json(analysis)

        # Sauvegarder localement
        os.makedirs("./data", exist_ok=True)
        filename = f"./data/{contact_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "contact_name": contact_name,
                "domain": contact_domain,
                "meeting_context": meeting_context,
                "topics": topics,
                "conversation": conversation_text,
                "meeting_datetime": f"{meeting_time} {meeting_hour}",
                "analysis": analysis
            }, f, ensure_ascii=False, indent=2)
        st.info(f"Conversation sauvegardée: {filename}")