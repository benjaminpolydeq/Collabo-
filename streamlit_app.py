"""
Collabo - Application de Networking Intelligent
app/main.py
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
/* --- styles inchangés, volontairement --- */
</style>
""", unsafe_allow_html=True)

# =========================================================
# SERVICES
# =========================================================

class EncryptionService:
    @staticmethod
    def get_key():
        key_file = Path("data/.key")
        key_file.parent.mkdir(exist_ok=True)
        if key_file.exists():
            return key_file.read_bytes()
        key = Fernet.generate_key()
        key_file.write_bytes(key)
        return key

    @staticmethod
    def encrypt_data(data: str) -> str:
        return Fernet(EncryptionService.get_key()).encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(data: str) -> str:
        return Fernet(EncryptionService.get_key()).decrypt(data.encode()).decode()


class StorageService:
    DATA_DIR = Path("data")

    @classmethod
    def save_contacts(cls, contacts):
        cls.DATA_DIR.mkdir(exist_ok=True)
        encrypted = EncryptionService.encrypt_data(
            json.dumps(contacts, ensure_ascii=False)
        )
        (cls.DATA_DIR / "contacts.enc").write_text(encrypted)

    @classmethod
    def load_contacts(cls):
        file = cls.DATA_DIR / "contacts.enc"
        if file.exists():
            return json.loads(
                EncryptionService.decrypt_data(file.read_text())
            )
        return []

    @classmethod
    def save_conversations(cls, conversations):
        cls.DATA_DIR.mkdir(exist_ok=True)
        encrypted = EncryptionService.encrypt_data(
            json.dumps(conversations, ensure_ascii=False)
        )
        (cls.DATA_DIR / "conversations.enc").write_text(encrypted)

    @classmethod
    def load_conversations(cls):
        file = cls.DATA_DIR / "conversations.enc"
        if file.exists():
            return json.loads(
                EncryptionService.decrypt_data(file.read_text())
            )
        return {}

# =========================================================
# SESSION STATE (AVANT TOUT UI)
# =========================================================

st.session_state.setdefault("contacts", StorageService.load_contacts())
st.session_state.setdefault("conversations", StorageService.load_conversations())
st.session_state.setdefault("current_contact_id", None)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="app-header">
  <div class="app-title">🤝 Collabo</div>
  <div class="app-subtitle">Plateforme de Networking Intelligent & Sécurisée</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    page = st.radio(
        "",
        ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
        key="main_navigation",
        label_visibility="collapsed"
    )

# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    st.metric("Contacts", len(st.session_state.contacts))
    st.metric("Conversations", len(st.session_state.conversations))

# =========================================================
# CONTACTS
# =========================================================

elif page == "👥 Contacts":
    st.markdown("## 👥 Contacts")

    tab_list, tab_add = st.tabs(["📋 Liste", "➕ Ajouter"])

    with tab_list:
        for contact in st.session_state.contacts:
            cid = contact["id"]
            with st.expander(f"👤 {contact['name']}"):
                st.write(contact)

                if st.button("💬 Chat", key=f"chat_{cid}"):
                    st.session_state.current_contact_id = cid

                if st.button("🗑️ Supprimer", key=f"del_{cid}"):
                    st.session_state.contacts = [
                        c for c in st.session_state.contacts if c["id"] != cid
                    ]
                    StorageService.save_contacts(st.session_state.contacts)

    with tab_add:
        with st.form("add_contact"):
            name = st.text_input("Nom")
            domain = st.text_input("Domaine")
            submitted = st.form_submit_button("Ajouter")

            if submitted and name and domain:
                st.session_state.contacts.append({
                    "id": datetime.now().isoformat(),
                    "name": name,
                    "domain": domain,
                    "created_at": datetime.now().isoformat()
                })
                StorageService.save_contacts(st.session_state.contacts)

# =========================================================
# CONVERSATIONS
# =========================================================

elif page == "💬 Conversations":
    st.markdown("## 💬 Conversations")

    if not st.session_state.contacts:
        st.info("Ajoutez un contact")
    else:
        contacts_map = {c["name"]: c for c in st.session_state.contacts}

        selected = st.radio(
            "",
            list(contacts_map.keys()),
            key="conversation_selector",
            label_visibility="collapsed"
        )

        contact = contacts_map[selected]
        cid = contact["id"]

        st.session_state.conversations.setdefault(cid, [])

        for msg in st.session_state.conversations[cid]:
            st.write(f"{msg['timestamp']} - {msg['text']}")

        with st.form("send_message", clear_on_submit=True):
            message = st.text_area("Message")
            send = st.form_submit_button("Envoyer")

            if send and message:
                st.session_state.conversations[cid].append({
                    "sender": "user",
                    "text": message,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                StorageService.save_conversations(st.session_state.conversations)

# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":
    st.markdown("## 📊 Analytics")
    st.write("Fonctionnel")

# =========================================================
# PARAMÈTRES
# =========================================================

elif page == "⚙️ Paramètres":
    st.markdown("## ⚙️ Paramètres")
    st.info("Collabo v1.0 — stable")