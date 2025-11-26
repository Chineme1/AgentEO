import os
import json
from agents.perception import PerceptionAgent
from agents.summarizer import ExtractiveSummarizer
from agents.summary_labeler import SummaryLabeler
from config import IMAP_HOST, EMAIL_USER, EMAIL_PASS, DATA_DIR

os.makedirs(DATA_DIR, exist_ok=True)

OUT_PATH = os.path.join(DATA_DIR, "fetched_emails.json")
LABELED_OUT = os.path.join(DATA_DIR, "auto_labeled_emails.json")

#gets the emails from inbox
def run_fetch(limit=50):
    print("Initializing agents...")
    p = PerceptionAgent(IMAP_HOST, EMAIL_USER, EMAIL_PASS)
    summarizer = ExtractiveSummarizer()
    labeler = SummaryLabeler()

    print("Fetching emails...")
    emails = p.fetch_inbox(limit=limit)

    if len(emails) == 0:
        print("ERROR: No emails were fetched. JSON files will not be written.")
        return

    # Save raw fetched emails
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(emails, f, indent=2)
    print(f"Saved raw emails to {OUT_PATH}")

    print("Generating summaries and labeling emails...")
    labeled = []

    #summarize the emails and get the corresponding predicted label
    for e in emails:
        subject = e.get("subject", "") or ""
        body = e.get("body", "") or ""
        full_text = (subject + "\n" + body).strip()

        summary = summarizer.summarize(full_text)
        e["summary"] = summary

        label = labeler.label_from_summary(summary)
        e["label"] = label

        labeled.append(e)

    # Save labeled dataset
    with open(LABELED_OUT, "w", encoding="utf-8") as f:
        json.dump(labeled, f, indent=2)

    print(f"Labeled {len(labeled)} emails.")
    print(f"Labeled dataset saved to {LABELED_OUT}")
    print("You can now run train.py to train the LSTM model.")


if __name__ == "__main__":
    run_fetch(limit=300)
