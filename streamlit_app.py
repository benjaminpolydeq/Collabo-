import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from ai_service import AIService

# ==============================
# Charger les variables d'environnement
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"
DATA_FILE = "data.json"

# ==============================
# Initialiser le service IA
# ==============================
ai = AIService(api_key=OPENAI_API_KEY)

# ==============================
# Charger ou créer data.json
# ==============================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

# Initialisation des clés
data.setdefault("users", [])
data.setdefault("contacts", [])
data.setdefault("messages", [])

# ==============================
# Streamlit Interface
# ==============================
st.set_page_config(page_title="🤝 Collabo", page_icon="🤝", layout="wide")
st.title("🤝 Collabo - Network for Professionals")

# ==============================
# Barre latérale - Connexion / Inscription
# ==============================
st.sidebar.header("Connexion / Inscription")
menu = st.sidebar.selectbox("Menu", ["Connexion", "Inscription"])

current_user = None

# ------------------------------
# Inscription
# ------------------------------
if menu == "Inscription":
    new_user = st.sidebar.text_input("Nom d'utilisateur")
    password = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("S'inscrire"):
        if new_user.strip() == "" or password.strip() == "":
            st.sidebar.warning("Veuillez remplir tous les champs.")
        elif any(u.get("username") == new_user for u in data["users"]):
            st.sidebar.error("Nom d'utilisateur déjà existant.")
        else:
            user = {
                "username": new_user,
                "password": password,
                "contacts": [],
                "favorites": [],
                "online": True
            }
            data["users"].append(user)
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
            st.sidebar.success("Inscription réussie ! Connectez-vous maintenant.")

# ------------------------------
# Connexion
# ------------------------------
elif menu == "Connexion":
    username = st.sidebar.text_input("Nom d'utilisateur", key="login_user")
    password = st.sidebar.text_input("Mot de passe", type="password", key="login_pass")
    if st.sidebar.button("Se connecter"):
        user = next((u for u in data["users"] if u.get("username") == username and u.get("password") == password), None)
        if user:
            current_user = user
            st.sidebar.success(f"Connecté en tant que {username}")
            user["online"] = True
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        else:
            st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")

# ==============================
# Dashboard utilisateur
# ==============================
if current_user:
    st.subheader(f"Bienvenue {current_user['username']}")

    # ==============================
    # Section Contacts
    # ==============================
    st.markdown("### 📇 Contacts")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Ajouter un contact**")
        contact_username = st.text_input("Nom d'utilisateur du contact")
        if st.button("Ajouter contact"):
            contact_user = next((u for u in data["users"] if u.get("username") == contact_username), None)
            if contact_user:
                if contact_username not in current_user["contacts"]:
                    current_user["contacts"].append(contact_username)
                    with open(DATA_FILE, "w") as f:
                        json.dump(data, f, indent=4)
                    st.success(f"{contact_username} ajouté à vos contacts !")
                else:
                    st.info(f"{contact_username} est déjà dans vos contacts.")
            else:
                st.error("Utilisateur introuvable.")

    with col2:
        st.markdown("**Contacts en ligne**")
        online_contacts = [u for u in current_user["contacts"] if next((x for x in data["users"] if x.get("username") == u and x.get("online")), None)]
        st.write(online_contacts if online_contacts else "Aucun contact en ligne")

    # ==============================
    # Lancer une discussion
    # ==============================
    st.markdown("### 💬 Discussions")
    if current_user["contacts"]:
        chat_contact = st.selectbox("Choisir un contact", current_user["contacts"])
        message_text = st.text_area("Votre message")
        if st.button("Envoyer message"):
            if message_text.strip():
                msg = {
                    "from": current_user["username"],
                    "to": chat_contact,
                    "message": message_text,
                    "timestamp": time.time()
                }
                data["messages"].append(msg)
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                st.success("Message envoyé !")
    else:
        st.info("Ajoutez des contacts pour commencer à discuter.")

    # ==============================
    # Afficher les messages
    # ==============================
    st.markdown("### 📨 Messages")
    chat_history = [m for m in data["messages"] if m["from"] == current_user["username"] or m["to"] == current_user["username"]]
    for m in chat_history:
        sender = m["from"]
        recipient = m["to"]
        st.write(f"**{sender} → {recipient}:** {m['message']}")

    # ==============================
    # Analyse IA de la discussion
    # ==============================
    st.markdown("### 🤖 Analyse IA")
    if st.button("Analyser mes discussions"):
        if chat_history:
            all_text = "\n".join([m["message"] for m in chat_history])
            result = ai.analyze_conversation(all_text, current_user["username"])
            st.json(result)
        else:
            st.info("Aucune discussion à analyser.")