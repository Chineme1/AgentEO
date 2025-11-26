# agents/decision.py
from config import LABEL_MAP

class DecisionAgent:
    def __init__(self, label_map=LABEL_MAP):
        self.label_map = label_map

    def decide_label(self, category):
        return self.label_map.get(category, "Label_Other")
