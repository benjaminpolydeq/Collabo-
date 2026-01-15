# streamlit_app.py
import os, json
import streamlit as st
from datetime import datetime
from io import BytesIO
import time

# Import conditionnel
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# =============================
# CONFIG PAGE
# =============================
st.set_page_config(
    page_title="Collabo - Messagerie Intelligente",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# CUSTOM CSS
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}
[data-testid="stSidebar"] * { color: white !important; }

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 25px;
}

.message-sent {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 15px 15px 5px 15px;
    margin: 0.5rem 0;
    max-width: 70%;
    margin-left: auto;
}

.message-received {
    background: #f0f2f6;
    color: #333;
    padding: 1rem;
    border-radius: 15px 15px 15px 5px;
    margin: 0.5rem 0;
    max-width: 70%;
}
</style>
""", unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
DEFAULT_STATE = {
    "logged_in": False,
    "username": "",
    "page": "Dashboard"
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
                {"username": "alice", "password": "123", "online": True, "bio": "Développeuse passionnée"},
                {"username": "bob", "password": "123", "online": False, "bio": "Designer créatif"}
            ],
            "contacts": [
                {"owner": "alice", "name": "bob", "favorite": True}
            ],
            "messages": [],
            "ai_analyses": []
        }, f, indent=4)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=4)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# =============================
# AI SERVICE
# =============================
class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if AI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.enabled = False

    def analyze_sentiment(self, text):
        if not self.enabled:
            return {"sentiment": "neutre"}

ai_service = AIService()

# =============================
# UTILITIES
# =============================
def get_user(u):
    return next((x for x in data["users"] if x["username"] == u), None)

def get_contacts(u):
    return [c for c in data["contacts"] if c["owner"] == u]

def get_messages(u1, u2):
    return sorted(
        [m for m in data["messages"]
         if (m["sender"] == u1 and m["receiver"] == u2)
         or (m["sender"] == u2 and m["receiver"] == u1)],
        key=lambda x: x["timestamp"]
    )

def login():
    u = st.session_state.get("input_user", "")
    p = st.session_state.get("input_pass", "")
    user = get_user(u)
    if user and user["password"] == p:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()
    else:
        st.sidebar.error("Identifiants incorrects")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

def send_message(to_user, text):
    if not text.strip():
        return
    data["messages"].append({
        "sender": st.session_state.username,
        "receiver": to_user,
        "text": text,
        "timestamp": str(datetime.now())
    })
    save_data(data)
    st.session_state.data = load_data()

def add_contact():
    name = st.session_state.get("new_contact_name", "")
    if not get_user(name):
        st.error("Utilisateur inexistant")
        return
    data["contacts"].append({
        "owner": st.session_state.username,
        "name": name,
        "favorite": False
    })
    save_data(data)
    st.session_state.data = load_data()
    st.rerun()

# =============================
# SIDEBAR
# =============================
st.sidebar.markdown("### 🤝 Collabo")

if not st.session_state.logged_in:
    st.sidebar.text_input("Utilisateur", key="input_user")
    st.sidebar.text_input("Mot de passe", type="password", key="input_pass")
    st.sidebar.button("Connexion", on_click=login)
else:
    st.sidebar.success(st.session_state.username)
    st.sidebar.button("Déconnexion", on_click=logout)
    st.session_state.page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Contacts", "Messages"]
    )

# =============================
# MAIN
# =============================
if not st.session_state.logged_in:
    st.info("Veuillez vous connecter")
    st.stop()

# =============================
# DASHBOARD
# =============================
if st.session_state.page == "Dashboard":
    st.metric("👥 Contacts", len(get_contacts(st.session_state.username)))
    sent = len([m for m in data["messages"] if m["sender"] == st.session_state.username])
    received = len([m for m in data["messages"] if m["receiver"] == st.session_state.username])
    st.metric("📤 Envoyés", sent)
    st.metric("📥 Reçus", received)

# =============================
# CONTACTS
# =============================
elif st.session_state.page == "Contacts":
    st.text_input("Ajouter contact", key="new_contact_name")
    st.button("Ajouter", on_click=add_contact)

    for c in get_contacts(st.session_state.username):
        st.write(c["name"])

# =============================
# MESSAGES
# =============================
elif st.session_state.page == "Messages":
    contacts = get_contacts(st.session_state.username)

    for contact in contacts:
        messages = get_messages(st.session_state.username, contact["name"])

        with st.expander(f"💬 {contact['name']}"):
            for msg in messages:
                if msg["sender"] == st.session_state.username:
                    st.markdown(
                        f'<div class="message-sent">Vous : {msg["text"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="message-received">{msg["sender"]} : {msg["text"]}</div>',
                        unsafe_allow_html=True
                    )

            st.text_input("Message", key=f"msg_{contact['name']}")
            if st.button("Envoyer", key=f"send_{contact['name']}"):
                send_message(contact["name"], st.session_state[f"msg_{contact['name']}"])
                st.rerun()