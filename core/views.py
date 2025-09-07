# core/views.py

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Review
from .scraper.flipkart import scrape_flipkart_reviews
from .utils import analyze_sentiments_for_reviews


def dashboard(request):
    
    return render(request, "dashboard.html")


def product_list(request):
   
    products = Product.objects.all().values("pid", "name")
    return JsonResponse({"products": list(products)})


@csrf_exempt
def add_and_scrape_product(request):
   
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        pid = data.get("pid")
        name = data.get("name")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not pid or not name:
        return JsonResponse({"error": "pid and name are required"}, status=400)

    product, created = Product.objects.get_or_create(pid=pid, defaults={"name": name})
    message = "Product added successfully" if created else "Product already existed"

    # Scrape 
    reviews_data = scrape_flipkart_reviews(pid, max_pages=10)
    saved_reviews = []
    for r in reviews_data:
        rev = Review.objects.create(
            product=product,
            reviewer=r.get('reviewer_name') or "Anonymous",
            rating=r.get('rating') or 0,
            verified=True,
            text=r.get('review_text') or "",
            title=r.get('title') or "",
            location=r.get('location') or "",
            review_date=r.get('date'),
            category="product",
        )
        saved_reviews.append(rev)

  
    analyzed_count = analyze_sentiments_for_reviews(saved_reviews)

    return JsonResponse({
        "message": message,
        "product": {"pid": product.pid, "name": product.name},
        "reviews_scraped": len(reviews_data),
        "sentiment_analyzed": analyzed_count
    })


def dashboard_data(request, pid):
    try:
        product = Product.objects.get(pid=pid)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    reviews = Review.objects.filter(product=product).order_by("-id")
    total_reviews = reviews.count()

    if total_reviews:
        total_rating = 0
        count = 0
        for r in reviews:
            try:
                rating = float(r.rating)
                total_rating += rating
                count += 1
            except (TypeError, ValueError):
                continue
        avg_rating = round(total_rating / count, 2) if count else 2.4
    else:
        avg_rating = 2.4

    sentiment_counts = {}
    recent_reviews = []

    for r in reviews:
        if hasattr(r.review_date, "strftime"):
            date_str = r.review_date.strftime("%b %d, %Y")
        else:
            date_str = str(r.review_date)

        recent_reviews.append({
            "reviewer": r.reviewer,
            "rating": r.rating,
            "text": r.text,
            "sentiment": r.sentiment or "neutral",
            "review_date": date_str
        })

        s = r.sentiment or "unknown"
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

    chart_data = [{"sentiment": k, "count": v} for k, v in sentiment_counts.items()]

    return JsonResponse({
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "sentiment_counts": chart_data,
        "recent_reviews": recent_reviews  
    })


from django.http import JsonResponse
from .models import Product, Review

def critical_issues(request, pid):
    try:
        product = Product.objects.get(pid=pid)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    reviews = Review.objects.filter(product=product)
    total_reviews = reviews.count() or 1  # avoid division by zero

    issues = []

    # 1️⃣ Missing rating (avg fallback)
    missing_rating_count = reviews.filter(rating__isnull=True).count()
    if missing_rating_count > 0:
        issues.append({
            "issue": "Missing rating / avg fallback used",
            "severity": "High",
            "count": missing_rating_count,
            "percent": round(missing_rating_count / total_reviews * 100, 1)
        })

    # 2️⃣ Reviewer empty
    reviewer_empty_count = reviews.filter(reviewer__isnull=True).count() + \
                           reviews.filter(reviewer__exact="").count()
    if reviewer_empty_count > 0:
        issues.append({
            "issue": "Reviewer name missing",
            "severity": "High",
            "count": reviewer_empty_count,
            "percent": round(reviewer_empty_count / total_reviews * 100, 1)
        })

    # 3️⃣ Unknown sentiment
    unknown_sentiment_count = reviews.filter(sentiment__in=[None, "", "unknown"]).count()
    if unknown_sentiment_count > 0:
        issues.append({
            "issue": "Unknown sentiment",
            "severity": "Medium",
            "count": unknown_sentiment_count,
            "percent": round(unknown_sentiment_count / total_reviews * 100, 1)
        })

    # 4️⃣ Very short review texts
    short_text_count = reviews.filter(text__length__lt=20).count()
    if short_text_count > 0:
        issues.append({
            "issue": "Short / truncated review text",
            "severity": "Medium",
            "count": short_text_count,
            "percent": round(short_text_count / total_reviews * 100, 1)
        })

    return JsonResponse({
        "total_reviews": total_reviews,
        "critical_issues": issues
    })
