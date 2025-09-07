# core/management/commands/scrape_flipkart.py
from django.core.management.base import BaseCommand
from core.models import Product, Review
from core.scraper.flipkart import scrape_flipkart_reviews

class Command(BaseCommand):
    help = 'Scrape Flipkart reviews and save to DB'

    def add_arguments(self, parser):
        parser.add_argument('product_pid', type=str, help='Flipkart product PID')
        parser.add_argument('product_name', type=str, help='Name of the product')

    def handle(self, *args, **kwargs):
        product_pid = kwargs['product_pid']
        product_name = kwargs['product_name']

        product, created = Product.objects.get_or_create(name=product_name)
        if created:
            print(f"[DEBUG] Created new Product: {product_name}")

        reviews = scrape_flipkart_reviews(product_pid, max_pages=4)

        for r in reviews:
            Review.objects.create(
                product=product,
                reviewer=r['reviewer_name'],
                rating=r['rating'],
                verified=True,
                text=r['review_text'],
                title=r['title'],
                location=r['location'],
                review_date=r['date'],
                category="product",
            )
            print(f"[DEBUG] Saved review: {r['reviewer_name']} - {r['rating']}")
