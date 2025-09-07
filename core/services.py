from .models import Product, Review, CriticalIssue
from .scraper.flipkart import scrape_flipkart_reviews
from django.db.models import Avg, Count
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import nltk

# Safe on Windows: download quietly
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

def ingest_reviews_for_pid(product: Product, pid: str, max_pages: int = 4) -> int:
    """
    Scrape reviews by PID and store them. Returns count saved.
    """
    data = scrape_flipkart_reviews(pid, max_pages=max_pages)
    saved = 0
    for r in data:
        Review.objects.create(
            product=product,
            reviewer=r.get('reviewer_name') or 'No name',
            rating=float(r.get('rating') or 0) or 0.0,
            verified=True,
            text=r.get('review_text') or '',
            title=r.get('title') or '',
            location=r.get('location') or '',
            review_date=r.get('date') or '',
        )
        saved += 1
    return saved

def run_sentiment_for_product(product: Product) -> int:
    """
    Run sentence-level aggregation -> store review-level sentiment + score.
    """
    clf = pipeline("sentiment-analysis", device=-1)

    updated = 0
    for review in Review.objects.filter(product=product):
        if not review.text:
            continue
        sents = sent_tokenize(review.text)
        if not sents:
            continue

        results = clf(sents)
        # majority + mean confidence of winning class
        pos_scores = [r["score"] for r in results if r["label"] == "POSITIVE"]
        neg_scores = [r["score"] for r in results if r["label"] == "NEGATIVE"]
        positive = len(pos_scores)
        negative = len(neg_scores)

        if positive >= negative:
            review.sentiment = "positive"
            review.sentiment_score = sum(pos_scores)/len(pos_scores) if pos_scores else 0.0
        else:
            review.sentiment = "negative"
            review.sentiment_score = sum(neg_scores)/len(neg_scores) if neg_scores else 0.0

        review.save(update_fields=["sentiment", "sentiment_score"])
        updated += 1
    return updated

def run_critical_issues_for_product(product: Product) -> int:
    """
    Simple critical-issue detector (negative, product-related sentences → top phrases).
    Uses a lightweight heuristic so demo works without huge infra.
    """
    from collections import Counter
    import re

    neg_texts = list(
        Review.objects.filter(product=product, sentiment="negative")
        .values_list("text", flat=True)
    )

    if not neg_texts:
        return 0

    # naive key-phrase extraction: frequent 1–2 word nouns-like tokens
    # (you can replace with KeyBERT later; this is hackathon-friendly)
    blob = " ".join(neg_texts).lower()
    # keep words only
    words = re.findall(r"[a-z]{3,}", blob)
    stop = {
        "the","and","this","that","with","from","have","been","just","very","also","but","are",
        "too","not","for","you","your","was","has","had","its","they","them","their","there",
        "after","more","less","when","where","which","then","than","what","why","how","can","could",
        "would","should","may","might","did","does","done","into","over","under","onto","upon"
    }
    words = [w for w in words if w not in stop]

    # make 1-2 gram counts
    unigrams = Counter(words)
    bigrams = Counter([" ".join(t) for t in zip(words, words[1:])])

    # merge and pick top few that look like product issues
    merged = (unigrams + bigrams)
    # filter out generic words that kept showing up
    ban = {"good","great","nice","awesome","perfect","amazing","product","quality"}
    candidates = [(k, v) for k, v in merged.items() if k not in ban]
    candidates.sort(key=lambda kv: kv[1], reverse=True)

    CriticalIssue.objects.filter(product=product).delete()
    saved = 0
    for phrase, freq in candidates[:5]:
        CriticalIssue.objects.create(
            product=product,
            phrase=phrase,
            frequency=freq,
            aspect="product",  # upgrade later with a zero-shot tagger
            avg_sentiment_score=0.0,  # can compute from contributing reviews later
        )
        saved += 1
    return saved

def product_stats(product: Product) -> dict:
    qs = Review.objects.filter(product=product)
    total = qs.count()
    avg = qs.aggregate(avg=Avg("rating"))["avg"] or 0
    pos = qs.filter(sentiment="positive").count()
    neg = qs.filter(sentiment="negative").count()
    return {
        "total": total,
        "avg_rating": round(avg, 2),
        "positive": pos,
        "negative": neg,
    }
