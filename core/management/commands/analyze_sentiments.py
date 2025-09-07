# core/management/commands/analyze_sentiments.py
from django.core.management.base import BaseCommand
from transformers import pipeline
from core.models import Review
from nltk.tokenize import sent_tokenize
import nltk
import statistics

nltk.download("punkt", quiet=True)

class Command(BaseCommand):
    help = "Analyze sentiment for all reviews with robust sentence-level analysis"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔍 Starting sentiment analysis...")

        # ✅ Use a stable, recommended model (not default)
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )

        reviews = Review.objects.all()
        updated_count = 0

        for review in reviews:
            if not review.text:
                continue

            # Split into sentences
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

            # ✅ Use median for robustness against extreme sentences
            avg_score = statistics.mean(weighted_scores)
            median_score = statistics.median(weighted_scores)

            # ✅ Final sentiment decision based on both average + majority vote
            majority_vote = "positive" if sum(sentiments) >= len(sentiments) / 2 else "negative"
            final_sentiment = "positive" if median_score >= 0.5 else majority_vote

            review.sentiment = final_sentiment
            review.sentiment_score = round(avg_score, 3)
            review.save(update_fields=["sentiment", "sentiment_score"])

            print(
                f"📄 {review.reviewer[:20]}... | "
                f"Sentiment: {final_sentiment.upper()} | "
                f"Avg: {avg_score:.2f}, Median: {median_score:.2f}"
            )
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Sentiment analysis completed for {updated_count} reviews.")
        )
