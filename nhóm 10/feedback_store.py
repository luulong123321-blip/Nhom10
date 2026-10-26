import json
import os
from datetime import datetime

FEEDBACK_FILE = os.path.join("data", "feedback.json")

def init_feedback_store():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def save_feedback(data):
    init_feedback_store()
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            feedbacks = json.load(f)
    except Exception:
        feedbacks = []
        
    data["timestamp"] = datetime.now().isoformat()
    feedbacks.append(data)
    
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)