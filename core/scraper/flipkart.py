import requests
from bs4 import BeautifulSoup

def scrape_flipkart_reviews(product_pid, max_pages=4):
    reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    base_url = f"https://www.flipkart.com/flostrain-manual-nose-ear-hair-trimmer-portable-stainless-steel-remover-10-min-runtime-2-length-settings/product-reviews/itm77372ab994526?pid={product_pid}&lid=LST{product_pid}B7LBYA&marketplace=FLIPKART&page=1"

    for page in range(1, max_pages + 1):
        url = f"{base_url}&page={page}"
        print(f"[DEBUG] Fetching page: {url}")
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')

        review_blocks = soup.find_all('div', class_='col-12-12')
        if not review_blocks:
            break

        for block in review_blocks:
            title = block.find('p', class_='z9E0IG')
            text = block.find('div', class_='ZmyHeo')
            reviewer_name = block.find('p', class_='_2NsDsF AwS1CA')
            location = block.find('p', class_='MztJPv')
            rating_div = block.find('div', class_='XQDdHH Ga3i8K')
            review_date = block.find('p', class_='_2NsDsF')

            reviews.append({
                'title': title.get_text() if title else 'No title',
                'review_text': text.get_text(strip=True) if text else 'No text',
                'reviewer_name': reviewer_name.get_text() if reviewer_name else 'No name',
                'location': location.get_text() if location else 'No location',
                'rating': float(rating_div.get_text(strip=True)) if rating_div else 0,
                'date': review_date.get_text() if review_date else 'No date'
            })

    print(f"[DEBUG] Total reviews fetched: {len(reviews)}")
    return reviews

