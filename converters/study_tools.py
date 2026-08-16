import re
from collections import Counter
from pypdf import PdfReader


STOPWORDS = {
    "the", "is", "are", "and", "or", "to", "of", "in", "on", "for", "with",
    "a", "an", "this", "that", "it", "as", "by", "be", "from", "at", "was",
    "were", "has", "have", "had", "will", "can", "may", "you", "your", "we",
    "they", "he", "she", "them", "our", "but", "not", "if", "than", "then"
}


def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        parts.append(txt)
    text = "\n".join(parts).strip()
    if not text:
        raise Exception("No extractable text found in PDF.")
    return text


def _sentences(text):
    s = re.split(r'(?<=[.!?])\s+', text.replace("\n", " ").strip())
    return [x.strip() for x in s if len(x.strip()) > 20]


def _word_freq(text):
    words = re.findall(r"[A-Za-z']+", text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return Counter(words)


def generate_summary(text, max_sentences=8):
    sents = _sentences(text)
    if not sents:
        return "Could not generate summary."

    freq = _word_freq(text)
    scored = []
    for s in sents:
        score = sum(freq.get(w.lower(), 0) for w in re.findall(r"[A-Za-z']+", s))
        scored.append((score, s))

    best = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    # preserve readable order by original sentence index
    best_set = {b[1] for b in best}
    ordered = [s for s in sents if s in best_set]
    return " ".join(ordered)


def extract_key_points(text, n=10):
    sents = _sentences(text)
    if not sents:
        return []

    freq = _word_freq(text)
    scored = []
    for s in sents:
        score = sum(freq.get(w.lower(), 0) for w in re.findall(r"[A-Za-z']+", s))
        scored.append((score, s))

    best = sorted(scored, key=lambda x: x[0], reverse=True)[:n]
    return [b[1] for b in best]


def generate_important_questions(text, n=8):
    points = extract_key_points(text, n=n * 2)
    questions = []

    for p in points:
        # basic question templates
        clean = p.strip().rstrip(".")
        if len(clean) < 25:
            continue

        # Try to form varied questions
        questions.append(f"What is meant by: \"{clean}\"?")
        if len(questions) >= n:
            break
        questions.append(f"Explain the significance of: \"{clean}\".")
        if len(questions) >= n:
            break

    return questions[:n]