from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField()
    text = models.TextField()
    date = models.DateField()
    sentiment = models.CharField(max_length=20, null=True, blank=True)  # placeholder
    keywords = models.TextField(null=True, blank=True)  # comma-separated for now
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} | {self.rating}"
