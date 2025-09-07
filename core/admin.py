# from django.contrib import admin
# from .models import Product, Review

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'url', 'created_at')
#     search_fields = ('name',)

# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('product', 'reviewer', 'rating', 'verified', 'title', 'location', 'review_date', 'text','sentiment','sentiment_score')

# admin.site.register(Review, ReviewAdmin)

# from django.contrib import admin
# from .models import CriticalIssue

# @admin.register(CriticalIssue)
# class CriticalIssueAdmin(admin.ModelAdmin):
#     list_display = ("product", "phrase", "frequency", "avg_sentiment_score")
#     search_fields = ("phrase", "product__name")
#     list_filter = ("product",)
#     ordering = ("-frequency",)



from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'pid')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'verified', 'title', 'location', 'review_date', 'sentiment', 'sentiment_score')
    search_fields = ('reviewer', 'title', 'text')
    list_filter = ('rating', 'sentiment', 'verified')
    ordering = ('-id',)

# Comment out CriticalIssue admin until we add that model
# @admin.register(CriticalIssue)
# class CriticalIssueAdmin(admin.ModelAdmin):
#     list_display = ("product", "phrase", "frequency", "avg_sentiment_score")
#     search_fields = ("phrase", "product__name")
#     list_filter = ("product",)
#     ordering = ("-frequency",)