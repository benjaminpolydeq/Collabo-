# streamlit_app.py
import os, json
import streamlit as st
from datetime import datetime, timedelta
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
# CUSTOM CSS - DESIGN MODERNE
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .message-sent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 2px 5px rgba(102, 126, 234, 0.3);
    }
    
    .message-received {
        background: #f0f2f6;
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 70%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h1, h2, h3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px;
        font-weight: 600;
    }
    
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #667eea30;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .ai-analysis {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        border: 2px solid #f093fb;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

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
            return {"sentiment": "neutral", "emoji": "😐", "color": "#667eea"}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de sentiment. Réponds uniquement avec: 'positif', 'négatif' ou 'neutre'."},
                    {"role": "user", "content": f"Analyse le sentiment de ce message: {text}"}
                ],
                max_tokens=50
            )
            result = response.choices[0].message.content.lower()
            
            if "positif" in result:
                return {"sentiment": "positif", "emoji": "😊", "color": "#11998e"}
            elif "négatif" in result:
                return {"sentiment": "négatif", "emoji": "😔", "color": "#eb3349"}
            else:
                return {"sentiment": "neutre", "emoji": "😐", "color": "#667eea"}
                
        except Exception as e:
            return {"sentiment": "erreur", "emoji": "⚠️", "color": "#ffa500", "error": str(e)}
    
    def suggest_response(self, conversation_history):
        if not self.enabled:
            return "IA non disponible. Ajoutez votre clé OpenAI."
        
        try:
            messages_text = "\n".join([f"{m['sender']}: {m['text']}" for m in conversation_history[-5:]])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui suggère des réponses amicales et professionnelles."},
                    {"role": "user", "content": f"Basé sur cette conversation, suggère une réponse appropriée:\n\n{messages_text}"}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def summarize_conversation(self, messages):
        if not self.enabled:
            return "IA non disponible. Ajoutez votre clé OpenAI."
        
        try:
            messages_text = "\n".join([f"{m['sender']}: {m['text']}" for m in messages])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu résumes des conversations de manière concise et claire."},
                    {"role": "user", "content": f"Résume cette conversation en 2-3 phrases:\n\n{messages_text}"}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Erreur: {str(e)}"

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
        st.sidebar.success(f"✅ Bienvenue {u} !")
        time.sleep(0.5)
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
    
    if len(p) < 3:
        st.sidebar.error("⚠️ Le mot de passe doit contenir au moins 3 caractères")
        return
    
    if get_user(u):
        st.sidebar.error("❌ Ce nom d'utilisateur existe déjà")
        return
    
    data["users"].append({
        "username": u,
        "password": p,
        "email": e,
        "online": False,
        "bio": ""
    })
    save_data(data)
    st.session_state.data = load_data()
    st.sidebar.success(f"✅ Compte créé ! Vous pouvez vous connecter.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

def send_message(to_user, text):
    if text.strip() == "":
        return
    
    msg_data = {
        "sender": st.session_state.username,
        "receiver": to_user,
        "text": text,
        "timestamp": str(datetime.now())
    }
    data["messages"].append(msg_data)
    
    if ai_service.enabled:
        sentiment = ai_service.analyze_sentiment(text)
        data["ai_analyses"].append({
            "message_id": len(data["messages"]) - 1,
            "sentiment": sentiment,
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
        img = qr.make_image(fill_color="#667eea", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except:
        return None

def add_contact():
    new_contact = st.session_state.get("new_contact_name", "").strip()
    if not new_contact:
        return
    
    if not get_user(new_contact):
        st.error("❌ Cet utilisateur n'existe pas")
        return
    
    if new_contact == st.session_state.username:
        st.error("❌ Vous ne pouvez pas vous ajouter vous-même")
        return
    
    existing = [c for c in data["contacts"] if c["owner"] == st.session_state.username and c["name"] == new_contact]
    if existing:
        st.warning("⚠️ Ce contact existe déjà")
        return
    
    data["contacts"].append({
        "owner": st.session_state.username,
        "name": new_contact,
        "favorite": False
    })
    save_data(data)
    st.session_state.data = load_data()
    st.success(f"✅ {new_contact} ajouté à vos contacts !")
    time.sleep(1)
    st.rerun()

# =============================
# SIDEBAR
# =============================
st.sidebar.markdown("### 🤝 Collabo")
st.sidebar.markdown("*Messagerie Intelligente*")
st.sidebar.divider()

if not st.session_state.logged_in:
    auth_mode = st.sidebar.radio("", ["🔐 Connexion", "✨ Inscription"], label_visibility="collapsed")
    
    st.sidebar.text_input("👤 Utilisateur", key="input_user", placeholder="Votre nom")
    st.sidebar.text_input("🔒 Mot de passe", type="password", key="input_pass", placeholder="••••••")
    
    if auth_mode == "✨ Inscription":
        st.sidebar.text_input("📧 Email (optionnel)", key="input_email", placeholder="email@example.com")
        st.sidebar.button("✨ Créer un compte", on_click=register, use_container_width=True)
    else:
        st.sidebar.button("🔐 Se connecter", on_click=login, use_container_width=True)
    
    st.sidebar.divider()
    st.sidebar.info("💡 **Comptes de test**\n- alice / 123\n- bob / 123")
    
else:
    st.sidebar.success(f"👤 **{st.session_state.username}**")
    user = get_user(st.session_state.username)
    if user and user.get("bio"):
        st.sidebar.caption(user["bio"])
    
    st.sidebar.button("🚪 Déconnexion", on_click=logout, use_container_width=True)
    st.sidebar.divider()
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "👥 Contacts", "💬 Messages", "🤖 IA Assistant", "📊 Statistiques"],
        label_visibility="collapsed"
    )
    st.session_state.page = page.split(" ", 1)[1]

# =============================
# HEADER
# =============================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align:center'>🤝 Collabo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #667eea; font-size: 1.2rem;'>Messagerie Intelligente Nouvelle Génération</p>", unsafe_allow_html=True)

st.divider()

if not st.session_state.logged_in:
    st.info("👈 Connectez-vous pour accéder à toutes les fonctionnalités")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 💬 Messages")
        st.write("Discutez en temps réel avec vos contacts")
    with col2:
        st.markdown("### 🤖 IA")
        st.write("Analyse intelligente de vos conversations")
    with col3:
        st.markdown("### 📊 Stats")
        st.write("Suivez vos statistiques de communication")
    
    st.stop()

# =============================
# DASHBOARD
# =============================
if st.session_state.page == "Dashboard":
    st.markdown("### 🏠 Tableau de bord")
    st.write(f"Bienvenue **{st.session_state.username}** ! 👋")
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    contacts = get_contacts(st.session_state.username)
    total_sent = len([m for m in data["messages"] if m["sender"]==st.session_state.username])
    total_received = len([m for m in data["messages"] if m["receiver"]==st.session_state.username])
    fav_contacts = len([c for c in contacts if c.get("favorite")])
    
    with col1:
        st.metric("👥 Contacts", len(contacts))
    with col2:
        st.metric("📤 Envoyés", total_sent)
    with col3:
        st.metric("📥 Reçus", total_received)
    with col4:
        st.metric("⭐ Favoris", fav_contacts)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Activité récente")
        recent_msgs = sorted(
            [m for m in data["messages"] if m["sender"]==st.session_state.username or m["receiver"]==st.session_state.username],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:5]
        
        if recent_msgs:
            for msg in recent_msgs:
                sender = "Vous" if msg["sender"] == st.session_state.username else msg["sender"]
                receiver = "Vous" if msg["receiver"] == st.session_state.username else msg["receiver"]
                st.markdown(f"**{sender}** → **{receiver}**: {msg['text'][:50]}...")
        else:
            st.info("Aucune activité récente")
    
    with col2:
        st.markdown("### ⭐ Contacts favoris")
        fav_list = [c for c in contacts if c.get("favorite")]
        if fav_list:
            for contact in fav_list:
                st.markdown(f"⭐ **{contact['name']}**")
        else:
            st.info("Aucun contact favori")

# =============================
# CONTACTS
# =============================
elif st.session_state.page == "Contacts":
    st.markdown("### 👥 Mes Contacts")
    
    with st.expander("➕ Ajouter un nouveau contact", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Nom d'utilisateur", key="new_contact_name", placeholder="Ex: alice", label_visibility="collapsed")
        with col2:
            st.button("➕ Ajouter", on_click=add_contact, use_container_width=True)
    
    st.divider()
    
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("📭 Aucun contact. Ajoutez-en un ci-dessus !")
    else:
        favorites = [c for c in contacts if c.get("favorite")]
        others = [c for c in contacts if not c.get("favorite")]
        
        if favorites:
            st.markdown("#### ⭐ Favoris")
            for i, contact in enumerate(favorites):
                col1, col2, col3 = st.columns([0.5, 0.1, 0.4])
                with col1:
                    st.markdown(f"### {contact['name']}")
                with col2:
                    st.button(
                        "⭐",
                        key=f"fav_{contact['name']}_{i}",
                        on_click=toggle_fav,
                        args=(contacts.index(contact),),
                        help="Retirer des favoris"
                    )
                with col3:
                    qr_img = generate_qr(contact["name"])
                    if qr_img:
                        st.image(qr_img, width=100)
                st.divider()
        
        if others:
            st.markdown("#### 📋 Tous les contacts")
            for i, contact in enumerate(others):
                col1, col2, col3 = st.columns([0.5, 0.1, 0.4])
                with col1:
                    st.markdown(f"### {contact['name']}")
                with col2:
                    st.button(
                        "☆",
                        key=f"unfav_{contact['name']}_{i}",
                        on_click=toggle_fav,
                        args=(contacts.index(contact),),
                        help="Ajouter aux favoris"
                    )
                with col3:
                    qr_img = generate_qr(contact["name"])
                    if qr_img:
                        st.image(qr_img, width=100)
                st.divider()

# =============================
# MESSAGES
# =============================
elif st.session_state.page == "Messages":
    st.markdown("### 💬 Messages")
    contacts = get_contacts(st.session_state.username)
    
    if len(contacts) == 0:
        st.info("📭 Ajoutez des contacts pour commencer à échanger !")
    else:
        for i, contact in enumerate(contacts):
            messages = get_messages(st.session_state.username, contact["name"])
            unread = len([m for m in messages if m["receiver"] == st.session_state.username])
            
            badge = f" 🔴 {unread}" if unread > 0 else ""
            
            with st.expander(f"💬 {contact['name']}{badge}", expanded=(i==0)):
                
                if messages:
                    st.markdown("#### 📜 Historique")
                    for msg in messages[-10:]:
                        if msg["sender"] == st.session_state.username:
                            st.markdown(f'<div class="message-sent">💭 Vous: {msg["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="message-receiv```python
        st.metric("📤 Messages envoyés", len(my_sent))
    with col3:
        st.metric("📥 Messages reçus", len(my_received))
    with col4:
        st.metric("💬 Total échanges", len(my_sent) + len(my_received))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Messages par contact")
        contact_stats = {}
        for contact in contacts:
            msgs = get_messages(st.session_state.username, contact["name"])
            contact_stats[contact["name"]] = len(msgs)
        
        if contact_stats:
            for name, count in sorted(contact_stats.items(), key=lambda x: x[1], reverse=True):
                st.progress(count / max(contact_stats.values()) if max(contact_stats.values()) > 0 else 0)
                st.write(f"**{name}**: {count} messages")
        else:
            st.info("Aucune statistique disponible")
    
    with col2:
        st.markdown("#### ⭐ Top contacts")
        if contact_stats:
            top_3 = sorted(contact_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            
            medals = ["🥇", "🥈", "🥉"]
            for i, (name, count) in enumerate(top_3):
                st.markdown(f"{medals[i]} **{name}** - {count} messages")
        else:
            st.info("Aucun contact actif")
    
    st.divider()
    
    if ai_service.enabled and "ai_analyses" in data and data["ai_analyses"]:
        st.markdown("#### 🤖 Analyse des sentiments")
        
        sentiments = {"positif": 0, "négatif": 0, "neutre": 0}
        for analysis in data["ai_analyses"]:
            sent = analysis.get("sentiment", {}).get("sentiment", "neutre")
            if sent in sentiments:
                sentiments[sent] += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positifs", sentiments["positif"])
        with col2:
            st.metric("😐 Neutres", sentiments["neutre"])
        with col3:
            st.metric("😔 Négatifs", sentiments["négatif"])
        
        total_analyzed = sum(sentiments.values())
        if total_analyzed > 0:
            positive_rate = (sentiments["positif"] / total_analyzed) * 100
            st.progress(positive_rate / 100)
            st.write(f"**Taux de positivité**: {positive_rate:.1f}%")
    
    st.divider()
    
    st.markdown("#### 📅 Activité récente")
    
    today = datetime.now().date()
    last_7_days = {}
    
    for i in range(7):
        day = today - timedelta(days=i)
        last_7_days[day.strftime("%d/%m")] = 0
    
    for msg in my_sent + my_received:
        try:
            msg_date = datetime.strptime(msg["timestamp"][:10], "%Y-%m-%d").date()
            day_str = msg_date.strftime("%d/%m")
            if day_str in last_7_days:
                last_7_days[day_str] += 1
        except:
            pass
    
    if any(last_7_days.values()):
        for day, count in reversed(list(last_7_days.items())):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(day)
            with col2:
                st.progress(count / max(last_7_days.values()) if max(last_7_days.values()) > 0 else 0)
                st.caption(f"{count} messages")
    else:
        st.info("Aucune activité ces 7 derniers jours")

# =============================
# FOOTER
# =============================
st.divider()
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown("""
    <p style='text-align: center; color: #667eea; font-size: 0.9rem;'>
    Made with ❤️ by Collabo Team<br>
    🤖 Powered by AI • 🔒 Secure • ⚡ Fast
    </p>
    """, unsafe_allow_html=True)
```

