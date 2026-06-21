from typing import List, Dict
from textblob import TextBlob
import re
from collections import Counter
import nltk
from .celery_app import celery

# Ensure NLTK resources (for first-run environments) - safe to call repeatedly
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

STOPWORDS = set(nltk.corpus.stopwords.words('english'))


def _clean_and_tokenize(text: str) -> List[str]:
    text = text.lower()
    # simple tokenization
    tokens = re.findall(r"\b[a-z]{2,}\b", text)
    return tokens


@celery.task(bind=True)
def sentiment_analysis(self, text: str) -> Dict:
    """Return polarity and subjectivity using TextBlob."""
    blob = TextBlob(text)
    return {
        'polarity': round(blob.sentiment.polarity, 4),
        'subjectivity': round(blob.sentiment.subjectivity, 4),
    }


@celery.task(bind=True)
def extract_keywords(self, text: str, top_k: int = 5) -> Dict:
    """Return top_k keywords by frequency excluding stopwords."""
    tokens = _clean_and_tokenize(text)
    tokens = [t for t in tokens if t not in STOPWORDS]
    counts = Counter(tokens)
    most = counts.most_common(top_k)
    return {'keywords': [w for w, _ in most]}


@celery.task(bind=True)
def tokenize(self, text: str) -> Dict:
    tokens = _clean_and_tokenize(text)
    return {'tokens': tokens}
