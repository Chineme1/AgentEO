# build_dataset.py

import os
import json
from agents.perception import PerceptionAgent
from agents.autolabeler import AutoLabeler
from config import IMAP_HOST, EMAIL_USER, EMAIL_PASS, DATA_DIR

os.makedirs(DATA_DIR, exist_ok=True)
OUT_PATH = os.path.join(DATA_DIR, "fetched_emails.json")
LABELED_OUT = os.path.join(DATA_DIR, "auto_labeled_emails.json")

def run_fetch(limit=300):
    p = PerceptionAgent(IMAP_HOST, EMAIL_USER, EMAIL_PASS)
    auto = AutoLabeler()

    print("Fetching emails...")
    emails = p.fetch_inbox(limit=limit)

    # Save raw data
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(emails, f, indent=2)
    print(f"Saved raw fetch to {OUT_PATH}")

    print("Auto-labeling emails...")
    labeled = []
    for e in emails:
        subject = e.get("subject", "")
        body = e.get("body", "")
        label = auto.label_email(subject, body)
        e["label"] = label
        labeled.append(e)

    # Save auto-labeled dataset
    with open(LABELED_OUT, "w", encoding="utf-8") as f:
        json.dump(labeled, f, indent=2)

    print(f"Auto-labeled {len(labeled)} emails.")
    print(f"Saved auto-labeled dataset to {LABELED_OUT}")
    print("You can now train without manually labeling!")

if __name__ == "__main__":
    run_fetch(limit=300)
