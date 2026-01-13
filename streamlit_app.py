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
load_dotenv()  # charge le fichier .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==============================
# Fichiers de stockage local (simulation DB)
# ==============================
DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "contacts": {}, "messages": {}}, f, indent=4)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==============================
# Service IA
# ==============================
class AIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY

    def _mock_analysis(self):
        return {
            "key_points": ["Discussion sur opportunités", "Échange d'expertise", "Planification"],
            "opportunities": ["Projet commun", "Partage de réseau"],
            "cooperation_model": "Partenariat stratégique",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 75,
            "priority_level": "medium",
            "next_actions": ["Appel suivi", "Partager docs", "Introduire contacts"],
            "red_flags": [],
            "strengths": ["Communication claire", "Compétences complémentaires"]
        }

    def analyze_conversation(self, conversation_text: str, contact_name: str):
        if not AI_ANALYSIS_ENABLED or not self.api_key:
            return self._mock_analysis()

        prompt = f"""
Analyse cette conversation professionnelle avec {contact_name}.
Conversation:
{conversation_text}
Fournis une analyse structurée en JSON avec:
key_points, opportunities, cooperation_model, credibility_score,
usefulness_score, success_probability, priority_level, next_actions,
red_flags, strengths
Réponds uniquement en JSON.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            content = response.choices[0].message.content.strip()
            # Nettoyage JSON code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"Erreur API OpenAI: {e}")
            return self._mock_analysis()

# ==============================
# Streamlit Interface
# ==============================
st.set_page_config(page_title="Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - Network Pro")

ai_service = AIService()
data = load_data()

# ------------------------------
# Login / Inscription
# ------------------------------
auth_container = st.container()
with auth_container:
    st.subheader("Connexion / Inscription")
    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input("Nom d'utilisateur", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter", key="login_btn"):
            user = next((u for u in data["users"] if u["username"] == username and u["password"] == password), None)
            if user:
                st.success(f"Bienvenue {username} !")
                st.session_state["user"] = username
            else:
                st.warning("Utilisateur ou mot de passe incorrect")

    with col2:
        new_user = st.text_input("Nouvel utilisateur", key="signup_user")
        new_pass = st.text_input("Mot de passe", type="password", key="signup_pass")
        if st.button("S'inscrire", key="signup_btn"):
            if any(u["username"] == new_user for u in data["users"]):
                st.warning("Nom déjà utilisé")
            else:
                data["users"].append({"username": new_user, "password": new_pass})
                save_data(data)
                st.success(f"Utilisateur {new_user} créé !")

# ------------------------------
# Dashboard principal
# ------------------------------
if "user" in st.session_state:
    user = st.session_state["user"]
    st.header(f"Dashboard de {user}")

    dash_container = st.container()

    with dash_container:
        # Ajouter un contact
        st.subheader("Contacts")
        new_contact = st.text_input("Nom du contact", key="contact_name")
        contact_email = st.text_input("Email", key="contact_email")
        contact_domain = st.text_input("Domaine", key="contact_domain")
        contact_topic = st.text_input("Sujet abordé", key="contact_topic")
        contact_occasion = st.text_input("Occasion", key="contact_occasion")

        if st.button("Ajouter contact", key="add_contact"):
            contact_id = f"{user}_{new_contact}"
            if user not in data["contacts"]:
                data["contacts"][user] = {}
            data["contacts"][user][contact_id] = {
                "name": new_contact,
                "email": contact_email,
                "domain": contact_domain,
                "topic": contact_topic,
                "occasion": contact_occasion
            }
            if contact_id not in data["messages"]:
                data["messages"][contact_id] = []
            save_data(data)
            st.success(f"Contact {new_contact} ajouté !")

        # Liste des contacts
        st.subheader("Liste des contacts")
        if user in data["contacts"]:
            for cid, c in data["contacts"][user].items():
                st.write(f"{c['name']} | {c['email']} | {c['domain']}")
                # Lancer discussion
                if st.button(f"Chat avec {c['name']}", key=f"chat_{cid}"):
                    st.session_state["current_chat"] = cid

    # ------------------------------
    # Chat / Analyse conversation
    # ------------------------------
    if "current_chat" in st.session_state:
        chat_id = st.session_state["current_chat"]
        st.subheader(f"Discussion avec {data['contacts'][user][chat_id]['name']}")
        chat_input = st.text_area("Votre message", key=f"msg_input_{chat_id}")
        if st.button("Envoyer", key=f"send_{chat_id}"):
            message = {
                "from": user,
                "to": data["contacts"][user][chat_id]["name"],
                "text": chat_input,
                "timestamp": datetime.now().isoformat()
            }
            data["messages"][chat_id].append(message)
            save_data(data)
            st.success("Message envoyé !")
            chat_input = ""

        # Afficher l'historique
        st.subheader("Historique")
        for msg in data["messages"][chat_id]:
            st.write(f"{msg['timestamp']} | {msg['from']} -> {msg['to']}: {msg['text']}")

        # Analyse IA
        if st.button("Analyser cette conversation", key=f"analyze_{chat_id}"):
            conversation_text = "\n".join(msg["text"] for msg in data["messages"][chat_id])
            result = ai_service.analyze_conversation(conversation_text, data["contacts"][user][chat_id]["name"])
            st.subheader("Analyse IA")
            st.json(result)