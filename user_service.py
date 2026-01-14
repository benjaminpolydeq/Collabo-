import os
import json
import sqlite3
import hashlib
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import openai

# ==============================
# CONFIG
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(
    page_title="🤝 Collabo",
    page_icon="🤝",
    layout="wide"
)

# ==============================
# DATABASE (LOCAL – PRIVÉ)
# ==============================
DB_FILE = "collabo.db"

def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

db = get_db()
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    content TEXT,
    timestamp TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    owner TEXT,
    name TEXT,
    domain TEXT,
    occasion TEXT,
    notes TEXT
)
""")

db.commit()

# ==============================
# AUTH
# ==============================
def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register(u, p):
    try:
        cur.execute("INSERT INTO users VALUES (?,?)", (u, hash_pwd(p)))
        db.commit()
        return True
    except:
        return False

def login(u, p):
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pwd(p)))
    return cur.fetchone() is not None

# ==============================
# AI SERVICE
# ==============================
class AIService:
    def analyze(self, text, contact):
        if not OPENAI_API_KEY or not AI_ANALYSIS_ENABLED:
            return self.mock()

        prompt = f"""
Analyse cette discussion professionnelle avec {contact}.
Retourne UNIQUEMENT du JSON avec :
key_points, opportunities, cooperation_model,
credibility_score, usefulness_score,
success_probability, priority_level, next_actions
"""
        try:
            r = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt + "\n\n" + text}],
                max_tokens=1200
            )
            return json.loads(r.choices[0].message.content)
        except:
            return self.mock()

    def mock(self):
        return {
            "key_points": ["Discussion stratégique"],
            "opportunities": ["Collaboration"],
            "cooperation_model": "Partenariat",
            "credibility_score": 8,
            "usefulness_score": 7,
            "success_probability": 70,
            "priority_level": "medium",
            "next_actions": ["Relancer", "Planifier RDV"]
        }

ai = AIService()

# ==============================
# SESSION
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None

# ==============================
# AUTH UI
# ==============================
if not st.session_state.user:
    st.title("🤝 Collabo – Connexion")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        u = st.text_input("Utilisateur", key="login_user")
        p = st.text_input("Mot de passe", type="password", key="login_pass")

        if st.button("Se connecter"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects")

    with tab2:
        u2 = st.text_input("Nouvel utilisateur", key="reg_user")
        p2 = st.text_input("Mot de passe", type="password", key="reg_pass")

        if st.button("Créer un compte"):
            if register(u2, p2):
                st.success("Compte créé")
            else:
                st.error("Utilisateur déjà existant")

    st.stop()

# ==============================
# MAIN APP
# ==============================
user = st.session_state.user
st.sidebar.success(f"Connecté : {user}")

menu = st.sidebar.radio(
    "Menu",
    ["💬 Chat", "👥 Contacts", "🧠 Analyse IA", "🚪 Déconnexion"]
)

# ==============================
# CHAT
# ==============================
if menu == "💬 Chat":
    st.header("💬 Discussion sécurisée")

    receiver = st.text_input("Contact")
    msg = st.text_area("Message")

    if st.button("Envoyer"):
        cur.execute(
            "INSERT INTO messages (sender,receiver,content,timestamp) VALUES (?,?,?,?)",
            (user, receiver, msg, datetime.now().isoformat())
        )
        db.commit()

    cur.execute("""
    SELECT sender, content, timestamp FROM messages
    WHERE (sender=? OR receiver=?)
    ORDER BY timestamp DESC
    """, (user, user))

    for s, c, t in cur.fetchall():
        st.markdown(f"**{s}** : {c}")

# ==============================
# CONTACTS
# ==============================
if menu == "👥 Contacts":
    st.header("👥 Réseau professionnel")

    name = st.text_input("Nom")
    domain = st.text_input("Domaine")
    occasion = st.text_input("Occasion")
    notes = st.text_area("Notes")

    if st.button("Ajouter"):
        cur.execute(
            "INSERT INTO contacts VALUES (?,?,?,?,?)",
            (user, name, domain, occasion, notes)
        )
        db.commit()

    cur.execute("SELECT name, domain, occasion FROM contacts WHERE owner=?", (user,))
    st.table(cur.fetchall())

# ==============================
# ANALYSE IA
# ==============================
if menu == "🧠 Analyse IA":
    st.header("🧠 Analyse de discussion")

    contact = st.text_input("Contact analysé", key="analysis_contact")
    text = st.text_area("Discussion", height=200)

    if st.button("Analyser"):
        with st.spinner("Analyse IA..."):
            result = ai.analyze(text, contact)
        st.json(result)

# ==============================
# LOGOUT
# ==============================
if menu == "🚪 Déconnexion":
    st.session_state.user = None
    st.rerun()