from langchain_core.messages import HumanMessage, AIMessage
from loguru import logger
from typing import Optional
import json
import os

MEMORY_DIR = "data/memory"

class MemoryManager:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.sessions = {}

    def _get_session_path(self, session_id: str) -> str:
        return f"{MEMORY_DIR}/{session_id}.json"

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({
            "role": role,
            "content": content[:500]
        })
        # Keep last 10 messages only
        self.sessions[session_id] = self.sessions[session_id][-10:]
        self._save(session_id)

    def get_history(self, session_id: str) -> list:
        if session_id not in self.sessions:
            self._load(session_id)
        return self.sessions.get(session_id, [])

    def get_context_string(self, session_id: str) -> str:
        history = self.get_history(session_id)
        if not history:
            return ""
        context = "Previous conversation:\n"
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:200]}\n"
        return context

    def _save(self, session_id: str):
        path = self._get_session_path(session_id)
        with open(path, "w") as f:
            json.dump(self.sessions[session_id], f)

    def _load(self, session_id: str):
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.sessions[session_id] = json.load(f)

    def clear(self, session_id: str):
        self.sessions[session_id] = []
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            os.remove(path)

memory_manager = MemoryManager()