from django.urls import path
from . import views
from django.urls import path
from .views import add_product , scrape_product

urlpatterns = [
    path('', views.dashboard, name='dashoard'),
    path('api/add-product/', add_product, name='add-product'),
    path('api/scrape-product/', scrape_product, name='scrape-product'),
    # path('add/', views.add_product, name='add_product'),
    # path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # path('rescrape/<int:product_id>/', views.rescrape_product, name='rescrape_product'),
    # path('sentiment/<int:product_id>/', views.run_sentiment_view, name='run_sentiment'),
    # path('critical/<int:product_id>/', views.run_critical_issues_view, name='run_critical_issues'),
]


