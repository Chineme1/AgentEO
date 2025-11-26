#takes a summary and labels it accordingly based off score
class SummaryLabeler:
    CATEGORIES = {
        "Shopping": ["order", "shipment", "delivery", "purchase", "amazon", "tracking"],
        "Bills": ["bill", "due", "invoice", "payment", "statement"],
        "School": ["assignment", "lecture", "professor", "course", "university"],
        "Projects": ["meeting", "deadline", "project", "task"],
        "Personal": ["hey", "family", "friend", "let's", "catch up"],
        "Receipts": ["receipt", "transaction", "confirmation"],
    }

    def label_from_summary(self, summary):
        text = summary.lower()

        scores = {cat: 0 for cat in self.CATEGORIES}
        for cat, kw_list in self.CATEGORIES.items():
            for kw in kw_list:
                if kw in text:
                    scores[cat] += 1

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Other"
