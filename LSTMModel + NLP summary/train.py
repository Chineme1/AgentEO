import os
import json
import random
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader
from torch import optim
import torch.nn.functional as F
from tqdm import tqdm

from config import DATA_DIR, MODEL_DIR, NUM_WORDS, MAX_LEN, EMBED_DIM, HIDDEN_DIM, NUM_CLASSES, CATEGORIES, TOKENIZER_PATH, MODEL_WEIGHTS
from model.tokenizer import EmailTokenizer
from model.utils import EmailDataset
from model.LSTM_classifier import LSTMEmailClassifier

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

#gets the labeled emails based off the summaries in order to train them
def load_labeled_emails(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = []
    labels = []
    for e in data:
        if "label" in e and e["label"] in CATEGORIES:
            texts.append(e.get("summary", "").strip())
            labels.append(CATEGORIES.index(e["label"]))
    return texts, labels

#train the LSTM to predict labels according to summaries and labels it has
def train(json_path, epochs=5, batch_size=32, lr=1e-3, device="cpu"):
    texts, labels = load_labeled_emails(json_path)
    if len(texts) == 0:
        raise RuntimeError("No labeled data found. Please label some emails in data/fetched_emails.json (add 'label').")

    # Shuffle
    combined = list(zip(texts, labels))
    random.shuffle(combined)
    texts, labels = zip(*combined)

    # tokenizer
    tokenizer = EmailTokenizer(num_words=NUM_WORDS, max_len=MAX_LEN)
    tokenizer.fit(texts)
    tokenizer.save(TOKENIZER_PATH)
    print("Tokenizer saved to", TOKENIZER_PATH)

    sequences = []
    for t in texts:
        seq = tokenizer.encode(t)[0]   # returns (1, max_len)
        sequences.append(seq)
    sequences = np.array(sequences)
    labels = np.array(labels)

    X_train, X_val, y_train, y_val = train_test_split(sequences, labels, test_size=0.15, random_state=42)

    train_ds = EmailDataset(X_train, y_train)
    val_ds = EmailDataset(X_val, y_val)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    device = torch.device(device)
    model = LSTMEmailClassifier(vocab_size=NUM_WORDS+2, embed_dim=EMBED_DIM, hidden_dim=HIDDEN_DIM, output_dim=NUM_CLASSES)
    model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0.0
        for Xb, yb in tqdm(train_loader, desc=f"Epoch {epoch} train"):
            Xb = Xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = model(Xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()*Xb.size(0)
        avg_loss = total_loss / len(train_ds)
        print(f"Epoch {epoch} train loss: {avg_loss:.4f}")

        # validation
        model.eval()
        total = 0
        correct = 0
        with torch.no_grad():
            for Xb, yb in val_loader:
                Xb = Xb.to(device)
                yb = yb.to(device)
                logits = model(Xb)
                preds = torch.argmax(logits, dim=1)
                total += yb.size(0)
                correct += (preds == yb).sum().item()
        acc = correct/total
        print(f"Epoch {epoch} val acc: {acc:.4f}")

        # save checkpoint
        torch.save(model.state_dict(), MODEL_WEIGHTS)
        print(f"Saved model to {MODEL_WEIGHTS}")

if __name__ == "__main__":
    # Expects labeled data in data/fetched_emails.json with 'label' field
    JSON = os.path.join(DATA_DIR, "auto_labeled_emails.json")
    train(JSON, epochs=6, batch_size=32, lr=1e-3, device="cpu")
