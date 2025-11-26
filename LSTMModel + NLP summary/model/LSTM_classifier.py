import torch
import torch.nn as nn
import torch.nn.functional as F

#used to predict the label or category of an email given a tokenized file
class LSTMEmailClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim, padding_idx=0):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim, padding_idx=padding_idx)
        self.lstm = nn.LSTM(input_size=embed_dim, hidden_size=hidden_dim, batch_first=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        # x: (batch, seq_len)
        embedded = self.embedding(x)               # (batch, seq_len, embed_dim)
        outputs, (hn, cn) = self.lstm(embedded)    # hn: (num_layers * num_directions, batch, hidden_dim)
        last_hidden = hn[-1]                       # (batch, hidden_dim)
        out = self.dropout(last_hidden)
        logits = self.fc(out)
        return logits
