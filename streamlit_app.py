"""
Collabo - Application de Networking Intelligent
app/main.py
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import os
from cryptography.fernet import Fernet
import base64
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="Collabo - Networking Intelligent",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
st.markdown("""
<style>
    /* Thème principal */
    :root {
        --primary-color: #2E3440;
        --secondary-color: #5E81AC;
        --accent-color: #88C0D0;
        --background-color: #ECEFF4;
        --card-background: #FFFFFF;
        --text-color: #2E3440;
        --success-color: #A3BE8C;
        --warning-color: #EBCB8B;
        --danger-color: #BF616A;
    }
    
    /* Styles généraux */
    .main {
        background-color: var(--background-color);
    }
    
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Carte professionnelle */
    .professional-card {
        background: var(--card-background);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 4px solid var(--secondary-color);
    }
    
    /* En-tête */
    .app-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Badge de statut */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    
    .badge-high {
        background-color: #BF616A20;
        color: #BF616A;
    }
    
    .badge-medium {
        background-color: #EBCB8B20;
        color: #D08770;
    }
    
    .badge-low {
        background-color: #A3BE8C20;
        color: #A3BE8C;
    }
    
    /* Contact card */
    .contact-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #E5E9F0;
        transition: all 0.3s ease;
    }
    
    .contact-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .contact-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 8px;
    }
    
    .contact-detail {
        font-size: 0.95rem;
        color: #4C566A;
        margin: 4px 0;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* Messages */
    .message-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        max-width: 70%;
    }
    
    .message-sent {
        background: linear-gradient(135deg, #5E81AC 0%, #81A1C1 100%);
        color: white;
        margin-left: auto;
    }
    
    .message-received {
        background: #ECEFF4;
        color: var(--text-color);
    }
    
    /* Métriques */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--secondary-color);
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #4C566A;
        margin-top: 8px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--primary-color);
    }
    
    /* Alertes */
    .alert-info {
        background-color: #88C0D020;
        border-left: 4px solid #88C0D0;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# Classes de données
class EncryptionService:
    """Service de chiffrement local"""
    
    @staticmethod
    def get_key():
        """Génère ou récupère la clé de chiffrement"""
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
        """Chiffre les données"""
        f = Fernet(EncryptionService.get_key())
        return f.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Déchiffre les données"""
        f = Fernet(EncryptionService.get_key())
        return f.decrypt(encrypted_data.encode()).decode()

class StorageService:
    """Service de stockage local sécurisé"""
    
    DATA_DIR = Path("data")
    
    @classmethod
    def save_contacts(cls, contacts):
        """Sauvegarde les contacts de manière chiffrée"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        data = json.dumps(contacts, ensure_ascii=False, indent=2)
        encrypted = EncryptionService.encrypt_data(data)
        (cls.DATA_DIR / "contacts.enc").write_text(encrypted)
    
    @classmethod
    def load_contacts(cls):
        """Charge les contacts déchiffrés"""
        file_path = cls.DATA_DIR / "contacts.enc"
        if file_path.exists():
            encrypted = file_path.read_text()
            decrypted = EncryptionService.decrypt_data(encrypted)
            return json.loads(decrypted)
        return []
    
    @classmethod
    def save_conversations(cls, conversations):
        """Sauvegarde les conversations chiffrées"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        data = json.dumps(conversations, ensure_ascii=False, indent=2)
        encrypted = EncryptionService.encrypt_data(data)
        (cls.DATA_DIR / "conversations.enc").write_text(encrypted)
    
    @classmethod
    def load_conversations(cls):
        """Charge les conversations déchiffrées"""
        file_path = cls.DATA_DIR / "conversations.enc"
        if file_path.exists():
            encrypted = file_path.read_text()
            decrypted = EncryptionService.decrypt_data(encrypted)
            return json.loads(decrypted)
        return {}

# Initialisation de la session
if 'contacts' not in st.session_state:
    st.session_state.contacts = StorageService.load_contacts()

if 'conversations' not in st.session_state:
    st.session_state.conversations = StorageService.load_conversations()

if 'current_contact' not in st.session_state:
    st.session_state.current_contact = None

# En-tête de l'application
st.markdown("""
<div class="app-header">
    <div class="app-title">🤝 Collabo</div>
    <div class="app-subtitle">Plateforme de Networking Intelligent & Sécurisée</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📱 Navigation")
    page = st.radio(
        "",
        ["🏠 Dashboard", "👥 Contacts", "💬 Conversations", "📊 Analytics", "⚙️ Paramètres"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Statistiques rapides
    st.markdown("### 📈 Statistiques")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Contacts", len(st.session_state.contacts))
    with col2:
        st.metric("Conversations", len(st.session_state.conversations))
    
    st.markdown("---")
    
    # Sécurité
    st.markdown("### 🔒 Sécurité")
    st.success("✓ Chiffrement actif")
    st.info("✓ Stockage local")
    st.info("✓ Zéro serveur externe")

# Page principale selon la sélection
if page == "🏠 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Contacts Totaux</div>
        </div>
        """.format(len(st.session_state.contacts)), unsafe_allow_html=True)
    
    with col2:
        high_priority = sum(1 for c in st.session_state.contacts if c.get('priority') == 'high')
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Haute Priorité</div>
        </div>
        """.format(high_priority), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Conversations</div>
        </div>
        """.format(len(st.session_state.conversations)), unsafe_allow_html=True)
    
    with col4:
        # RDV à venir
        upcoming = sum(1 for c in st.session_state.contacts if c.get('next_meeting'))
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">RDV à venir</div>
        </div>
        """.format(upcoming), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Activité récente
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📅 Prochains Rendez-vous")
        if st.session_state.contacts:
            contacts_with_meetings = [c for c in st.session_state.contacts if c.get('next_meeting')]
            if contacts_with_meetings:
                for contact in contacts_with_meetings[:5]:
                    st.markdown(f"""
                    <div class="professional-card">
                        <strong>👤 {contact['name']}</strong><br>
                        📅 {contact.get('next_meeting', 'Non défini')}<br>
                        📝 {contact.get('next_action', 'Aucune action')}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun rendez-vous programmé")
        else:
            st.info("Ajoutez des contacts pour voir vos rendez-vous")
    
    with col2:
        st.markdown("### ⭐ Contacts Prioritaires")
        high_priority_contacts = [c for c in st.session_state.contacts if c.get('priority') == 'high']
        if high_priority_contacts:
            for contact in high_priority_contacts[:5]:
                st.markdown(f"""
                <div class="contact-card">
                    <div class="contact-name">{contact['name']}</div>
                    <div class="contact-detail">🏢 {contact.get('domain', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun contact haute priorité")

elif page == "👥 Contacts":
    st.markdown("## 👥 Gestion des Contacts")
    
    tab1, tab2 = st.tabs(["📋 Liste des Contacts", "➕ Ajouter un Contact"])
    
    with tab1:
        if st.session_state.contacts:
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Rechercher", placeholder="Nom, domaine...")
            with col2:
                filter_priority = st.selectbox("Priorité", ["Toutes", "Haute", "Moyenne", "Basse"])
            with col3:
                filter_domain = st.selectbox("Domaine", ["Tous"] + list(set(c.get('domain', '') for c in st.session_state.contacts if c.get('domain'))))
            
            # Affichage des contacts
            for idx, contact in enumerate(st.session_state.contacts):
                # Filtrage
                if search and search.lower() not in contact['name'].lower() and search.lower() not in contact.get('domain', '').lower():
                    continue
                if filter_priority != "Toutes" and contact.get('priority', '').lower() != filter_priority.lower():
                    continue
                if filter_domain != "Tous" and contact.get('domain', '') != filter_domain:
                    continue
                
                with st.expander(f"👤 {contact['name']} - {contact.get('domain', 'N/A')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **📧 Contact:** {contact.get('email', 'N/A')} | 📱 {contact.get('phone', 'N/A')}<br>
                        **🏢 Domaine:** {contact.get('domain', 'N/A')}<br>
                        **🤝 Occasion:** {contact.get('occasion', 'N/A')}<br>
                        **💭 Sujets abordés:** {contact.get('topics', 'N/A')}<br>
                        **📅 Prochain RDV:** {contact.get('next_meeting', 'Non défini')}<br>
                        **📝 Prochaine action:** {contact.get('next_action', 'Aucune')}<br>
                        **⭐ Priorité:** <span class="status-badge badge-{contact.get('priority', 'low')}">{contact.get('priority', 'low').upper()}</span>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("💬 Chat", key=f"chat_{idx}"):
                            st.session_state.current_contact = contact
                            st.rerun()
                        if st.button("🗑️ Supprimer", key=f"del_{idx}"):
                            st.session_state.contacts.pop(idx)
                            StorageService.save_contacts(st.session_state.contacts)
                            st.rerun()
        else:
            st.info("Aucun contact enregistré. Ajoutez votre premier contact!")
    
    with tab2:
        with st.form("new_contact"):
            st.markdown("### ➕ Nouveau Contact")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Nom complet*")
                email = st.text_input("📧 Email")
                domain = st.text_input("🏢 Domaine d'activité*")
            
            with col2:
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
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'domain': domain,
                        'occasion': occasion,
                        'topics': topics,
                        'next_meeting': next_meeting,
                        'next_action': next_action,
                        'priority': priority,
                        'created_at': datetime.now().isoformat()
                    }
                    st.session_state.contacts.append(new_contact)
                    StorageService.save_contacts(st.session_state.contacts)
                    st.success(f"✅ Contact {name} ajouté avec succès!")
                    st.rerun()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

elif page == "💬 Conversations":
    st.markdown("## 💬 Messagerie Sécurisée")
    
    if st.session_state.contacts:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("### 📱 Contacts")
            selected_contact = st.radio(
                "",
                [c['name'] for c in st.session_state.contacts],
                label_visibility="collapsed"
            )
            
            # Trouver le contact sélectionné
            contact = next(c for c in st.session_state.contacts if c['name'] == selected_contact)
        
        with col2:
            st.markdown(f"### 💬 Conversation avec {contact['name']}")
            st.markdown(f"*{contact.get('domain', 'N/A')}*")
            
            # Zone de conversation
            conv_key = contact['id']
            if conv_key not in st.session_state.conversations:
                st.session_state.conversations[conv_key] = []
            
            # Afficher les messages
            for msg in st.session_state.conversations[conv_key]:
                align = "message-sent" if msg['sender'] == 'user' else "message-received"
                st.markdown(f"""
                <div class="message-bubble {align}">
                    {msg['text']}<br>
                    <small style="opacity: 0.7;">{msg['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # Envoyer un message
            with st.form("send_message", clear_on_submit=True):
                message = st.text_area("💭 Votre message", height=100)
                col1, col2 = st.columns([4, 1])
                with col1:
                    send = st.form_submit_button("📤 Envoyer", use_container_width=True)
                with col2:
                    audio = st.form_submit_button("🎤 Audio")
                
                if send and message:
                    new_msg = {
                        'sender': 'user',
                        'text': message,
                        'timestamp': datetime.now().strftime("%H:%M")
                    }
                    st.session_state.conversations[conv_key].append(new_msg)
                    StorageService.save_conversations(st.session_state.conversations)
                    st.rerun()
    else:
        st.info("Ajoutez des contacts pour commencer à discuter")

elif page == "📊 Analytics":
    st.markdown("## 📊 Analyses & Insights")
    
    if st.session_state.contacts:
        # Distribution par domaine
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Contacts par Domaine")
            domains = {}
            for contact in st.session_state.contacts:
                domain = contact.get('domain', 'Non défini')
                domains[domain] = domains.get(domain, 0) + 1
            
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"""
                <div class="professional-card">
                    <strong>{domain}</strong>: {count} contact(s)
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⭐ Distribution des Priorités")
            priorities = {'high': 0, 'medium': 0, 'low': 0}
            for contact in st.session_state.contacts:
                priority = contact.get('priority', 'low')
                priorities[priority] += 1
            
            st.markdown(f"""
            <div class="professional-card">
                <span class="status-badge badge-high">HAUTE: {priorities['high']}</span><br><br>
                <span class="status-badge badge-medium">MOYENNE: {priorities['medium']}</span><br><br>
                <span class="status-badge badge-low">BASSE: {priorities['low']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📈 Activité du Réseau")
        st.info("💡 Analysez vos interactions pour optimiser votre networking")
    else:
        st.info("Ajoutez des contacts pour voir les analytics")

elif page == "⚙️ Paramètres":
    st.markdown("## ⚙️ Paramètres")
    
    st.markdown("### 🔒 Sécurité & Confidentialité")
    
    st.markdown("""
    <div class="profes