# model/tokenizer.py
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

class EmailTokenizer:
    def __init__(self, num_words=20000, max_len=300):
        self.num_words = num_words
        self.max_len = max_len
        self.tok = Tokenizer(num_words=num_words, oov_token="<OOV>")

    def fit(self, texts):
        self.tok.fit_on_texts(texts)

    def save(self, path="model/tokenizer.pkl"):
        with open(path, "wb") as f:
            pickle.dump(self.tok, f)

    def load(self, path="model/tokenizer.pkl"):
        with open(path, "rb") as f:
            self.tok = pickle.load(f)

    def encode(self, text):
        seq = self.tok.texts_to_sequences([text])
        seq = pad_sequences(seq, maxlen=self.max_len, padding="post", truncating="post")
        return seq
