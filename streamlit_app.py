# streamlit_app.py
import os, json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
import qrcode
from ai_service import AIService  # ton service IA existant

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
AI_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

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

data = load_data()

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
        contacts[idx]["favorite"] = not contacts[idx]["favorite"]
        save_data(data)

def login():
    u = st.session_state.input_user
    p = st.session_state.input_pass
    user = get_user(u)
    if user and user["password"] == p:
        st.session_state.logged_in = True
        st.session_state.username = u

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
    if AI_ENABLED and OPENAI_API_KEY:
        ai = AIService(api_key=OPENAI_API_KEY)
        return ai.analyze(message)
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
# CONTACTS
# =============================
if st.session_state.page == "Contacts":
    st.subheader("📇 Contacts")
    contacts = get_contacts(st.session_state.username)
    MAX = 10
    for i in range(MAX):
        col1, col2, col3 = st.columns([0.6,0.1,0.3])
        if i < len(contacts):
            contact = contacts[i]
            col1.write(contact["name"])
            col2.button("★" if contact.get("favorite") else "☆", key=f"fav_{i}", on_click=toggle_fav, args=(i,))
            buf = generate_qr(contact["name"])
            col3.image(buf, width=80)
        else:
            col1.write("")
            col2.write("")
            col3.write("")

# =============================
# MESSAGES
# =============================
if st.session_state.page == "Messages":
    st.subheader("💬 Messages")
    contacts = get_contacts(st.session_state.username)
    MAX = 5
    for i in range(MAX):
        col1, col2 = st.columns([0.7,0.3])
        if i < len(contacts):
            contact = contacts[i]
            m_placeholder = st.empty()
            with m_placeholder:
                st.write(f"Messages avec {contact['name']}")
                msg_input = st.text_input(f"Envoyer à {contact['name']}", key=f"msg_input_{i}")
                st.button("Envoyer", key=f"send_{i}", on_click=send_message, args=(contact["name"], msg_input))
        else:
            col1.write("")
            col2.write("")

# =============================
# IA
# =============================
if st.session_state.page == "IA":
    st.subheader("🤖 Analyse IA")
    msg_input = st.text_area("Texte à analyser", key="ai_input")
    if st.button("Analyser"):
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
    st.write(f"Total contacts: {total_contacts}")
    st.write(f"Total messages envoyés: {total_messages}")