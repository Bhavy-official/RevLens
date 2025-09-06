# cleaner.py
import re
from typing import List, Dict

# Function to clean and process the review data
def clean_review_data(reviews: List[Dict]) -> List[Dict]:
    """
    Cleans and processes the review data.
    Removes reviews with missing essential data and cleans the review text.
    """
    cleaned_reviews = []

    for review in reviews:
        # Check if the review has all necessary information (rating, reviewer, review text)
        if not review.get('reviewer') or not review.get('review_text') or review.get('rating') is None:
            continue  # Skip reviews with missing data

        # Clean the review text by removing unwanted characters and HTML tags
        cleaned_text = clean_text(review['review_text'])

        # Add cleaned review to the list
        cleaned_review = {
            'reviewer': review['reviewer'],
            'rating': review['rating'],
            'title': review['title'] or "No Title",  # If title is missing, use a placeholder
            'review_text': cleaned_text,
            'date': review['date'] or "No Date",  # Use "No Date" if the date is missing
        }

        cleaned_reviews.append(cleaned_review)

    return cleaned_reviews


# Function to clean the review text
def clean_text(text: str) -> str:
    """
    Removes HTML tags and unwanted characters from the review text.
    """
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove special characters (keep only letters, numbers, and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Strip leading/trailing whitespaces
    text = text.strip()
    
    # Normalize spaces (replace multiple spaces with a single one)
    text = re.sub(r'\s+', ' ', text)

    return text
