from django.core.management.base import BaseCommand
from core.models import Review
from datetime import datetime
import re

class Command(BaseCommand):
    help = "Clean and normalize review data without wiping fields like location or title."

    def handle(self, *args, **kwargs):
        reviews = Review.objects.all().order_by("id")
        seen = set()
        cleaned_count = 0
        deleted_count = 0

        for review in reviews:
            original_text = review.text

            # 1. Skip empty or too-short reviews
            if not review.text or len(review.text.strip()) < 5:
                review.delete()
                deleted_count += 1
                continue

            # 2. Clean text
            cleaned_text = re.sub(r"\s+", " ", review.text.strip())
            cleaned_text = re.sub(r"[^\x00-\x7F]+", "", cleaned_text)

            # 3. Deduplication key
            key = (review.reviewer.lower() if review.reviewer else "anon", cleaned_text.lower())
            if key in seen:
                review.delete()
                deleted_count += 1
                continue
            seen.add(key)

            # 4. Clean title and reviewer without overwriting valid data
            if review.title:
                review.title = re.sub(r"\s+", " ", review.title.strip())
            if review.reviewer:
                review.reviewer = review.reviewer.strip().title()

            # 5. Validate rating
            try:
                if review.rating is None or not (1.0 <= float(review.rating) <= 5.0):
                    review.delete()
                    deleted_count += 1
                    continue
            except (ValueError, TypeError):
                review.delete()
                deleted_count += 1
                continue

            # 6. Normalize date (only if not already in YYYY-MM-DD format)
            if review.review_date and "-" not in review.review_date:
                try:
                    parsed_date = datetime.strptime(review.review_date, "%d %b %Y")
                    review.review_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass  # keep original if parsing fails

            # ✅ Save safely (without wiping other fields)
            review.text = cleaned_text
            review.save()  # <-- NO update_fields here
            cleaned_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Cleaned {cleaned_count} reviews, deleted {deleted_count} invalid/duplicate reviews."
        ))
