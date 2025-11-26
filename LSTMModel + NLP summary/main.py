from config import IMAP_HOST, EMAIL_USER, EMAIL_PASS
from agents.perception import PerceptionAgent
from agents.LSTMagent import ModelAgent
from agents.decision import DecisionAgent
from agents.memory import MemoryAgent
from gmail_actions.apply_label import apply_label

#the main loop to basically get everything and creates the agent for the user to interact with 
def run_agent(limit=10):
    perception = PerceptionAgent(IMAP_HOST, EMAIL_USER, EMAIL_PASS)
    model_agent = ModelAgent(device="cpu")
    decision = DecisionAgent()
    memory = MemoryAgent()

    #gets the email and processes them
    emails = perception.fetch_inbox(limit=limit)
    for e in emails:
        text = (e.get("subject","") + " " + e.get("body","")).strip()[:10000]
        print("\n---")
        print("From:", e.get("from"))
        print("Subject:", e.get("subject"))
        # memory check
        mem_cat = memory.check_memory(e)
        if mem_cat:
            category = mem_cat
            print("Memory override:", category)
        else:
            category = model_agent.classify(text)
            print("Model predicted:", category)

        label = decision.decide_label(category)
        print("Applying label:", label)
        apply_label(e["id"], label, IMAP_HOST, EMAIL_USER, EMAIL_PASS)

        # Feedback: simple interactive loop
        ans = input(f"Is '{category}' correct? (y/n) ").strip().lower()
        if ans == "n":
            new_cat = input("Enter correct category (Shopping,Bills,School,Projects,Personal,Receipts,Other): ").strip()
            if new_cat not in decision.label_map:
                print("Unknown category, skipping memory save.")
            else:
                memory.save({
                    "email_id": e["id"],
                    "subject_keyword": e.get("subject","").split()[0] if e.get("subject") else "",
                    "correct_category": new_cat
                })
                print("Saved correction to memory")

if __name__ == "__main__":
    run_agent(limit=10)
