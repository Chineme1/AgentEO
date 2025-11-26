import torch
import pickle
from config import TOKENIZER_PATH, MODEL_WEIGHTS, NUM_WORDS, MAX_LEN, CATEGORIES
from model.LSTM_classifier import LSTMEmailClassifier
from model.tokenizer import EmailTokenizer
import numpy as np

#creates the LSTM model agent for us to use
class ModelAgent:
    #basically decides what to use for your device to run the model
    def __init__(self, device="cpu"):
        self.device = torch.device(device)
        # load tokenizer (basically text -> sequences)
        self.tokenizer = EmailTokenizer(num_words=NUM_WORDS, max_len=MAX_LEN)
        self.tokenizer.load(TOKENIZER_PATH)

        # this is where the LSTM model is actually getting built 
        vocab_size = NUM_WORDS + 2   # + OOV, padding
        self.model = LSTMEmailClassifier(vocab_size=vocab_size, embed_dim=128, hidden_dim=128, output_dim=len(CATEGORIES))
        self.model.load_state_dict(torch.load(MODEL_WEIGHTS, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        self.CATEGORIES = CATEGORIES

    #takes the tokenized sequence and does a forward pass on the model to get the best score to be returned, in this case the best predicted label for the category
    def classify(self, email_text):
        seq = self.tokenizer.encode(email_text)  # returns numpy array (1, max_len)
        x = torch.tensor(seq, dtype=torch.long).to(self.device)
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)
            pred = torch.argmax(probs, dim=1).item()
        return self.CATEGORIES[pred]
