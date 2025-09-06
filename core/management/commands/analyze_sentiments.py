# core/management/commands/analyze_sentiments.py
from django.core.management.base import BaseCommand
from transformers import pipeline
from core.models import Review
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)

class Command(BaseCommand):
    help = "Analyze sentiment for all reviews with sentence-level weighting"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔍 Starting sentiment analysis...")

        classifier = pipeline("sentiment-analysis", device=-1)
        reviews = Review.objects.all()
        updated_count = 0

        for review in reviews:
            if not review.text:
                continue

            sentences = sent_tokenize(review.text)
            results = classifier(sentences)

            # Compute weighted score: POSITIVE = score, NEGATIVE = 1 - score
            weighted_scores = []
            for r in results:
                if r["label"] == "POSITIVE":
                    weighted_scores.append(r["score"])
                else:
                    weighted_scores.append(1 - r["score"])

            # Final sentiment
            avg_score = sum(weighted_scores) / len(weighted_scores)
            final_sentiment = "positive" if avg_score >= 0.5 else "negative"

            # Save to DB
            review.sentiment = final_sentiment
            review.sentiment_score = avg_score
            review.save(update_fields=["sentiment", "sentiment_score"])

            print(f"{review.reviewer[:20]}... | Sentiment: {final_sentiment} | Score: {avg_score:.2f}")
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Sentiment analysis completed for {updated_count} reviews."))
