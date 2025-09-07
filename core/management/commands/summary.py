# core/management/commands/summary.py
from django.core.management.base import BaseCommand, CommandError
from core.models import Product, Review
import re
from collections import Counter
import spacy

class Command(BaseCommand):
    help = "Generate generic review summary & critical issues"

    def add_arguments(self, parser):
        parser.add_argument('--pid', type=str, help="Product PID")
        parser.add_argument('--name', type=str, help="Product name (alt to PID)")

    def handle(self, *args, **options):
        pid = options.get('pid')
        name = options.get('name')

        if not pid and not name:
            raise CommandError("Please provide either --pid or --name")

        try:
            product = Product.objects.get(pid=pid) if pid else Product.objects.get(name=name)
        except Product.DoesNotExist:
            raise CommandError("Product not found")

        reviews = Review.objects.filter(product=product)
        if not reviews.exists():
            self.stdout.write(self.style.WARNING("No reviews found"))
            return

        nlp = spacy.load("en_core_web_sm")

        all_text = " ".join(r.text for r in reviews if r.text)
        doc = nlp(all_text)

        # extract noun chunks & count frequency
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 2]
        counts = Counter(noun_phrases)

        # get top 10 issues
        top_issues = counts.most_common(10)

        total_reviews = reviews.count()

        self.stdout.write(self.style.SUCCESS(f"Total Reviews: {total_reviews}\n"))
        for issue, count in top_issues:
            percent = round((count / total_reviews) * 100, 1)
            severity = (
                "High" if percent > 20
                else "Medium" if percent > 10
                else "Low"
            )
            self.stdout.write(
                f"{issue.title()}\n"
                f"Severity: {severity}\n"
                f"Mentioned in {count} reviews ({percent}%)\n"
            )

        self.stdout.write(self.style.SUCCESS("✅ Generic issue extraction complete"))
