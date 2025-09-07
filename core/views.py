# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.db.models import Count
# from .models import Product, Review, CriticalIssue
# from .forms import ProductAddForm
# from .services import (
#     ingest_reviews_for_pid,
#     run_sentiment_for_product,
#     run_critical_issues_for_product,
#     product_stats,
# )

# def products_home(request):
#     # Sidebar list: products with review counts
#     products = Product.objects.annotate(n_reviews=Count("review")).order_by("-id")

#     # If there are products, show latest one on landing
#     current = products.first() if products else None
#     issues = CriticalIssue.objects.filter(product=current).order_by("-frequency")[:5] if current else []
#     reviews = Review.objects.filter(product=current).order_by("-id")[:10] if current else []

#     context = {
#         "products": products,
#         "current": current,
#         "issues": issues,
#         "reviews": reviews,
#         "stats": product_stats(current) if current else {"total":0,"avg_rating":0,"positive":0,"negative":0},
#         "form": ProductAddForm(),
#     }
#     return render(request, "dashboard.html", context)

# def add_product(request):
#     if request.method == "POST":
#         form = ProductAddForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data["name"]
#             pid  = form.cleaned_data["pid"]
#             product, created = Product.objects.get_or_create(name=name)

#             try:
#                 saved = ingest_reviews_for_pid(product, pid, max_pages=4)
#                 analyzed = run_sentiment_for_product(product)
#                 issues = run_critical_issues_for_product(product)
#                 messages.success(request, f"Added {name}: {saved} reviews, analyzed {analyzed}, found {issues} critical issues.")
#             except Exception as e:
#                 messages.error(request, f"Failed: {e}")
#             return redirect("product_detail", product_id=product.id)
#         else:
#             messages.error(request, "Invalid form.")
#     return redirect("products_home")

# def product_detail(request, product_id: int):
#     product = get_object_or_404(Product, id=product_id)
#     products = Product.objects.annotate(n_reviews=Count("review")).order_by("-id")

#     issues = CriticalIssue.objects.filter(product=product).order_by("-frequency")[:5]
#     reviews = Review.objects.filter(product=product).order_by("-id")[:10]

#     context = {
#         "products": products,
#         "current": product,
#         "issues": issues,
#         "reviews": reviews,
#         "stats": product_stats(product),
#         "form": ProductAddForm(),
#     }
#     return render(request, "dashboard.html", context)

# def rescrape_product(request, product_id: int):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == "POST":
#         pid = request.POST.get("pid")
#         if not pid:
#             messages.error(request, "Provide PID to rescrape.")
#             return redirect("product_detail", product_id=product.id)
#         try:
#             saved = ingest_reviews_for_pid(product, pid, max_pages=4)
#             analyzed = run_sentiment_for_product(product)
#             issues = run_critical_issues_for_product(product)
#             messages.success(request, f"Re-scraped: {saved} new reviews, analyzed {analyzed}, issues {issues}.")
#         except Exception as e:
#             messages.error(request, f"Failed: {e}")
#     return redirect("product_detail", product_id=product.id)


# from django.shortcuts import redirect, get_object_or_404
# from django.contrib import messages
# from .models import Product
# from .services import run_sentiment_for_product, run_critical_issues_for_product

# def run_sentiment_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == "POST":
#         try:
#             analyzed = run_sentiment_for_product(product)
#             messages.success(request, f"Sentiment analysis done: {analyzed} reviews analyzed.")
#         except Exception as e:
#             messages.error(request, f"Failed: {e}")
#     return redirect("product_detail", product_id=product.id)

# def run_critical_issues_view(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == "POST":
#         try:
#             issues = run_critical_issues_for_product(product)
#             messages.success(request, f"Critical issues detected: {issues} issues found.")
#         except Exception as e:
#             messages.error(request, f"Failed: {e}")
#     return redirect("product_detail", product_id=product.id)





from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")


# core/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Product

from django.http import JsonResponse
from core.models import Product

# core/views.py
from django.http import JsonResponse
from core.models import Product
from core.scraper.flipkart import scrape_flipkart_reviews
from core.models import Review
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_product(request):
    pid = request.GET.get("pid")
    name = request.GET.get("name")

    if not pid or not name:
        return JsonResponse({"error": "pid and name are required"}, status=400)

    product, created = Product.objects.get_or_create(pid=pid, defaults={"name": name})
    if not created:
        return JsonResponse({"message": "Product already exists"}, status=200)

    return JsonResponse({
        "message": "Product added successfully",
        "product": {"pid": product.pid, "name": product.name}
    }, status=201)


@csrf_exempt
def scrape_product(request):
    pid = request.GET.get("pid")
    name = request.GET.get("name")
    if not pid or not name:
        return JsonResponse({"error": "pid and name required"}, status=400)

    # Ensure product exists
    product, _ = Product.objects.get_or_create(pid=pid, defaults={"name": name})

    reviews = scrape_flipkart_reviews(pid, max_pages=2)  # smaller for testing
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

    return JsonResponse({"message": f"{len(reviews)} reviews scraped for {product.name}"})
