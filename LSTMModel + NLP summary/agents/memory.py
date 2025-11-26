import json
import os

#basically handles past classification mistakes and stores corrected labels
class MemoryAgent:
    #checks to see fi the json is even there for the agent to use 
    def __init__(self, path="memory.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f, indent=2)

    #loads the file
    def load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    #saves entries to the json
    def save(self, entry):
        # entry example: {"email_id": "123", "subject_keyword": "invoice", "correct_category":"Bills"}
        data = self.load()
        data.append(entry)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    #check to see if a subject keyword actually appears in the subject of the email, then returns the correct category
    def check_memory(self, email_data):
        data = self.load()
        subj = email_data.get("subject", "").lower()
        for entry in data:
            kw = entry.get("subject_keyword", "").lower()
            if kw and kw in subj:
                return entry.get("correct_category")
        return None
