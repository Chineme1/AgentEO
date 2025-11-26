# Update these before running, these are your settings.

IMAP_HOST = "imap.gmail.com"
EMAIL_USER = "royaliscool1214@gmail.com"
EMAIL_PASS = "iayyrjmwqrgpiqev"   # or load from env var
DATA_DIR = "data"
MODEL_DIR = "model"
TOKENIZER_PATH = f"{MODEL_DIR}/tokenizer.pkl"
MODEL_WEIGHTS = f"{MODEL_DIR}/model_weights.pth"

# LSTM model hyperparams (can tune)
NUM_WORDS = 20000
MAX_LEN = 300
EMBED_DIM = 128
HIDDEN_DIM = 128
NUM_CLASSES = 7  # Shopping, Bills, School, Projects, Personal, Receipts, Other

CATEGORIES = ["Shopping", "Bills", "School", "Projects", "Personal", "Receipts", "Other"]
LABEL_MAP = {cat: f"Label_{cat}" for cat in CATEGORIES}
