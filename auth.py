# auth.py
import json
import hashlib
from pathlib import Path

USERS_FILE = Path("users.json")

def load_users():
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    return {}

def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=2))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password)
    }
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username not in users:
        return False
    return users[username]["password"] == hash_password(password)