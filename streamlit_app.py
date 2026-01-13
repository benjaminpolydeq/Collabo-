import streamlit as st
from auth import login, register
from chat_store import add_message, get_conversation
from ai_service import AIService

st.set_page_config("Collabo", "🤝", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

# ---------- AUTH ----------
if not st.session_state.user:
    st.title("🤝 Collabo – Connexion")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        u = st.text_input("Utilisateur")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects")

    with tab2:
        u = st.text_input("Nouvel utilisateur")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Créer un compte"):
            if register(u, p):
                st.success("Compte créé, connectez-vous")
            else:
                st.error("Utilisateur existe déjà")

    st.stop()

# ---------- APP ----------
st.sidebar.success(f"Connecté : {st.session_state.user}")
contact = st.sidebar.text_input("Contact (username)")

if not contact:
    st.info("Entrez le nom d’un contact pour discuter")
    st.stop()

st.title(f"💬 Discussion avec {contact}")

messages = get_conversation(st.session_state.user, contact)

for m in messages:
    align = "user" if m["sender"] == st.session_state.user else "assistant"
    st.chat_message(align).write(m["content"])

msg = st.chat_input("Votre message")

if msg:
    add_message(st.session_state.user, contact, msg)
    st.rerun()

# ---------- IA ----------
st.divider()
st.subheader("🧠 Analyse IA de la discussion")

if st.button("Analyser la conversation"):
    ai = AIService()
    full_text = "\n".join(
        f"{m['sender']}: {m['content']}" for m in messages
    )
    result = ai.analyze_conversation(full_text, contact)
    st.json(result)