from django.urls import path
from store import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),  # For all products
    path('shop/<slug:category_slug>/', views.shop, name='product_by_category'),  # For products filtered by category
    path('shop/<category_slug>/<product_slug>/', views.product_detail, name='product_detail'),
    path('search/',views.search,name="search"),


]
