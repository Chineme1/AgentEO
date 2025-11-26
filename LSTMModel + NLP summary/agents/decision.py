from config import LABEL_MAP

#takes the category predicted by LSTM andconverts it into the actual Gmail/IMAP label string in order to apply it to the email.

class DecisionAgent:
    def __init__(self, label_map=LABEL_MAP):
        self.label_map = label_map

    def decide_label(self, category):
        return self.label_map.get(category, "Label_Other")
