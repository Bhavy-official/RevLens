# core/utils.py
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import statistics

classifier = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device=-1
)

def analyze_sentiments_for_reviews(reviews):
    """
    Takes a queryset or list of Review objects and updates
    their sentiment and sentiment_score fields.
    Returns the number of reviews updated.
    """
    updated_count = 0
    for review in reviews:
        if not review.text:
            continue

        sentences = sent_tokenize(review.text)
        if not sentences:
            continue

        results = classifier(sentences, truncation=True)

        weighted_scores = []
        sentiments = []

        for r in results:
            score = r["score"]
            if r["label"] == "POSITIVE":
                sentiments.append(1)
                weighted_scores.append(score)
            else:
                sentiments.append(0)
                weighted_scores.append(1 - score)

        avg_score = statistics.mean(weighted_scores)
        median_score = statistics.median(weighted_scores)
        majority_vote = "positive" if sum(sentiments) >= len(sentiments)/2 else "negative"
        final_sentiment = "positive" if median_score >= 0.5 else majority_vote

        review.sentiment = final_sentiment
        review.sentiment_score = round(avg_score, 3)
        review.save(update_fields=["sentiment", "sentiment_score"])
        updated_count += 1

    return updated_count
