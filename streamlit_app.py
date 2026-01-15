# streamlit_app.py
import os, json
import streamlit as st
from datetime import datetime
from io import BytesIO
import qrcode
from dotenv import load_dotenv

# Optionnel : IA avancée (Transformers/Tokenizers)
try:
    from ai_service import AIService
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# =============================
# CONFIG PAGE
# =============================
st.set_page_config(
    page_title="Collabo",
    page_icon="🤝",
    layout="wide"
)

# =============================
# LOAD ENV
# =============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true" and AI_AVAILABLE

# =============================
# SESSION STATE INIT
# =============================
DEFAULT_STATE = {
    "initialized": True,
    "logged_in": False,
    "username": "",
    "page": "Dashboard",
    "auth_mode": "Connexion"
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# DATA
# =============================
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": [
                {"username": "alice", "password": "123", "online": True},
                {"username": "bob", "password": "123", "online": False}
            ],
            "contacts": [
                {"owner": "alice", "name": "bob", "favorite": True}
            ],
            "messages": []
        }, f, indent=4)

def load_data(): 
    with open(DATA_FILE) as f: 
        return json.load(f)

def save_data(d): 
    with open(DATA_FILE, "w") as f: 
        json.dump(d, f, indent=4)

# Charger les données UNE SEULE FOIS par session
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# =============================
# UTILITIES
# =============================
def get_user(u):
    return next((x for x in data["users"] if x["username"] == u), None)

def get_contacts(u):
    return [c for c in data["contacts"] if c["owner"] == u]

def get_messages(u1, u2):
    return sorted(
        [m for m in data["messages"] if (m["sender"]==u1 and m["receiver"]==u2) or (m["sender"]==u2 and m["receiver"]==u1)],
        key=lambda x: x["timestamp"]
    )

def toggle_fav(idx):
    contacts = get_contacts(st.session_state.username)
    if idx < len(contacts):
        contact_to_toggle = contacts[idx]
        # Trouver l'index dans data["contacts"]
        for c in data["contacts"]:
            if c["owner"] == st.session_state.username and c["name"] == contact_to_toggle["name"]:
                c["favorite"] = not c.get("favorite", False)
                break
        save_data(data)
        st.session_state.data = load_data()  # Recharger les données
        st.rerun()

def login():
    u = st.session_state.input_user
    p = st.session_state.input_pass
    user = get_user(u)
    if user and user["password"] == p:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()

def send_message(to_user, text):
    if text.strip() == "":
        return
    data["messages"].append({
        "sender": st.session_state.username,
        "receiver": to_user,
        "text": text,
        "timestamp": str(datetime.now())
    })
    save_data(data)
    st.session_state.data = load_data()
    st.rerun()

def generate_qr(username):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(f"collabo://add/{username}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def ai_analyze(message):
    if AI_ENABLED:
        try:
            ai = AIService(api_key=OPENAI_API_KEY)
            return ai.analyze(message)
        except Exception as e:
            return f"Erreur IA: {e}"
    return "IA désactivée"

# =============================
# SIDEBAR
# =============================
st.sidebar.title("🤝 Collabo")

st.sidebar.radio("Navigation", ["Dashboard","Contacts","Messages","IA","Stats"], key="page")
st.sidebar.radio("Mode", ["Connexion","Inscription"], key="auth_mode")

st.sidebar.text_input("Utilisateur", key="input_user")
st.sidebar.text_input("Mot de passe", type="password", key="input_pass")
st.sidebar.text_input("Email (optionnel)", key="input_email")

st.sidebar.button("Se connecter", on_click=login)

# =============================
# HEADER
# =============================
st.markdown("<h1 style='text-align:center'>🤝 Collabo</h1>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.info("Veuillez vous connecter")
    st.stop()

st.success(f"Connecté : {st.session_state.username}")

# =============================
# DASHBOARD
# =============================
if st.session_state.page == "Dashboard":
    st.subheader("📊 Tableau de bord")
    st.write(f"Bienvenue {st.session_state.username} !")

# =============================
# CONTACTS (DOM stable - CORRIGÉ)
# =============================
if st.session_state.page == "Contacts":
    st.subheader("📇 Contacts")
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("Aucun contact pour le moment")
    else:
        for i, contact in enumerate(contacts):
            with st.container():
                col1, col2, col3 = st.columns([0.6, 0.1, 0.3])
                with col1:
                    st.write(contact["name"])
                with col2:
                    st.button(
                        "★" if contact.get("favorite") else "☆",
                        key=f"fav_{contact['name']}_{i}",
                        on_click=toggle_fav,
                        args=(i,)
                    )
                with col3:
                    st.image(generate_qr(contact["name"]), width=80)

# =============================
# MESSAGES (DOM stable - CORRIGÉ)
# =============================
if st.session_state.page == "Messages":
    st.subheader("💬 Messages")
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("Aucun contact pour envoyer des messages")
    else:
        for i, contact in enumerate(contacts):
            with st.expander(f"💬 Conversation avec {contact['name']}", expanded=(i==0)):
                # Afficher l'historique
                messages = get_messages(st.session_state.username, contact["name"])
                if messages:
                    for msg in messages[-5:]:  # Afficher les 5 derniers messages
                        sender = "Vous" if msg["sender"] == st.session_state.username else contact["name"]
                        st.text(f"{sender}: {msg['text']}")
                else:
                    st.info("Aucun message")
                
                # Zone d'envoi
                with st.form(key=f"form_{contact['name']}_{i}"):
                    msg_input = st.text_input(f"Envoyer à {contact['name']}", key=f"msg_input_{i}")
                    submit = st.form_submit_button("Envoyer")
                    if submit and msg_input:
                        send_message(contact["name"], msg_input)

# =============================
# IA
# =============================
if st.session_state.page == "IA":
    st.subheader("🤖 Analyse IA")
    msg_input = st.text_area("Texte à analyser", key="ai_input")
    if st.button("Analyser"):
        with st.spinner("Analyse en cours..."):
            result = ai_analyze(msg_input)
            st.write(result)

# =============================
# STATS
# =============================
if st.session_state.page == "Stats":
    st.subheader("📊 Statistiques")
    contacts = get_contacts(st.session_state.username)
    total_contacts = len(contacts)
    total_messages = len([m for m in data["messages"] if m["sender"]==st.session_state.username])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total contacts", total_contacts)
    with col2:
        st.metric("Messages envoyés", total_messages)