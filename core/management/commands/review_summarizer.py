from django.core.management.base import BaseCommand
from core.models import Review, Product
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
from collections import defaultdict, Counter
import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class Command(BaseCommand):
    help = "Summarize reviews and enhance short reviews with additional content"

    def __init__(self):
        super().__init__()
        self.summarizer = None
        self.text_generator = None
        self.tokenizer = None
        self.min_words_threshold = 10  # Reviews with fewer words will be enhanced
        self.max_summary_length = 150
        self.min_summary_length = 50
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))

    def load_models(self):
        """Load summarization and text generation models"""
        self.stdout.write("🔄 Loading AI models...")
        try:
            # Load summarization model
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                max_length=self.max_summary_length,
                min_length=self.min_summary_length,
                do_sample=True
            )
            
            # Load text generation model for enhancement
            self.text_generator = pipeline(
                "text2text-generation",
                model="t5-small",
                max_length=100,
                num_return_sequences=1
            )
            
            self.stdout.write("✅ Models loaded successfully")
            return True
        except Exception as e:
            self.stdout.write(f"❌ Failed to load models: {e}")
            return False

    def count_words(self, text):
        """Count meaningful words in text (excluding stopwords)"""
        if not text:
            return 0
        words = word_tokenize(text.lower())
        meaningful_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        return len(meaningful_words)

    def extract_keywords(self, text):
        """Extract important keywords from text"""
        if not text:
            return []
        
        words = word_tokenize(text.lower())
        # Filter out stopwords and non-alphabetic words
        keywords = [word for word in words if word.isalpha() and word not in self.stop_words and len(word) > 2]
        
        # Get most common words
        word_freq = Counter(keywords)
        return [word for word, count in word_freq.most_common(10)]

    def generate_enhancement_templates(self, product_name, rating, keywords):
        """Generate enhancement templates based on product and rating"""
        positive_templates = [
            f"This {product_name} exceeded my expectations in terms of {', '.join(keywords[:3])}.",
            f"I'm really satisfied with the {product_name} because of its excellent {keywords[0] if keywords else 'quality'}.",
            f"The {product_name} stands out for its {keywords[0] if keywords else 'performance'} and overall value.",
            f"What I love most about this {product_name} is the {keywords[0] if keywords else 'design'} and functionality.",
        ]
        
        negative_templates = [
            f"Unfortunately, the {product_name} disappointed me mainly due to issues with {keywords[0] if keywords else 'quality'}.",
            f"I had high hopes for this {product_name}, but the {keywords[0] if keywords else 'performance'} was below expectations.",
            f"The {product_name} has several problems, particularly with {', '.join(keywords[:2]) if len(keywords) >= 2 else 'overall quality'}.",
            f"I wouldn't recommend this {product_name} because of concerns about {keywords[0] if keywords else 'reliability'}.",
        ]
        
        neutral_templates = [
            f"The {product_name} is decent with some good points regarding {keywords[0] if keywords else 'functionality'}.",
            f"This {product_name} has mixed results - good {keywords[0] if keywords else 'features'} but room for improvement.",
            f"Overall, the {product_name} meets basic expectations for {keywords[0] if keywords else 'the price point'}.",
        ]
        
        if rating >= 4:
            return positive_templates
        elif rating <= 2:
            return negative_templates
        else:
            return neutral_templates

    def enhance_short_review(self, review):
        """Enhance a short review by adding more descriptive content"""
        original_text = review.text
        word_count = self.count_words(original_text)
        
        if word_count >= self.min_words_threshold:
            return original_text  # No enhancement needed
        
        product_name = review.product.name if review.product else "product"
        rating = review.rating
        keywords = self.extract_keywords(original_text)
        
        # Get enhancement templates
        templates = self.generate_enhancement_templates(product_name, rating, keywords)
        selected_template = random.choice(templates)
        
        # Combine original text with enhancement
        if original_text.strip().endswith('.'):
            enhanced_text = f"{original_text} {selected_template}"
        else:
            enhanced_text = f"{original_text}. {selected_template}"
        
        # Add more specific details based on common review patterns
        detail_additions = self.add_contextual_details(review, keywords)
        if detail_additions:
            enhanced_text += f" {detail_additions}"
        
        return enhanced_text

    def add_contextual_details(self, review, keywords):
        """Add contextual details based on product category and rating patterns"""
        details = []
        
        # Add timing context
        timing_phrases = [
            "After using it for a few days",
            "From my experience over the past week",
            "Having tried this for some time",
            "Based on my recent usage"
        ]
        
        # Add comparison context
        comparison_phrases = [
            "compared to similar products",
            "relative to other options in this price range",
            "when measured against alternatives",
            "in comparison to my previous purchases"
        ]
        
        # Add recommendation context
        if review.rating >= 4:
            recommendation_phrases = [
                "I would definitely recommend it to others",
                "It's worth considering for anyone looking for this type of product",
                "This would be a good choice for most people"
            ]
        elif review.rating <= 2:
            recommendation_phrases = [
                "I would suggest looking at other options",
                "There might be better alternatives available",
                "Consider other products before choosing this one"
            ]
        else:
            recommendation_phrases = [
                "It might work for some people",
                "Results may vary depending on your needs",
                "It's an average option in its category"
            ]
        
        # Randomly select and combine details
        selected_details = []
        if random.choice([True, False]):
            selected_details.append(random.choice(timing_phrases))
        if random.choice([True, False]):
            selected_details.append(random.choice(recommendation_phrases))
        
        return " ".join(selected_details)

    def summarize_reviews_by_product(self, reviews):
        """Generate summaries of reviews grouped by product"""
        product_summaries = defaultdict(list)
        
        for review in reviews:
            product_name = review.product.name if review.product else "Unknown Product"
            product_summaries[product_name].append({
                'text': review.text,
                'rating': review.rating,
                'reviewer': review.reviewer,
                'id': review.id
            })
        
        summaries = {}
        for product_name, product_reviews in product_summaries.items():
            # Combine all review texts for summarization
            combined_text = " ".join([r['text'] for r in product_reviews if r['text']])
            
            if len(combined_text.split()) > 50:  # Only summarize if enough content
                try:
                    summary_result = self.summarizer(
                        combined_text, 
                        max_length=self.max_summary_length,
                        min_length=self.min_summary_length,
                        do_sample=True
                    )
                    summary_text = summary_result[0]['summary_text']
                except Exception as e:
                    summary_text = "Unable to generate summary due to processing constraints."
            else:
                summary_text = "Insufficient review content for meaningful summarization."
            
            # Calculate statistics
            ratings = [r['rating'] for r in product_reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            total_reviews = len(product_reviews)
            
            summaries[product_name] = {
                'summary': summary_text,
                'total_reviews': total_reviews,
                'average_rating': round(avg_rating, 2),
                'rating_distribution': Counter(ratings),
                'sample_reviews': product_reviews[:3]  # First 3 reviews as samples
            }
        
        return summaries

    def process_and_enhance_reviews(self, reviews):
        """Process reviews: enhance short ones and collect enhanced data"""
        enhanced_count = 0
        processed_reviews = []
        
        for review in reviews:
            original_word_count = self.count_words(review.text)
            
            if original_word_count < self.min_words_threshold:
                enhanced_text = self.enhance_short_review(review)
                enhanced_count += 1
                
                # Update the review in database (optional)
                # review.text = enhanced_text
                # review.save(update_fields=['text'])
                
                processed_reviews.append({
                    'id': review.id,
                    'original_text': review.text,
                    'enhanced_text': enhanced_text,
                    'original_word_count': original_word_count,
                    'enhanced_word_count': self.count_words(enhanced_text),
                    'rating': review.rating,
                    'reviewer': review.reviewer
                })
            else:
                processed_reviews.append({
                    'id': review.id,
                    'original_text': review.text,
                    'enhanced_text': review.text,
                    'original_word_count': original_word_count,
                    'enhanced_word_count': original_word_count,
                    'rating': review.rating,
                    'reviewer': review.reviewer
                })
        
        return processed_reviews, enhanced_count

    def display_results(self, summaries, enhanced_reviews, enhanced_count, total_reviews):
        """Display comprehensive results"""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS(f"REVIEW ANALYSIS & ENHANCEMENT RESULTS"))
        self.stdout.write("=" * 80)
        
        # Enhancement Statistics
        self.stdout.write(f"\n📊 ENHANCEMENT STATISTICS:")
        self.stdout.write(f"  Total Reviews Processed: {total_reviews}")
        self.stdout.write(f"  Reviews Enhanced: {enhanced_count}")
        self.stdout.write(f"  Enhancement Rate: {(enhanced_count/total_reviews*100):.1f}%")
        
        # Product Summaries
        self.stdout.write(f"\n📝 PRODUCT SUMMARIES:")
        for product_name, data in summaries.items():
            self.stdout.write(f"\n  Product: {product_name}")
            self.stdout.write(f"  Total Reviews: {data['total_reviews']}")
            self.stdout.write(f"  Average Rating: {data['average_rating']}/5.0")
            self.stdout.write(f"  Rating Distribution: {dict(data['rating_distribution'])}")
            self.stdout.write(f"  Summary: {data['summary']}")
            self.stdout.write("-" * 60)
        
        # Sample Enhanced Reviews
        enhanced_samples = [r for r in enhanced_reviews if r['enhanced_text'] != r['original_text']][:5]
        if enhanced_samples:
            self.stdout.write(f"\n✨ SAMPLE ENHANCED REVIEWS:")
            for i, review in enumerate(enhanced_samples, 1):
                self.stdout.write(f"\n  Sample {i}:")
                self.stdout.write(f"  Original ({review['original_word_count']} words): {review['original_text']}")
                self.stdout.write(f"  Enhanced ({review['enhanced_word_count']} words): {review['enhanced_text']}")
                self.stdout.write(f"  Rating: {review['rating']}/5.0")
                self.stdout.write("-" * 40)
        
        self.stdout.write("=" * 80 + "\n")

    def add_arguments(self, parser):
        parser.add_argument(
            "--min-words", type=int, default=10,
            help="Minimum word count threshold for enhancement (default: 10)"
        )
        parser.add_argument(
            "--product-name", type=str, default=None,
            help="Filter reviews by specific product name (optional)"
        )
        parser.add_argument(
            "--max-reviews", type=int, default=1000,
            help="Maximum number of reviews to process (default: 1000)"
        )
        parser.add_argument(
            "--save-enhanced", action="store_true",
            help="Save enhanced reviews back to database"
        )

    def handle(self, *args, **options):
        if not self.load_models():
            return
        
        self.min_words_threshold = options["min_words"]
        
        # Filter reviews
        if options["product_name"]:
            try:
                product = Product.objects.get(name__icontains=options["product_name"])
                reviews = Review.objects.filter(product=product)[:options["max_reviews"]]
                self.stdout.write(f"Analyzing product: {product.name}")
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Product '{options['product_name']}' not found."))
                return
        else:
            reviews = Review.objects.all()[:options["max_reviews"]]
            self.stdout.write(f"Analyzing all products")
        
        total_reviews = reviews.count()
        if total_reviews == 0:
            self.stdout.write("No reviews found matching criteria.")
            return
        
        self.stdout.write(f"Processing {total_reviews} reviews...")
        
        # Process and enhance reviews
        enhanced_reviews, enhanced_count = self.process_and_enhance_reviews(reviews)
        
        # Generate product summaries
        summaries = self.summarize_reviews_by_product(reviews)
        
        # Display results
        self.display_results(summaries, enhanced_reviews, enhanced_count, total_reviews)
        
        # Save enhanced reviews if requested
        if options["save_enhanced"]:
            self.stdout.write("💾 Saving enhanced reviews to database...")
            saved_count = 0
            for enhanced_review in enhanced_reviews:
                if enhanced_review['enhanced_text'] != enhanced_review['original_text']:
                    try:
                        review = Review.objects.get(id=enhanced_review['id'])
                        review.text = enhanced_review['enhanced_text']
                        review.save(update_fields=['text'])
                        saved_count += 1
                    except Review.DoesNotExist:
                        continue
            
            self.stdout.write(f"✅ Saved {saved_count} enhanced reviews to database")
        
        self.stdout.write(self.style.SUCCESS("Analysis and enhancement complete!"))