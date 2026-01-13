# user_service.py
import os
import json
import hashlib

DATA_DIR = "./data"
USERS_FILE = f"{DATA_DIR}/users.json"
os.makedirs(DATA_DIR, exist_ok=True)

class UserService:
    """Service pour gérer les utilisateurs"""

    def __init__(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump([], f)

    def hash_password(self, password: str):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, email: str, password: str):
        users = self.get_all_users()
        if any(u["email"] == email for u in users):
            return False, "Email déjà utilisé"
        user = {
            "username": username,
            "email": email,
            "password": self.hash_password(password),
            "contacts": []
        }
        users.append(user)
        self.save_all_users(users)
        return True, "Utilisateur créé"

    def login_user(self, email: str, password: str):
        users = self.get_all_users()
        for u in users:
            if u["email"] == email and u["password"] == self.hash_password(password):
                return True, u
        return False, "Email ou mot de passe incorrect"

    def get_all_users(self):
        with open(USERS_FILE, "r") as f:
            return json.load(f)

    def save_all_users(self, users):
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
