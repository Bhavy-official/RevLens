# import re
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk import download

# # Download the stopwords if not already available
# download('punkt')
# download('stopwords')

# def clean_review_data(review):
#     # Step 1: Remove leading/trailing whitespaces
#     review['review_text'] = review['review_text'].strip() if review.get('review_text') else "No review text"

#     # Step 2: Remove non-alphanumeric characters (except spaces)
#     review['review_text'] = re.sub(r'[^A-Za-z0-9\s]', '', review['review_text'])

#     # Step 3: Remove HTML tags if present
#     review['review_text'] = re.sub(r'<.*?>', '', review['review_text'])

#     # Step 4: Convert text to lowercase
#     review['review_text'] = review['review_text'].lower()

#     # Step 5: Remove stop words (common but unimportant words)
#     stop_words = set(stopwords.words('english'))
#     word_tokens = word_tokenize(review['review_text'])

#     # Remove stop words and rejoin the text
#     filtered_text = [word for word in word_tokens if word not in stop_words]
#     review['review_text'] = ' '.join(filtered_text)

#     # Step 6: Handling missing reviewer and title data
#     review['reviewer_name'] = review.get('reviewer_name', 'Unknown Reviewer')
#     review['title'] = review.get('title', 'No Title')
    
#     return review
