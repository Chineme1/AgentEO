# agents/auto_labeler.py

import re

class AutoLabeler:
    """
    Weak labeling heuristic to auto-label emails before training.
    This gives the LSTM a starting point.
    """

    def __init__(self):
        # Keyword dictionaries
        self.rules = {
            "Shopping": [
                "order", "shipped", "delivery", "amazon", "ebay",
                "sale", "coupon", "tracking", "purchase"
            ],
            "Bills": [
                "bill", "due", "payment", "invoice", "statement",
                "past due", "amount due", "utility"
            ],
            "School": [
                "assignment", "exam", "class", "professor", "university",
                "course", "homework", "syllabus", "lecture"
            ],
            "Projects": [
                "meeting", "deadline", "project", "task",
                "update", "deliverable", "client"
            ],
            "Personal": [
                "hey", "how are you", "let's meet", "dinner",
                "call me", "family", "friend", "hang out"
            ],
            "Receipts": [
                "receipt", "refunded", "confirmation",
                "transaction", "paid", "payment received"
            ],
        }

    def label_email(self, subject, body):
        text = (subject + " " + body).lower()

        # Try each category and count matches
        scores = {cat: 0 for cat in self.rules}

        for category, keywords in self.rules.items():
            for kw in keywords:
                if kw in text:
                    scores[category] += 1
        
        # Pick the highest scoring category
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "Other"
        return best
