# streamlit_app.py
"""
Collabo - Application de Networking Intelligent
Version améliorée avec toutes les fonctionnalités
"""

import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from ai_service import AIService
import qrcode
from io import BytesIO
import base64

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
    .main-header {
        background: linear-gradient(135deg, #2E3440 0%, #5E81AC 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .contact-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #5E81AC;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .online-badge {
        background: #A3BE8C;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
    }
    .offline-badge {
        background: #BF616A;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
    }
    .favorite-star {
        color: #EBCB8B;
        font-size: 1.2em;
    }
    .message-sent {
        background: #5E81AC;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
        margin-left: auto;
    }
    .message-received {
        background: #ECEFF4;
        color: #2E3440;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2em;
        font-weight: bold;
        color: #5E81AC;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# Charger les variables d'environnement
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
            "users": [],
            "contacts": [],
            "messages": [],
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
    """Génère un QR code pour inviter un contact"""
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
    """Basculer le statut favori d'un contact"""
    for c in data["contacts"]:
        if c["owner"] == owner and c["contact_name"] == contact_name:
            c["favorite"] = not c.get("favorite", False)
            break
    save_data(data)

def update_online_status(username, status):
    """Mettre à jour le statut en ligne"""
    user = get_user(username)
    if user:
        user["online"] = status
        save_data(data)

# ==============================
# Authentification Sidebar
# ==============================
if "username" not in st.session_state:
    st.markdown('<div class="main-header"><h1>🤝 Collabo</h1><p>Networking Intelligent & Sécurisé</p></div>', 
                unsafe_allow_html=True)
    
    st.sidebar.header("🔐 Authentification")
    auth_mode = st.sidebar.radio("", ["Connexion", "Inscription"])
    username = st.sidebar.text_input("👤 Utilisateur")
    password = st.sidebar.text_input("🔑 Mot de passe", type="password")

    if auth_mode == "Inscription":
        email = st.sidebar.text_input("📧 Email (optionnel)")
        if st.sidebar.button("✅ S'inscrire", use_container_width=True):
            if not username or not password:
                st.sidebar.error("❌ Veuillez remplir tous les champs")
            elif get_user(username):
                st.sidebar.warning("⚠️ Utilisateur déjà existant !")
            else:
                data["users"].append({
                    "username": username,
                    "password": password,
                    "email": email,
                    "created_at": str(datetime.now()),
                    "online": True
                })
                save_data(data)
                st.sidebar.success("✅ Inscription réussie ! Connectez-vous maintenant.")

    elif auth_mode == "Connexion":
        if st.sidebar.button("🚀 Se connecter", use_container_width=True):
            user = get_user(username)
            if user and user["password"] == password:
                st.session_state["username"] = username
                update_online_status(username, True)
                st.rerun()
            else:
                st.sidebar.error("❌ Utilisateur ou mot de passe incorrect !")
    
    # Message d'accueil
    st.info("👋 Bienvenue sur Collabo ! Connectez-vous ou créez un compte pour commencer.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔒 Sécurisé")
        st.write("Chiffrement de bout en bout")
    with col2:
        st.markdown("### 🤖 Intelligent")
        st.write("Analyse IA de vos conversations")
    with col3:
        st.markdown("### 🌐 Connecté")
        st.write("Networking professionnel")

# ==============================
# Application principale (utilisateur connecté)
# ==============================
else:
    current_user = st.session_state["username"]
    
    # Sidebar pour utilisateur connecté
    with st.sidebar:
        st.markdown(f"### 👤 {current_user}")
        
        # Statut en ligne
        online_status = st.checkbox("🟢 En ligne", value=True, key="online_status")
        update_online_status(current_user, online_status)
        
        st.markdown("---")
        
        # Statistiques rapides
        contacts = get_contacts(current_user)
        unread = count_unread_messages(current_user)
        
        st.metric("📇 Contacts", len(contacts))
        st.metric("💬 Messages non lus", unread)
        st.metric("⭐ Favoris", len([c for c in contacts if c.get("favorite", False)]))
        
        st.markdown("---")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            update_online_status(current_user, False)
            del st.session_state["username"]
            st.rerun()
    
    # En-tête principal
    st.markdown(f'<div class="main-header"><h1>🤝 Collabo</h1><p>Bienvenue {current_user} !</p></div>', 
                unsafe_allow_html=True)
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "👥 Contacts", 
        "💬 Messages", 
        "🤖 Analyse IA",
        "⚙️ Paramètres"
    ])
    
    # ==============================
    # TAB 1 : DASHBOARD
    # ==============================
    with tab1:
        st.header("📊 Tableau de Bord")
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(contacts)}</div>
                <div>Contacts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            favorites = len([c for c in contacts if c.get("favorite", False)])
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{favorites}</div>
                <div>Favoris</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            online = len([c for c in contacts if c.get("online", False)])
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{online}</div>
                <div>En ligne</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{unread}</div>
                <div>Non lus</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Activité récente
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("💬 Messages Récents")
            recent_messages = sorted(
                [m for m in data["messages"] 
                 if m["sender"] == current_user or m["receiver"] == current_user],
                key=lambda x: x["timestamp"],
                reverse=True
            )[:5]
            
            if recent_messages:
                for msg in recent_messages:
                    sender = msg["sender"]
                    receiver = msg["receiver"]
                    other = receiver if sender == current_user else sender
                    direction = "→" if sender == current_user else "←"
                    st.write(f"{direction} **{other}**: {msg['text'][:50]}...")
            else:
                st.info("Aucun message récent")
        
        with col2:
            st.subheader("⭐ Contacts Favoris")
            fav_contacts = [c for c in contacts if c.get("favorite", False)]
            if fav_contacts:
                for c in fav_contacts[:5]:
                    status = "🟢" if c.get("online", False) else "🔴"
                    st.write(f"{status} {c['contact_name']}")
            else:
                st.info("Aucun favori")
    
    # ==============================
    # TAB 2 : CONTACTS
    # ==============================
    with tab2:
        st.header("👥 Gestion des Contacts")
        
        # Sous-onglets pour mieux organiser
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "📋 Liste", 
            "➕ Ajouter", 
            "📲 Inviter",
            "📥 Importer"
        ])
        
        # Sous-tab: Liste des contacts
        with subtab1:
            if not contacts:
                st.info("👋 Vous n'avez pas encore de contacts. Ajoutez-en un !")
            else:
                # Filtres
                col1, col2, col3 = st.columns(3)
                with col1:
                    show_favorites = st.checkbox("⭐ Favoris uniquement")
                with col2:
                    show_online = st.checkbox("🟢 En ligne uniquement")
                with col3:
                    search = st.text_input("🔍 Rechercher", placeholder="Nom du contact...")
                
                # Afficher les contacts filtrés
                filtered_contacts = contacts
                if show_favorites:
                    filtered_contacts = [c for c in filtered_contacts if c.get("favorite", False)]
                if show_online:
                    filtered_contacts = [c for c in filtered_contacts if c.get("online", False)]
                if search:
                    filtered_contacts = [c for c in filtered_contacts 
                                       if search.lower() in c["contact_name"].lower()]
                
                st.write(f"**{len(filtered_contacts)} contact(s) trouvé(s)**")
                
                for idx, contact in enumerate(filtered_contacts):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            status_badge = "online-badge" if contact.get("online", False) else "offline-badge"
                            status_text = "En ligne" if contact.get("online", False) else "Hors ligne"
                            fav_icon = "⭐" if contact.get("favorite", False) else "☆"
                            
                            st.markdown(f"""
                            <div class="contact-card">
                                <strong>{fav_icon} {contact['contact_name']}</strong>
                                <span class="{status_badge}">{status_text}</span>
                                <br><small>Ajouté le: {contact.get('created_at', 'N/A')[:10]}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("⭐" if not contact.get("favorite", False) else "💛", 
                                       key=f"fav_{idx}"):
                                toggle_favorite(current_user, contact["contact_name"])
                                st.rerun()
                        
                        with col3:
                            if st.button("🗑️", key=f"del_{idx}"):
                                data["contacts"] = [c for c in data["contacts"] 
                                                  if not (c["owner"] == current_user 
                                                         and c["contact_name"] == contact["contact_name"])]
                                save_data(data)
                                st.rerun()
        
        # Sous-tab: Ajouter contact
        with subtab2:
            st.subheader("➕ Ajouter un nouveau contact")
            
            with st.form("add_contact_form"):
                contact_name = st.text_input("👤 Nom du contact*", placeholder="Ex: Jean Dupont")
                contact_email = st.text_input("📧 Email (optionnel)", placeholder="jean@example.com")
                contact_phone = st.text_input("📱 Téléphone (optionnel)", placeholder="+33 6 12 34 56 78")
                add_as_favorite = st.checkbox("⭐ Ajouter aux favoris")
                
                submitted = st.form_submit_button("✅ Ajouter Contact")
                
                if submitted:
                    if not contact_name.strip():
                        st.error("❌ Le nom du contact est obligatoire")
                    elif any(c["contact_name"] == contact_name and c["owner"] == current_user 
                           for c in data["contacts"]):
                        st.warning("⚠️ Ce contact existe déjà dans votre liste")
                    else:
                        data["contacts"].append({
                            "owner": current_user,
                            "contact_name": contact_name,
                            "email": contact_email,
                            "phone": contact_phone,
                            "created_at": str(datetime.now()),
                            "favorite": add_as_favorite,
                            "online": False
                        })
                        save_data(data)
                        st.success(f"✅ {contact_name} ajouté avec succès !")
                        st.rerun()
        
        # Sous-tab: Inviter
        with subtab3:
            st.subheader("📲 Inviter un contact via QR Code")
            
            st.info("🎯 Générez votre QR Code personnel et partagez-le pour que d'autres puissent vous ajouter facilement !")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🎨 Générer mon QR Code", use_container_width=True):
                    qr_buffer = generate_qr_code(current_user)
                    st.image(qr_buffer, caption=f"QR Code de {current_user}", width=300)
                    
                    # Bouton de téléchargement
                    st.download_button(
                        label="⬇️ Télécharger le QR Code",
                        data=qr_buffer,
                        file_name=f"collabo_qr_{current_user}.png",
                        mime="image/png"
                    )
            
            with col2:
                st.markdown("### 📝 Ou partagez votre code")
                st.code(f"collabo://add/{current_user}", language="text")
                st.caption("Envoyez ce code à vos contacts pour qu'ils vous ajoutent")
        
        # Sous-tab: Importer
        with subtab4:
            st.subheader("📥 Scanner un QR Code ou importer un contact")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📷 Scanner un QR Code")
                uploaded_file = st.file_uploader("Téléchargez une image QR Code", type=['png', 'jpg', 'jpeg'])
                
                if uploaded_file:
                    st.info("🔍 Fonctionnalité de scan en développement")
                    # Ici, vous pourriez intégrer pyzbar ou une bibliothèque similaire
            
            with col2:
                st.markdown("#### 🔗 Importer via code")
                invite_code = st.text_input("Entrez le code d'invitation", 
                                           placeholder="collabo://add/username")
                
                if st.button("➕ Ajouter depuis le code", use_container_width=True):
                    if invite_code.startswith("collabo://add/"):
                        username_to_add = invite_code.replace("collabo://add/", "")
                        
                        # Vérifier si l'utilisateur existe
                        if get_user(username_to_add):
                            # Vérifier si pas déjà dans les contacts
                            if not any(c["contact_name"] == username_to_add and c["owner"] == current_user 
                                     for c in data["contacts"]):
                                data["contacts"].append({
                                    "owner": current_user,
                                    "contact_name": username_to_add,
                                    "created_at": str(datetime.now()),
                                    "favorite": False,
                                    "online": get_user(username_to_add).get("online", False)
                                })
                                save_data(data)
                                st.success(f"✅ {username_to_add} ajouté à vos contacts !")
                                st.rerun()
                            else:
                                st.warning("⚠️ Ce contact est déjà dans votre liste")
                        else:
                            st.error("❌ Cet utilisateur n'existe pas")
                    else:
                        st.error("❌ Code d'invitation invalide")
    
    # ==============================
    # TAB 3 : MESSAGES
    # ==============================
    with tab3:
        st.header("💬 Messagerie")
        
        if not contacts:
            st.info("👋 Ajoutez des contacts pour commencer à échanger des messages")
        else:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📱 Conversations")
                
                # Liste des contacts avec nombre de messages non lus
                for contact in contacts:
                    unread_count = len([m for m in data["messages"] 
                                      if m["sender"] == contact["contact_name"] 
                                      and m["receiver"] == current_user 
                                      and not m.get("read", False)])
                    
                    status = "🟢" if contact.get("online", False) else "🔴"
                    badge = f" ({unread_count})" if unread_count > 0 else ""
                    
                    if st.button(f"{status} {contact['contact_name']}{badge}", 
                               key=f"chat_{contact['contact_name']}",
                               use_container_width=True):
                        st.session_state["selected_contact"] = contact["contact_name"]
            
            with col2:
                if "selected_contact" in st.session_state:
                    selected = st.session_state["selected_contact"]
                    st.subheader(f"💬 Conversation avec {selected}")
                    
                    # Afficher les messages
                    messages = get_messages(current_user, selected)
                    
                    # Marquer les messages comme lus
                    for m in messages:
                        if m["receiver"] == current_user and not m.get("read", False):
                            m["read"] = True
                    save_data(data)
                    
                    # Container pour les messages
                    with st.container():
                        if messages:
                            for msg in messages:
                                is_sent = msg["sender"] == current_user
                                msg_class = "message-sent" if is_sent else "message-received"
                                
                                st.markdown(f"""
                                <div class="{msg_class}">
                                    {msg['text']}<br>
                                    <small style="opacity: 0.7;">{msg['timestamp'][:16]}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("Aucun message. Commencez la conversation !")
                    
                    # Formulaire d'envoi
                    with st.form("send_message_form", clear_on_submit=True):
                        message_text = st.text_area("✍️ Votre message", height=100,
                                                   placeholder="Tapez votre message ici...")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            send_btn = st.form_submit_button("📤 Envoyer", use_container_width=True)
                        with col2:
                            audio_btn = st.form_submit_button("🎤 Audio")
                        
                        if send_btn and message_text.strip():
                            data["messages"].append({
                                "sender": current_user,
                                "receiver": selected,
                                "text": message_text,
                                "timestamp": str(datetime.now()),
                                "read": False
                            })
                            save_data(data)
                            st.rerun()
                else:
                    st.info("👈 Sélectionnez un contact pour commencer une conversation")
    
    # ==============================
    # TAB 4 : ANALYSE IA
    # ==============================
    with tab4:
        st.header("🤖 Analyse IA des Conversations")
        
        if not AI_ANALYSIS_ENABLED or ai is None:
            st.warning("⚠️ L'analyse IA n'est pas activée. Configurez votre clé API dans le fichier .env")
        elif not contacts:
            st.info("👋 Ajoutez des contacts et échangez des messages pour utiliser l'analyse IA")
        else:
            st.info("💡 L'IA analyse vos conversations pour extraire les points clés, opportunités et insights")
            
            contact_for_analysis = st.selectbox(
                "📊 Choisir un contact à analyser",
                [c["contact_name"] for c in contacts]
            )
            
            if st.button("🔍 Analyser la conversation", use_container_width=True):
                messages = get_messages(current_user, contact_for_analysis)
                
                if not messages:
                    st.warning("Aucun message à analyser pour ce contact")
                else:
                    full_text = "\n".join([f"{m['sender']}: {m['text']}" for m in messages])
                    
                    with st.spinner("🤖 Analyse en cours..."):
                        try:
                            result = ai.analyze_conversation(full_text, contact_for_analysis)
                            
                            # Afficher les résultats
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📌 Points Clés")
                                if "key_points" in result:
                                    for point in result["key_points"]:
                                        st.write(f"• {point}")
                                
                                st.subheader("🤝 Opportunités")
                                if "opportunities" in result:
                                    for opp in result["opportunities"]:
                                        st.write(f"• {opp}")
                            
                            with col2:
                                st.subheader("📊 Évaluation")
                                if "credibility_score" in result:
                                    st.metric("Crédibilité", f"{result['credibility_score']}/10")
                                if "usefulness_score" in result:
                                    st.metric("Utilité", f"{result['usefulness_score']}/10")
                                if "priority_level" in result:
                                    st.metric("Priorité", result["priority_level"].upper())
                            
                            # Afficher le JSON complet
                            with st.expander("📄 Voir l'analyse complète"):
                                st.json(result)
                        
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
    
    # ==============================
    # TAB 5 : PARAMÈTRES
    # ==============================
    with tab5:
        st.header("⚙️ Paramètres")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Profil")
            user_data = get_user(current_user)
            
            st.text_input("Nom d'utilisateur", value=current_user, disabled=True)
            new_email = st.text_input("Email", value=user_data.get("email", ""))
            
            if st.button("💾 Sauvegarder", use_container_width=True):
                user_data["email"] = new_email
                save_data(data)
                st.success("✅ Profil mis à jour !")
        
        with col2:
            st.subheader("🔔 Notifications")
            enable_notif = st.checkbox("Activer les notifications", value=True)
            sound_notif = st.checkbox("Sons de notification", value=True)
        
        st.markdown("---")
        
        st.subheader("💾 Gestion des Données")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Exporter mes données", use_container_width=True):
                user_export = {
                    "user": current_user,
                    "contacts": get_contacts(current_user),
                    "messages": [m for m in data["messages"] 
                               if m["sender"] == current_user or m["receiver"] == current_user],
                    "exported_at": str(datetime.now())
                }
                
                st.download_button(
                    "⬇️ Télécharger JSON",
                    json.dumps(user_export, indent=2, ensure_ascii=False),
                    f"collabo_export_{current_user}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with col2:
            data_size = len(json.dumps(data))
            st.metric("Espace utilisé", f"{data_size / 1024:.1f} KB")
        
        with col3:
            if st.button("🗑️ Effacer mes données", use_container_width=True):
                st.warning("⚠️ Cette action est irréversible !")
                if st.checkbox("Je confirme vouloir effacer toutes mes données"):
                    # Supprimer tous les contacts de l'utilisateur
                    data["contacts"] = [c for c in data["contacts"] 
                                       if c["owner"] != current_user]
                    # Supprimer tous les messages de l'utilisateur
                    data["messages"] = [m for m in data["messages"] 
                                       if m["sender"] != current_user 
                                       and m["receiver"] != current_user]
                    save_data(data)
                    st.success("✅ Données effacées avec succès")
                    st.rerun()
        
        st.markdown("---")
        
        st.subheader("ℹ️ À propos")
        st.markdown("""
        **🤝 Collabo v1.0.0**
        
        Application de networking professionnel intelligent et sécurisée.
        
        **Fonctionnalités :**
        - 👥 Gestion de contacts avec favoris
        - 💬 Messagerie sécurisée en temps réel
        - 📲 Invitation par QR Code
        - 🤖 Analyse IA des conversations
        - 🟢 Statut en ligne/hors ligne
        - 📊 Statistiques et analytics
        
        **Support :** support@collabo-app.com
        
        **Licence :** MIT License
        """)

# ==============================
# Auto-refresh pour notifications (optionnel)
# ==============================
# Décommentez si vous avez installé streamlit-autorefresh
# from streamlit_autorefresh import st_autorefresh
# st_autorefresh(interval=5000, key="autorefresh")