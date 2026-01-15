# streamlit_app.py
import os, json
import streamlit as st
from datetime import datetime
from io import BytesIO

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

# =============================
# CONFIG PAGE
# =============================
st.set_page_config(
    page_title="Collabo",
    page_icon="🤝",
    layout="wide"
)

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

# Charger les données
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
        for c in data["contacts"]:
            if c["owner"] == st.session_state.username and c["name"] == contact_to_toggle["name"]:
                c["favorite"] = not c.get("favorite", False)
                break
        save_data(data)
        st.session_state.data = load_data()

def login():
    u = st.session_state.get("input_user", "").strip()
    p = st.session_state.get("input_pass", "").strip()
    
    if not u or not p:
        st.sidebar.error("⚠️ Veuillez remplir tous les champs")
        return
    
    user = get_user(u)
    if user and user["password"] == p:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.sidebar.success(f"✅ Connecté en tant que {u}")
        st.rerun()
    else:
        st.sidebar.error("❌ Identifiants incorrects")

def register():
    u = st.session_state.get("input_user", "").strip()
    p = st.session_state.get("input_pass", "").strip()
    e = st.session_state.get("input_email", "").strip()
    
    if not u or not p:
        st.sidebar.error("⚠️ Veuillez remplir nom d'utilisateur et mot de passe")
        return
    
    if get_user(u):
        st.sidebar.error("❌ Ce nom d'utilisateur existe déjà")
        return
    
    # Créer le nouvel utilisateur
    data["users"].append({
        "username": u,
        "password": p,
        "email": e,
        "online": False
    })
    save_data(data)
    st.session_state.data = load_data()
    st.sidebar.success(f"✅ Compte créé ! Vous pouvez maintenant vous connecter.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
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

def generate_qr(username):
    if not QRCODE_AVAILABLE:
        return None
    try:
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(f"collabo://add/{username}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception as e:
        return None

def add_contact():
    new_contact = st.session_state.get("new_contact_name", "").strip()
    if not new_contact:
        return
    
    # Vérifier si le contact existe
    if not get_user(new_contact):
        st.error("❌ Cet utilisateur n'existe pas")
        return
    
    # Vérifier si déjà dans les contacts
    existing = [c for c in data["contacts"] if c["owner"] == st.session_state.username and c["name"] == new_contact]
    if existing:
        st.warning("⚠️ Ce contact existe déjà")
        return
    
    # Ajouter le contact
    data["contacts"].append({
        "owner": st.session_state.username,
        "name": new_contact,
        "favorite": False
    })
    save_data(data)
    st.session_state.data = load_data()
    st.success(f"✅ Contact {new_contact} ajouté !")
    st.rerun()

# =============================
# SIDEBAR
# =============================
st.sidebar.title("🤝 Collabo")

if not st.session_state.logged_in:
    # MODE AUTHENTIFICATION
    auth_mode = st.sidebar.radio("Mode", ["Connexion", "Inscription"], key="auth_mode")
    
    st.sidebar.text_input("Utilisateur", key="input_user")
    st.sidebar.text_input("Mot de passe", type="password", key="input_pass")
    
    if auth_mode == "Inscription":
        st.sidebar.text_input("Email (optionnel)", key="input_email")
        st.sidebar.button("S'inscrire", on_click=register, use_container_width=True)
    else:
        st.sidebar.button("Se connecter", on_click=login, use_container_width=True)
    
    st.sidebar.info("💡 Comptes de test:\n- alice / 123\n- bob / 123")
    
else:
    # MODE CONNECTÉ
    st.sidebar.success(f"👤 {st.session_state.username}")
    st.sidebar.button("🚪 Se déconnecter", on_click=logout, use_container_width=True)
    st.sidebar.divider()
    st.sidebar.radio("Navigation", ["Dashboard","Contacts","Messages","Stats"], key="page")

# =============================
# HEADER
# =============================
st.markdown("<h1 style='text-align:center'>🤝 Collabo</h1>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.info("👈 Veuillez vous connecter ou créer un compte dans la barre latérale")
    st.stop()

# =============================
# DASHBOARD
# =============================
if st.session_state.page == "Dashboard":
    st.subheader("📊 Tableau de bord")
    st.write(f"Bienvenue **{st.session_state.username}** !")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Contacts", len(get_contacts(st.session_state.username)))
    with col2:
        total_sent = len([m for m in data["messages"] if m["sender"]==st.session_state.username])
        st.metric("📤 Messages envoyés", total_sent)
    with col3:
        total_received = len([m for m in data["messages"] if m["receiver"]==st.session_state.username])
        st.metric("📥 Messages reçus", total_received)

# =============================
# CONTACTS
# =============================
elif st.session_state.page == "Contacts":
    st.subheader("📇 Contacts")
    
    # Ajouter un contact
    with st.expander("➕ Ajouter un contact"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Nom d'utilisateur", key="new_contact_name", placeholder="Ex: alice")
        with col2:
            st.button("Ajouter", on_click=add_contact)
    
    st.divider()
    
    # Liste des contacts
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("Aucun contact pour le moment. Ajoutez-en un ci-dessus !")
    else:
        for i, contact in enumerate(contacts):
            with st.container():
                col1, col2, col3 = st.columns([0.5, 0.1, 0.4])
                with col1:
                    st.write(f"**{contact['name']}**")
                with col2:
                    st.button(
                        "★" if contact.get("favorite") else "☆",
                        key=f"fav_{contact['name']}_{i}",
                        on_click=toggle_fav,
                        args=(i,),
                        help="Favori"
                    )
                with col3:
                    qr_img = generate_qr(contact["name"])
                    if qr_img:
                        st.image(qr_img, width=80)

# =============================
# MESSAGES
# =============================
elif st.session_state.page == "Messages":
    st.subheader("💬 Messages")
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("Aucun contact. Ajoutez des contacts pour envoyer des messages !")
    else:
        for i, contact in enumerate(contacts):
            with st.expander(f"💬 {contact['name']}", expanded=(i==0)):
                # Historique
                messages = get_messages(st.session_state.username, contact["name"])
                if messages:
                    for msg in messages[-10:]:
                        sender = "Vous" if msg["sender"] == st.session_state.username else contact["name"]
                        align = "right" if msg["sender"] == st.session_state.username else "left"
                        st.markdown(f"**{sender}**: {msg['text']}")
                else:
                    st.info("Aucun message")
                
                # Envoi
                with st.form(key=f"form_{contact['name']}_{i}"):
                    msg_input = st.text_input("Votre message", key=f"msg_{i}")
                    submit = st.form_submit_button("📤 Envoyer")
                    if submit and msg_input.strip():
                        send_message(contact["name"], msg_input)
                        st.rerun()

# =============================
# STATS
# =============================
elif st.session_state.page == "Stats":
    st.subheader("📊 Statistiques")
    contacts = get_contacts(st.session_state.username)
    total_contacts = len(contacts)
    total_sent = len([m for m in data["messages"] if m["sender"]==st.session_state.username])
    total_received = len([m for m in data["messages"] if m["receiver"]==st.session_state.username])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total contacts", total_contacts)
        st.metric("Messages envoyés", total_sent)
    with col2:
        st.metric("Messages reçus", total_received)
        st.metric("Total messages", total_sent + total_received)