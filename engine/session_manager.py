import uuid
from collections import deque
from typing import Dict, List, Optional

# Configurable max memory per session
MAX_HISTORY = 5  # keep last 5 exchanges

# In-memory store for all user sessions
session_store: Dict[str, deque] = {}

def start_session() -> str:
    """Starts a new session and returns its ID"""
    session_id = str(uuid.uuid4())
    session_store[session_id] = deque(maxlen=MAX_HISTORY)
    return session_id

def get_session_history(session_id: str) -> List[Dict]:
    """Returns the query/response history for a session"""
    return list(session_store.get(session_id, []))

def add_to_session(session_id: str, user_query: str, system_response: Dict):
    """Adds an interaction to session history"""
    if session_id not in session_store:
        session_store[session_id] = deque(maxlen=MAX_HISTORY)
    session_store[session_id].append({
        "query": user_query,
        "response": system_response
    })

def get_last_decision(session_id: str) -> Optional[Dict]:
    """Returns the last system decision from the session (if any)"""
    history = session_store.get(session_id)
    if history:
        return history[-1].get("response")
    return None

# 🧪 Example
if __name__ == "__main__":
    sid = start_session()
    print("🔑 Session ID:", sid)

    q = "46M, knee surgery, 3-month policy"
    r = {"decision": "approved", "amount": 40000, "justification": "Clause 12 applies"}
    add_to_session(sid, q, r)

    print("📜 Session History:", get_session_history(sid))
    print("🔁 Last Decision:", get_last_decision(sid))
