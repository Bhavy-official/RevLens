from django.core.management.base import BaseCommand
from core.models import Review
from transformers import pipeline
import re
from collections import defaultdict, Counter

class Command(BaseCommand):
    help = "ML-based Critical Issues Analyzer for product reviews (with detailed summary)"

    def __init__(self):
        super().__init__()
        self.classifier = None
        self.issue_labels = [
            "health safety problem",
            "product defect",
            "performance problem",
            "delivery or packaging issue",
            "taste or consumption issue",
            "value for money complaint",
            "general dissatisfaction"
        ]
        self.max_issues_per_review = 5

    # -----------------------------
    # Load classifier
    # -----------------------------
    def load_classifier(self):
        self.stdout.write("🔄 Loading zero-shot classifier...")
        try:
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            self.stdout.write("✅ Classifier loaded successfully")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to load classifier: {e}"))
            return False

    # -----------------------------
    # Helpers
    # -----------------------------
    def get_language_intensity(self, text):
        strong_words = ["terrible", "worst", "horrible", "disgusting", "hate", "awful", "painful"]
        count = sum(text.lower().count(word) for word in strong_words)
        return 1 + min(count * 0.3, 1)  # scales 1.0 - 2.0

    def extract_evidence_sentences(self, text, issue_label, max_samples=2):
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Deduplicate and normalize
        clean_sentences = []
        for s in sentences:
            s = re.sub(r"(read more|READ MORE)", "", s).strip()
            if s and s not in clean_sentences:
                clean_sentences.append(s)

        # Match issue keywords
        keywords = issue_label.split()
        evidence = [s for s in clean_sentences if any(word in s.lower() for word in keywords)]

        # Fallback: pick most intense sentences
        if not evidence:
            evidence = sorted(clean_sentences, key=lambda s: self.get_language_intensity(s), reverse=True)

        return evidence[:max_samples]

    # -----------------------------
    # Main analysis
    # -----------------------------
    def analyze_review(self, review):
        text = review.text
        if not text:
            return []

        results = self.classifier(text, self.issue_labels, multi_label=True)
        intensity = self.get_language_intensity(text)
        issues = []

        severity_base = {
            "health safety problem": 9,
            "product defect": 8,
            "performance problem": 7,
            "delivery or packaging issue": 5,
            "taste or consumption issue": 4,
            "value for money complaint": 3,
            "general dissatisfaction": 2,
        }

        for label, score in zip(results["labels"], results["scores"]):
            if score > 0.4:
                severity = min(severity_base.get(label, 1) * score * intensity, 10)
                evidence = self.extract_evidence_sentences(text, label)
                issues.append({
                    "issue": label,
                    "confidence": round(score, 3),
                    "severity": round(severity, 2),
                    "evidence": evidence,
                    "reviewer": review.reviewer,
                    "rating": review.rating,
                    "review_id": review.id,
                })
            if len(issues) >= self.max_issues_per_review:
                break

        return issues

    def analyze_reviews(self, reviews):
        all_issues = defaultdict(list)
        for idx, review in enumerate(reviews, 1):
            issues = self.analyze_review(review)
            if issues:
                for issue in issues:
                    all_issues[issue["issue"]].append(issue)
                review.is_critical = True
                review.save(update_fields=["is_critical"])
            if idx % 10 == 0:
                self.stdout.write(f"Processed {idx} reviews...")
        return all_issues

    # -----------------------------
    # Summary + Report Generation
    # -----------------------------
    def summarize(self, all_issues):
        summary = []
        for issue_label, issue_list in all_issues.items():
            count = len(issue_list)
            avg_severity = round(sum(i["severity"] for i in issue_list) / count, 2)
            top_reviewers = Counter(i["reviewer"] for i in issue_list).most_common(3)
            example_evidence = []
            for i in issue_list:
                for e in i["evidence"]:
                    if e not in example_evidence:
                        example_evidence.append(e)
                if len(example_evidence) >= 2:
                    break

            summary.append({
                "issue": issue_label,
                "total_mentions": count,
                "average_severity": avg_severity,
                "top_reviewers": top_reviewers,
                "example_evidence": example_evidence,
            })
        return sorted(summary, key=lambda x: x["total_mentions"], reverse=True)

    def generate_text_summary(self, summary, total_reviews):
        if not summary:
            return "No critical issues detected."
        top_issues = summary[:3]
        parts = [f"We analyzed {total_reviews} reviews in total."]
        parts.append(f"The most common problem was '{top_issues[0]['issue']}' ({top_issues[0]['total_mentions']} mentions).")
        if len(top_issues) > 1:
            parts.append("Other notable issues include " + ", ".join(
                f"'{i['issue']}' (avg severity {i['average_severity']}/10)"
                for i in top_issues[1:]
            ) + ".")
        return " ".join(parts)

    def display_summary(self, summary, total_reviews):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"TOP CRITICAL ISSUES — Analyzed {total_reviews} reviews"))
        self.stdout.write("=" * 60)
        for item in summary:
            self.stdout.write(f"\nIssue: {item['issue'].upper()}")
            self.stdout.write(f"  Mentions: {item['total_mentions']}")
            self.stdout.write(f"  Avg Severity: {item['average_severity']}/10")
            for ev in item['example_evidence']:
                self.stdout.write(f"    - {ev}")
        self.stdout.write("=" * 60)
        self.stdout.write(self.generate_text_summary(summary, total_reviews))
        self.stdout.write("\nAnalysis complete!\n")

    # -----------------------------
    # CLI Arguments
    # -----------------------------
    def add_arguments(self, parser):
        parser.add_argument("--min-rating", type=float, default=3.0,
                            help="Analyze reviews with rating less or equal to this value (default 3.0)")
        parser.add_argument("--product-name", type=str, default=None,
                            help="Filter reviews by product name (optional)")

    def handle(self, *args, **options):
        if not self.load_classifier():
            return

        from core.models import Product

        # Filter reviews by product name if provided
        if options["product_name"]:
            try:
                product = Product.objects.get(name__icontains=options["product_name"])
                reviews = Review.objects.filter(product=product, rating__lte=options["min_rating"])
                self.stdout.write(f"Analyzing product: {product.name}")
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Product '{options['product_name']}' not found."))
                return
        else:
            reviews = Review.objects.filter(rating__lte=options["min_rating"])
            self.stdout.write(f"Analyzing all products with rating ≤ {options['min_rating']}")

        total_reviews = reviews.count()
        if total_reviews == 0:
            self.stdout.write("No reviews found matching criteria.")
            return

        self.stdout.write(f"Processing {total_reviews} reviews...")
        all_issues = self.analyze_reviews(reviews)
        if not all_issues:
            self.stdout.write("No critical issues detected.")
            return

        summary = self.summarize(all_issues)
        self.display_summary(summary, total_reviews)

        summary_text = self.generate_text_summary(summary, total_reviews)

# Save to a .txt file
        filename = f"review_summary_{options['product_name'] or 'all'}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(summary_text)

        self.stdout.write(self.style.SUCCESS(f"✅ Summary saved to {filename}"))