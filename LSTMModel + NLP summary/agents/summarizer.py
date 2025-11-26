import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import defaultdict
import math

# Download required tokenizers safely
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

#basically splits the email into sentences, gets the word frequency across all the emails, chooses the highest score sentences and outputs those 
class ExtractiveSummarizer:
    def summarize(self, text, max_sentences=2):
        sentences = sent_tokenize(text)
        if len(sentences) <= max_sentences:
            return text

        # Frequency table
        words = word_tokenize(text.lower())
        freq = defaultdict(int)
        for w in words:
            if w.isalpha():
                freq[w] += 1

        # Sentence scores
        scores = []
        for sent in sentences:
            sent_words = word_tokenize(sent.lower())
            score = sum(freq[w] for w in sent_words if w.isalpha())
            scores.append((score, sent))

        # Pick top sentences
        scores.sort(reverse=True)
        summary = " ".join([s for _, s in scores[:max_sentences]])
        return summary
