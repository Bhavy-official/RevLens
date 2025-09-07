from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
     path("products/", views.product_list, name="product-list"),
    path('add-product/', views.add_and_scrape_product, name='add-product'),
    path("dashboard-data/<str:pid>/", views.dashboard_data, name="dashboard-data"),

]
    # path('add/', views.add_product, name='add_product'),
    # path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # path('rescrape/<int:product_id>/', views.rescrape_product, name='rescrape_product'),
    # path('sentiment/<int:product_id>/', views.run_sentiment_view, name='run_sentiment'),
    # path('critical/<int:product_id>/', views.run_critical_issues_view, name='run_critical_issues'),



