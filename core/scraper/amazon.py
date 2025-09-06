import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

def scrape_amazon_reviews(product_url, max_pages=2):
    """
    Scrapes Amazon reviews for a given product URL.
    Returns a list of dictionaries with reviewer, text, rating, date, verified.
    """
    reviews = []

    for page in range(1, max_pages + 1):
        url = f"{product_url}&pageNumber={page}"
        print(f"[DEBUG] Fetching page: {url}")
        res = requests.get(url, headers=HEADERS)
        print(f"[DEBUG] Status code: {res.status_code}")

        if res.status_code != 200:
            print(f"[DEBUG] Failed to fetch page {page}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        review_blocks = soup.select("li[data-hook='review']")
        if not review_blocks:
            print(f"[DEBUG] No reviews found with main selector, trying fallback")
            review_blocks = soup.select("div.a-section.celwidget")

        print(f"[DEBUG] Found {len(review_blocks)} review blocks on page {page}")

        for r in review_blocks:
            reviewer_tag = r.select_one(".a-profile-name")
            review_text_tag = r.select_one("span[data-hook='review-collapsed']") or r.select_one("span[data-hook='review-body']")
            rating_tag = r.select_one("i[data-hook='review-star-rating'] span.a-icon-alt")
            date_tag = r.select_one("span[data-hook='review-date']")
            verified_tag = r.select_one("span[data-hook='avp-badge-linkless']")

            reviewer = reviewer_tag.get_text(strip=True) if reviewer_tag else ""
            text = review_text_tag.get_text(strip=True) if review_text_tag else ""
            rating = float(rating_tag.get_text(strip=True).split()[0]) if rating_tag else None

            # parse date like "Reviewed in India on 21 August 2025"
            date_str = date_tag.get_text(strip=True).split(" on ")[-1] if date_tag else None
            try:
                date = datetime.strptime(date_str, "%d %B %Y").date() if date_str else None
            except Exception as e:
                print(f"[DEBUG] Date parse error: {e}")
                date = None

            verified = bool(verified_tag)

            print(f"[DEBUG] Review parsed: reviewer={reviewer}, rating={rating}, verified={verified}")
            print(f"[DEBUG] Review text: {text[:60]}...")  # first 60 chars

            reviews.append({
                "reviewer": reviewer,
                "text": text,
                "rating": rating,
                "date": date,
                "verified": verified
            })

    return reviews
