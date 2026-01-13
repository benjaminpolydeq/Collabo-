"""
Collabo - Application de Networking Intelligent
app/main.py
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet

# ------------------- CONFIG PAGE -------------------
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.set_option("runner.fastReruns", False)  # Évite les erreurs removeChild

# ------------------- CSS -------------------
st.markdown("""
<style>
:root {--primary-color: #2E3440; --secondary-color: #5E81AC; --accent-color: #88C0D0;
--background-color: #ECEFF4; --card-background: #FFFFFF; --text-color: #2E3440;
--success-color: #A3BE8C; --warning-color: #EBCB8B; --danger-color: #BF616A;}
.stApp {max-width:1400px; margin:0 auto;}
.professional-card {background:var(--card-background); border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px; border-left:4px solid var(--secondary-color);}
.app-header {background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); color:white; padding:30px; border-radius:12px; margin-bottom:30px; box-shadow:0 4px 12px rgba(0,0,0,0.15);}
.app-title {font-size:2.5rem; font-weight:700; margin-bottom:8px;}
.app-subtitle {font-size:1.1rem; opacity:0.95;}
.status-badge {display:inline-block; padding:6px 14px; border-radius:20px; font-size:0.85rem; font-weight:600; margin:4px;}
.badge-high {background-color:#BF616A20; color:#BF616A;}
.badge-medium {background-color:#EBCB8B20; color:#D08770;}
.badge-low {background-color:#A3BE8C20; color:#A3BE8C;}
.contact-card {background:white; border-radius:10px; padding:20px; margin:10px 0; border:1px solid #E5E9F0; transition: all 0.3s ease;}
.contact-card:hover {box-shadow:0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px);}
.contact-name {font-size:1.3rem; font-weight:600; color:var(--primary-color); margin-bottom:8px;}
.contact-detail {font-size:0.95rem; color:#4C566A; margin:4px 0;}
.stButton>button {border-radius:8px; font-weight:500; transition: all 0.3s ease;}
.message-bubble {padding:12px 16px; border-radius:12px; margin:8px 0; max-width:70%;}
.message-sent {background:linear-gradient(135deg, #5E81AC 0%, #81A1C1 100%); color:white; margin-left:auto;}
.message-received {background:#ECEFF4; color:var(--text-color);}
.metric-card {background:white; border-radius:10px; padding:20px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06);}
.metric-value {font-size:2.5rem; font-weight:700; color:var(--secondary-color);}
.metric-label {font-size:0.95rem; color:#4C566A; margin-top:8px;}
.css-1d391kg {background-color: var(--primary-color);}
.alert-info {background-color:#88C0D020; border-left:4px solid #88C0D0; padding:16px; border-radius:8px; margin:16px 0;}
</style>
""", unsafe_allow_html=True)

# ------------------- CLASSES -------------------
class EncryptionService:
    @staticmethod
    def get_key():
        key_file = Path("data/.key")
        key_file.parent.mkdir(exist_ok=True)
        if key_file.exists():
            return key_file.read_bytes()
        else:
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

# ------------------- SESSION -------------------
if 'contacts' not in st.session_state:
    st.session_state.contacts = StorageService.load_contacts()

if 'conversations' not in st.session_state:
    st.session_state.conversations = StorageService.load_conversations()

if 'current_contact' not in st.session_state:
    st.session_state.current_contact = None

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Utilisateur1"  # placeholder multi-user

if 'to_delete' not in st.session_state:
    st.session_state.to_delete = None

# ------------------- HEADER -------------------
st.markdown("""
<div class="app-header">
    <div class="app-title">🤝 Collabo</div>
    <div class="app-subtitle">Plateforme de Networking Intelligent & Sécurisée</div>
</div>
""", unsafe_allow_html=True)

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("### 📱 Navigation")
    page = st.radio(
        "",
        ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("### 📈 Statistiques")
    col1, col2 = st.columns(2)
    col1.metric("Contacts", len(st.session_state.contacts))
    col2.metric("Conversations", len(st.session_state.conversations))
    st.markdown("---")
    st.markdown("### 🔒 Sécurité")
    st.success("✓ Chiffrement actif")
    st.info("✓ Stockage local")
    st.info("✓ Zéro serveur externe")

# ------------------- DASHBOARD -------------------
if page == "🏠 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(st.session_state.contacts)}</div><div class="metric-label">Contacts Totaux</div></div>""", unsafe_allow_html=True)
    with col2:
        high_priority = sum(1 for c in st.session_state.contacts if c.get('priority') == 'high')
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{high_priority}</div><div class="metric-label">Haute Priorité</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{len(st.session_state.conversations)}</div><div class="metric-label">Conversations</div></div>""", unsafe_allow_html=True)
    with col4:
        upcoming = sum(1 for c in st.session_state.contacts if c.get('next_meeting'))
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{upcoming}</div><div class="metric-label">RDV à venir</div></div>""", unsafe_allow_html=True)

# ------------------- CONTACTS -------------------
elif page == "👥 Contacts":
    st.markdown("## 👥 Gestion des Contacts")
    tab1, tab2 = st.tabs(["📋 Liste des Contacts", "➕ Ajouter un Contact"])

    with tab1:
        if st.session_state.contacts:
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Rechercher", placeholder="Nom, domaine...")
            with col2:
                filter_priority = st.selectbox("Priorité", ["Toutes", "Haute", "Moyenne", "Basse"])
            with col3:
                filter_domain = st.selectbox("Domaine", ["Tous"] + list(set(c.get('domain', '') for c in st.session_state.contacts if c.get('domain'))))

            for contact in st.session_state.contacts:
                if search and search.lower() not in contact['name'].lower() and search.lower() not in contact.get('domain', '').lower():
                    continue
                if filter_priority != "Toutes" and contact.get('priority', '').lower() != filter_priority.lower():
                    continue
                if filter_domain != "Tous" and contact.get('domain', '') != filter_domain:
                    continue
                with st.expander(f"👤 {contact['name']} - {contact.get('domain', 'N/A')}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""**📧 Contact:** {contact.get('email', 'N/A')} | 📱 {contact.get('phone', 'N/A')}<br>**🏢 Domaine:** {contact.get('domain', 'N/A')}<br>**🤝 Occasion:** {contact.get('occasion', 'N/A')}<br>**💭 Sujets abordés:** {contact.get('topics', 'N/A')}<br>**📅 Prochain RDV:** {contact.get('next_meeting', 'Non défini')}<br>**📝 Prochaine action:** {contact.get('next_action', 'Aucune')}<br>**⭐ Priorité:** <span class="status-badge badge-{contact.get('priority', 'low')}">{contact.get('priority', 'low').upper()}</span>""", unsafe_allow_html=True)
                    with col2:
                        if st.button("💬 Chat", key=f"chat_{contact['id']}"):
                            st.session_state.current_contact = contact
                        if st.button("🗑️ Supprimer", key=f"del_{contact['id']}"):
                            st.session_state.to_delete = contact['id']

            # Suppression sécurisée après boucle
            if st.session_state.to_delete:
                st.session_state.contacts = [c for c in st.session_state.contacts if c["id"] != st.session_state.to_delete]
                StorageService.save_contacts(st.session_state.contacts)
                st.session_state.to_delete = None
                st.experimental_rerun()

    with tab2:
        with st.form("new_contact"):
            name = st.text_input("👤 Nom complet*")
            email = st.text_input("📧 Email")
            domain = st.text_input("🏢 Domaine d'activité*")
            phone = st.text_input("📱 Téléphone")
            occasion = st.text_input("🤝 Occasion de rencontre*")
            priority = st.selectbox("⭐ Priorité", ["low", "medium", "high"])
            topics = st.text_area("💭 Sujets abordés*")
            next_meeting = st.text_input("📅 Prochain RDV (facultatif)")
            next_action = st.text_area("📝 Prochaine action")
            submitted = st.form_submit_button("✅ Enregistrer le Contact")
            if submitted:
                if name and domain and occasion and topics:
                    new_contact = {
                        'id': datetime.now().isoformat(),
                        'name': name, 'email': email, 'phone': phone, 'domain': domain,
                        'occasion': occasion, 'topics': topics, 'next_meeting': next_meeting,
                        'next_action': next_action, 'priority': priority, 'created_at': datetime.now().isoformat()
                    }
                    st.session_state.contacts.append(new_contact)
                    StorageService.save_contacts(st.session_state.contacts)
                    st.success(f"✅ Contact {name} ajouté avec succès!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")