from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_at')
    search_fields = ('name',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'verified', 'title', 'location', 'review_date', 'text','sentiment','sentiment_score')

admin.site.register(Review, ReviewAdmin)