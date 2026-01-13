"""
Collabo - Application de Networking Intelligent
streamlit_app.py
"""

# ------------------------------
# Imports Python natifs
# ------------------------------
import os
import json
from datetime import datetime
from pathlib import Path

# ------------------------------
# Imports tiers
# ------------------------------
import streamlit as st
from cryptography.fernet import Fernet
from .services import AIService

# ------------------------------
# Configuration de la page (OBLIGATOIRE en tout premier)
# ------------------------------
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# CSS minimal pour style
# ------------------------------
st.markdown("""
<style>
    .stApp { max-width: 1400px; margin: 0 auto; }
    .contact-card { border:1px solid #E5E9F0; border-radius:10px; padding:15px; margin:5px 0; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Services : chiffrement et stockage
# ------------------------------
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
        f = Fernet(EncryptionService.get_key())
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        f = Fernet(EncryptionService.get_key())
        return f.decrypt(encrypted_data.encode()).decode()


class StorageService:
    DATA_DIR = Path("data")

    @classmethod
    def save_contacts(cls, contacts):
        cls.DATA_DIR.mkdir(exist_ok=True)
        data = json.dumps(contacts, ensure_ascii=False, indent=2)
        encrypted = EncryptionService.encrypt_data(data)
        (cls.DATA_DIR / "contacts.enc").write_text(encrypted)

    @classmethod
    def load_contacts(cls):
        file_path = cls.DATA_DIR / "contacts.enc"
        if file_path.exists():
            encrypted = file_path.read_text()
            decrypted = EncryptionService.decrypt_data(encrypted)
            return json.loads(decrypted)
        return []

    @classmethod
    def save_conversations(cls, conversations):
        cls.DATA_DIR.mkdir(exist_ok=True)
        data = json.dumps(conversations, ensure_ascii=False, indent=2)
        encrypted = EncryptionService.encrypt_data(data)
        (cls.DATA_DIR / "conversations.enc").write_text(encrypted)

    @classmethod
    def load_conversations(cls):
        file_path = cls.DATA_DIR / "conversations.enc"
        if file_path.exists():
            encrypted = file_path.read_text()
            decrypted = EncryptionService.decrypt_data(encrypted)
            return json.loads(decrypted)
        return {}

# ------------------------------
# Initialisation multi-utilisateur
# ------------------------------
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'users' not in st.session_state:
    st.session_state.users = ["Alice", "Bob", "Charlie"]  # Exemple simple multi-user

if 'contacts' not in st.session_state:
    st.session_state.contacts = StorageService.load_contacts()

if 'conversations' not in st.session_state:
    st.session_state.conversations = StorageService.load_conversations()

if 'current_contact' not in st.session_state:
    st.session_state.current_contact = None

# ------------------------------
# Sélection de l'utilisateur
# ------------------------------
st.sidebar.markdown("### 👤 Sélection Utilisateur")
st.session_state.current_user = st.sidebar.selectbox(
    "Utilisateur actif",
    st.session_state.users
)

# ------------------------------
# Navigation principale
# ------------------------------
st.sidebar.markdown("### 📱 Navigation")
page = st.sidebar.radio(
    "",
    ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
    label_visibility="collapsed"
)

# ------------------------------
# Instance AI Service
# ------------------------------
ai_service = AIService()

# ------------------------------
# Dashboard
# ------------------------------
if page == "🏠 Dashboard":
    st.markdown(f"# 🤝 Collabo - Tableau de Bord ({st.session_state.current_user})")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Contacts Totaux", len(st.session_state.contacts))
    with col2:
        st.metric("Conversations", len(st.session_state.conversations))

# ------------------------------
# Contacts
# ------------------------------
elif page == "👥 Contacts":
    st.markdown("## 👥 Gestion des Contacts")
    
    tab1, tab2 = st.tabs(["Liste des Contacts", "➕ Ajouter Contact"])
    
    with tab1:
        if st.session_state.contacts:
            for idx, contact in enumerate(st.session_state.contacts):
                with st.expander(f"{contact['name']} ({contact.get('domain','N/A')})"):
                    st.write(contact)
                    if st.button("💬 Chat", key=f"chat_{idx}"):
                        st.session_state.current_contact = contact
                        st.rerun()
        else:
            st.info("Aucun contact enregistré")
    
    with tab2:
        with st.form("new_contact"):
            name = st.text_input("Nom complet*")
            domain = st.text_input("Domaine*")
            email = st.text_input("Email")
            priority = st.selectbox("Priorité", ["low", "medium", "high"])
            submitted = st.form_submit_button("Ajouter")
            if submitted and name and domain:
                new_contact = {
                    'id': datetime.now().isoformat(),
                    'name': name,
                    'domain': domain,
                    'email': email,
                    'priority': priority,
                    'created_by': st.session_state.current_user
                }
                st.session_state.contacts.append(new_contact)
                StorageService.save_contacts(st.session_state.contacts)
                st.success("Contact ajouté !")
                st.rerun()

# ------------------------------
# Conversations
# ------------------------------
elif page == "💬 Conversations":
    st.markdown("## 💬 Messagerie Sécurisée")
    
    if st.session_state.contacts:
        contact_names = [c['name'] for c in st.session_state.contacts]
        selected_name = st.selectbox("Sélectionner un contact", contact_names)
        contact = next(c for c in st.session_state.contacts if c['name'] == selected_name)
        
        conv_key = f"{st.session_state.current_user}_{contact['id']}"
        if conv_key not in st.session_state.conversations:
            st.session_state.conversations[conv_key] = []
        
        # Affichage messages
        for msg in st.session_state.conversations[conv_key]:
            align = "🟢" if msg['sender'] == st.session_state.current_user else "⚪"
            st.write(f"{align} {msg['sender']}: {msg['text']} ({msg['timestamp']})")
        
        # Envoyer message
        with st.form("send_message", clear_on_submit=True):
            message = st.text_area("Votre message", height=100)
            send = st.form_submit_button("Envoyer")
            if send and message:
                new_msg = {
                    'sender': st.session_state.current_user,
                    'text': message,
                    'timestamp': datetime.now().strftime("%H:%M")
                }
                st.session_state.conversations[conv_key].append(new_msg)
                StorageService.save_conversations(st.session_state.conversations)
                
                # Analyse IA (optionnel)
                analysis = ai_service.analyze_conversation(
                    "\n".join([m['text'] for m in st.session_state.conversations[conv_key]]),
                    contact
                )
                st.json(analysis)
                st.rerun()

# ------------------------------
# Analytics
# ------------------------------
elif page == "📊 Analytics":
    st.markdown("## 📊 Analytics")
    st.write("Analyse multi-utilisateur disponible")
    
# ------------------------------
# Paramètres
# ------------------------------
elif page == "⚙️ Paramètres":
    st.markdown("## ⚙️ Paramètres")
    st.write("Configuration générale et sécurité")