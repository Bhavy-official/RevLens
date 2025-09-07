from django.core.management.base import BaseCommand
from core.models import Review
from datetime import datetime
import re

class Command(BaseCommand):
    help = "Lightweight clean and normalize review data."

    def handle(self, *args, **kwargs):
        reviews = Review.objects.all().order_by("id")
        cleaned_count = 0
        skipped_count = 0

        for review in reviews:
            # Skip really empty reviews
            if not review.text or len(review.text.strip()) < 5:
                skipped_count += 1
                continue

            # Normalize review text
            review.text = re.sub(r"\s+", " ", review.text.strip())
            review.text = re.sub(r"[^\x00-\x7F]+", "", review.text)

            # Normalize title
            if review.title:
                review.title = re.sub(r"\s+", " ", review.title.strip())

            # Normalize reviewer name
            if review.reviewer:
                review.reviewer = review.reviewer.strip().title()

            # Normalize rating
            try:
                rating = float(review.rating)
                if not (1.0 <= rating <= 5.0):
                    skipped_count += 1
                    continue
            except (TypeError, ValueError):
                skipped_count += 1
                continue

            # Normalize date if possible
            if review.review_date and "-" not in review.review_date:
                try:
                    parsed_date = datetime.strptime(review.review_date, "%d %b %Y")
                    review.review_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass  # keep original if parsing fails

            review.save()
            cleaned_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Cleaned {cleaned_count} reviews, skipped {skipped_count} invalid/empty ones."
        ))
