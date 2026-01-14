""" Collabo - Application de Networking Intelligent Version finale stable """

import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from ai_service import AIService
import qrcode
from io import BytesIO

# ==============================
# Configuration de la page
# ==============================
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# CSS personnalisé
# ==============================
st.markdown("""
<style>
.main-header { background: linear-gradient(135deg, #2E3440 0%, #5E81AC 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
.contact-card { background: white; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 4px solid #5E81AC; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.online-badge { background: #A3BE8C; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
.offline-badge { background: #BF616A; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
.favorite-star { color: #EBCB8B; font-size: 1.2em; }
.message-sent { background: #5E81AC; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 70%; margin-left: auto; }
.message-received { background: #ECEFF4; color: #2E3440; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 70%; }
.stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.stat-number { font-size: 2em; font-weight: bold; color: #5E81AC; }
</style>
""", unsafe_allow_html=True)

# ==============================
# Charger variables d'environnement
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

# ==============================
# Initialiser le service IA
# ==============================
try:
    ai = AIService(api_key=OPENAI_API_KEY)
except:
    ai = None
    st.warning("Service IA non disponible - Continuez sans analyse IA")

# ==============================
# Fichier de données
# ==============================
DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": [
                {"username": "alice", "password": "pass123", "email": "alice@example.com", "created_at": str(datetime.now()), "online": True},
                {"username": "bob", "password": "pass123", "email": "bob@example.com", "created_at": str(datetime.now()), "online": False}
            ],
            "contacts": [
                {"owner": "alice", "contact_name": "bob", "favorite": True, "online": False, "created_at": str(datetime.now())}
            ],
            "messages": [
                {"sender": "alice", "receiver": "bob", "text": "Salut Bob !", "timestamp": str(datetime.now()), "read": False}
            ],
            "invitations": []
        }, f, indent=4)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ==============================
# Fonctions utilitaires
# ==============================
def get_user(username):
    return next((u for u in data["users"] if u["username"] == username), None)

def get_contacts(username):
    return [c for c in data["contacts"] if c["owner"] == username]

def get_messages(user1, user2):
    return sorted(
        [m for m in data["messages"]
         if (m["sender"] == user1 and m["receiver"] == user2)
         or (m["sender"] == user2 and m["receiver"] == user1)],
        key=lambda x: x["timestamp"]
    )

def count_unread_messages(username):
    return len([m for m in data["messages"]
                if m["receiver"] == username and not m.get("read", False)])

def generate_qr_code(username):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    invite_data = f"collabo://add/{username}"
    qr.add_data(invite_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def toggle_favorite(owner, contact_name):
    for c in data["contacts"]:
        if c["owner"] == owner and c["contact_name"] == contact_name:
            c["favorite"] = not c.get("favorite", False)
            break
    save_data(data)

def update_online_status(username, status):
    user = get_user(username)
    if user:
        user["online"] = status
        save_data(data)

# ==============================
# Sidebar Authentification
# ==============================
if "username" not in st.session_state:
    st.markdown('<div class="main-header"><h1>🤝 Collabo</h1><p>Networking Intelligent & Sécurisé</p></div>', unsafe_allow_html=True)
    
    st.sidebar.header("🔐 Authentification")
    auth_mode = st.sidebar.radio("Mode", ["Connexion", "Inscription"], key="auth_mode")
    username_input = st.sidebar.text_input("👤 Utilisateur", key="username_input")
    password_input = st.sidebar.text_input("🔑 Mot de passe", type="password", key="password_input")

    if auth_mode == "Inscription":
        email_input = st.sidebar.text_input("📧 Email (optionnel)", key="email_input")
        st.sidebar.button("✅ S'inscrire", key="btn_register",
                          on_click=lambda: register_user(username_input, password_input, email_input))
    else:
        st.sidebar.button("🚀 Se connecter", key="btn_login",
                          on_click=lambda: login_user(username_input, password_input))

    st.info("👋 Bienvenue sur Collabo ! Connectez-vous ou créez un compte pour commencer.")

# ==============================
# Application principale
# ==============================
else:
    current_user = st.session_state["username"]
    st.success(f"✅ {current_user} connecté - toutes fonctionnalités disponibles")

    # Exemple stable de container pour contacts
    contacts_placeholder = st.container()
    with contacts_placeholder:
        st.subheader("📇 Mes contacts")
        user_contacts = get_contacts(current_user)
        for idx, contact in enumerate(user_contacts):
            key_fav = f"fav_{contact['contact_name']}_{idx}"
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(contact["contact_name"])
            with col2:
                st.button("★" if contact.get("favorite") else "☆",
                          key=key_fav,
                          on_click=toggle_favorite,
                          args=(current_user, contact["contact_name"]))

    # Placeholder pour messages
    messages_placeholder = st.container()
    with messages_placeholder:
        st.subheader("💬 Messages")
        # Ici on pourrait mettre boucle messages similaire

    # Placeholder pour dashboard / stats
    stats_placeholder = st.container()
    with stats_placeholder:
        st.subheader("📊 Statistiques")
        st.write("A compléter selon ton code actuel")