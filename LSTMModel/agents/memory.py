# agents/memory.py
import json
import os

class MemoryAgent:
    def __init__(self, path="memory.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f, indent=2)

    def load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def save(self, entry):
        # entry example: {"email_id": "123", "subject_keyword": "invoice", "correct_category":"Bills"}
        data = self.load()
        data.append(entry)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def check_memory(self, email_data):
        """
        Very simple check: if subject_keyword appears in subject, return corrected category.
        """
        data = self.load()
        subj = email_data.get("subject", "").lower()
        for entry in data:
            kw = entry.get("subject_keyword", "").lower()
            if kw and kw in subj:
                return entry.get("correct_category")
        return None
