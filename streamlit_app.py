# streamlit_app.py
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

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==============================
# Service IA
# ==============================
class AIService:
    """Service d'analyse IA des conversations"""
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY

    def _mock_analysis(self):
        return {
            "key_points": ["Discussion sur opportunités", "Échange d'expertise", "Prochaines étapes"],
            "opportunities": ["Projet commun", "Partage de réseau"],
            "cooperation_model": "Partenariat stratégique",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Appel de suivi", "Partager docs", "Introduire contacts"],
            "red_flags": [],
            "strengths": ["Communication claire", "Intérêts alignés"]
        }

    def analyze_conversation(self, conversation_text: str, contact_name: str):
        if not AI_ANALYSIS_ENABLED or not self.api_key:
            return self._mock_analysis()
        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}.
Conversation: {conversation_text}
Fournis une analyse JSON:
- key_points
- opportunities
- cooperation_model
- credibility_score
- usefulness_score
- success_probability
- priority_level
- next_actions
- red_flags
- strengths
Répond uniquement en JSON.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            if "```" in content:
                content = content.split("```")[-2].strip()
            return json.loads(content)
        except Exception as e:
            print(f"Erreur API OpenAI: {e}")
            return self._mock_analysis()

ai_service = AIService()

# ==============================
# Stockage local (JSON)
# ==============================
DATA_FILE = "data/messages.json"
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": {}, "messages": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==============================
# Streamlit Interface
# ==============================
st.set_page_config(page_title="Network", page_icon="🤝", layout="wide")

st.title("🤝 Network - Chat Pro sécurisé")

# ------------------------------
# Connexion / Inscription
# ------------------------------
data = load_data()
if "user" not in st.session_state:
    st.session_state.user = None

auth_option = st.sidebar.selectbox("Connexion / Inscription", ["Connexion", "Inscription"])
username = st.sidebar.text_input("Nom d'utilisateur")
password = st.sidebar.text_input("Mot de passe", type="password")

if auth_option == "Inscription":
    if st.sidebar.button("S'inscrire"):
        if username in data["users"]:
            st.sidebar.error("Nom déjà utilisé")
        else:
            data["users"][username] = {"password": password, "contacts": [], "created_at": str(datetime.now())}
            save_data(data)
            st.sidebar.success("Inscription réussie")
elif auth_option == "Connexion":
    if st.sidebar.button("Se connecter"):
        user = data["users"].get(username)
        if user and user["password"] == password:
            st.session_state.user = username
            st.sidebar.success(f"Connecté : {username}")
        else:
            st.sidebar.error("Nom ou mot de passe incorrect")

# ------------------------------
# Chat principal
# ------------------------------
if st.session_state.user:
    st.subheader(f"Bienvenue, {st.session_state.user}")
    # Sélection du contact
    contacts = list(data["users"].keys())
    contacts.remove(st.session_state.user)
    contact = st.selectbox("Choisir un contact", contacts)

    # Affichage messages
    st.markdown("### Conversation")
    conversation = [m for m in data["messages"] if
                    (m["sender"] == st.session_state.user and m["receiver"] == contact) or
                    (m["sender"] == contact and m["receiver"] == st.session_state.user)]
    for msg in conversation:
        st.write(f"**{msg['sender']}**: {msg['content']} ({msg['timestamp']})")

    # Nouveau message
    new_msg = st.text_input("Votre message")
    if st.button("Envoyer"):
        if new_msg.strip() != "":
            data["messages"].append({
                "sender": st.session_state.user,
                "receiver": contact,
                "content": new_msg,
                "timestamp": str(datetime.now())
            })
            save_data(data)
            st.experimental_rerun()

    # Analyse IA
    if st.button("Analyser cette conversation"):
        if conversation:
            full_text = "\n".join([m["content"] for m in conversation])
            analysis = ai_service.analyze_conversation(full_text, contact)
            st.markdown("### Analyse IA")
            st.json(analysis)