import torch
from torch.utils.data import Dataset
import numpy as np

#creates our dataset pretty much
class EmailDataset(Dataset):
    def __init__(self, sequences, labels):
        # sequences: numpy array (n, seq_len)
        # labels: list or array (n,)
        self.X = sequences.astype(np.int64)
        self.y = np.array(labels).astype(np.int64)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.long), torch.tensor(self.y[idx], dtype=torch.long)
