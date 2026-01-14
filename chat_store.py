# chat_store.py
import json
from datetime import datetime
from pathlib import Path

MESSAGES_FILE = Path("messages.json")

def load_messages():
    if MESSAGES_FILE.exists():
        return json.loads(MESSAGES_FILE.read_text())
    return []

def save_messages(messages):
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2))

def add_message(sender, receiver, content):
    messages = load_messages()
    messages.append({
        "sender": sender,
        "receiver": receiver,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_messages(messages)

def get_conversation(user1, user2):
    return [
        m for m in load_messages()
        if {m["sender"], m["receiver"]} == {user1, user2}
    ]