"""
URL patterns for product management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.ProductCategoryViewSet, basename='category')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')
router.register(r'pricing', views.ProductPricingViewSet, basename='pricing')
router.register(r'images', views.ProductImageViewSet, basename='image')
router.register(r'maintenance', views.ProductMaintenanceViewSet, basename='maintenance')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
