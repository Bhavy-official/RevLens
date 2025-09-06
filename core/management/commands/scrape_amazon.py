from django.core.management.base import BaseCommand
from core.models import Product, Review
from core.scraper.amazon import scrape_amazon_reviews

class Command(BaseCommand):
    help = "Scrape Amazon reviews for a product"

    def add_arguments(self, parser):
        parser.add_argument('product_url', type=str, help='Amazon product URL')

    def handle(self, *args, **options):
        product_url = options['product_url']
        self.stdout.write(f"[DEBUG] Starting scrape for: {product_url}")

        reviews = scrape_amazon_reviews(product_url)
        self.stdout.write(f"[DEBUG] Total reviews fetched: {len(reviews)}")

        if not reviews:
            self.stdout.write(self.style.WARNING("No reviews found"))
            return

        for r in reviews:
            Review.objects.create(
                product=None,  # set a Product instance if you want
                reviewer=r.get("reviewer", ""),
                text=r.get("text", ""),
                rating=r.get("rating"),
                date=r.get("date"),
                verified=r.get("verified", False)
            )

        self.stdout.write(self.style.SUCCESS(f"Scraped {len(reviews)} reviews for {product_url}"))
