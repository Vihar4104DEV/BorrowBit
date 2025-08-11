"""
URL patterns for payment management.

This module contains URL patterns for payment processing, checkout sessions, 
payment methods, and webhook handling.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='payment-method')
router.register(r'checkout-sessions', views.CheckoutSessionViewSet, basename='checkout-session')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'refunds', views.PaymentRefundViewSet, basename='payment-refund')
router.register(r'webhooks', views.PaymentWebhookViewSet, basename='payment-webhook')
router.register(r'analytics', views.PaymentAnalyticsViewSet, basename='payment-analytics')

app_name = 'payments'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('webhooks/stripe/', views.PaymentWebhookViewSet.as_view({'post': 'stripe_webhook'}), name='stripe-webhook'),
    path('webhooks/razorpay/', views.PaymentWebhookViewSet.as_view({'post': 'razorpay_webhook'}), name='razorpay-webhook'),
]

