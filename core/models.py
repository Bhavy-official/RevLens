from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=255)
    rating = models.FloatField()
    verified = models.BooleanField(default=True)
    text = models.TextField()
    title = models.CharField(max_length=255, blank=True)
    
    # Add these new fields
    location = models.CharField(max_length=255, blank=True)
    review_date = models.CharField(max_length=50, blank=True)  # or DateField if you parse it
    sentiment = models.CharField(max_length=20, blank=True)  
    sentiment_score = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"{self.reviewer} - {self.rating}"
