from django.db import models

# core/models.py
from django.db import models

class Product(models.Model):
    # Temporarily allow null and blank
    pid = models.CharField(max_length=50, null=True, blank=True)

    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.pid})"

from django.db import models

class Review(models.Model):
    
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=255)
    rating = models.FloatField()
    verified = models.BooleanField(default=True)
    text = models.TextField()
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    review_date = models.CharField(max_length=50)
    is_critical = models.BooleanField(default=False)
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)

    # ✅ NEW FIELD for aspect-based categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ("product", "Product Quality/Features"),
            ("delivery", "Packaging/Delivery"),
            ("seller", "Seller/Service"),
            ("other", "Other"),
        ],
        default="other",
    )

    def __str__(self):
        return f"{self.reviewer} - {self.title[:30]}..."
from django.db import models

from django.db import models

# core/models.py

from django.db import models

class CriticalIssue(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    phrase = models.CharField(max_length=255, null=True, blank=True)  # allow blank for now
    frequency = models.PositiveIntegerField(default=0)
    avg_sentiment_score = models.FloatField(default=0.0)
    aspect = models.CharField(max_length=50, default="general")

    def __str__(self):
        return f"{self.phrase or 'Unknown phrase'} ({self.frequency})"


# class Review(models.Model):
#     product = models.ForeignKey("Product", on_delete=models.CASCADE)
#     reviewer = models.CharField(max_length=255)
#     rating = models.FloatField()
#     verified = models.BooleanField(default=True)
#     text = models.TextField()
#     title = models.CharField(max_length=255)
#     location = models.CharField(max_length=255, blank=True, null=True)
#     review_date = models.CharField(max_length=50)
    
#     sentiment = models.CharField(max_length=20, blank=True, null=True)
#     sentiment_score = models.FloatField(blank=True, null=True)
    
#     # Add this field
#     is_critical = models.BooleanField(default=False)  # ✅ ADD THIS
    
#     category = models.CharField(
#         max_length=50,
#         choices=[
#             ("product", "Product Quality/Features"),
#             ("delivery", "Packaging/Delivery"),
#             ("seller", "Seller/Service"),
#             ("other", "Other"),
#         ],
#         default="other",
#     )

#     def __str__(self):
#         return f"{self.reviewer} - {self.title[:30]}..."