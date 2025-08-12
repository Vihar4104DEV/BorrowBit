"""
URL patterns for payment management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'rental-orders', views.RentalOrderViewSet, basename='rental-order')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'gateways', views.PaymentGatewayViewSet, basename='payment-gateway')
router.register(r'schedules', views.PaymentScheduleViewSet, basename='payment-schedule')
router.register(r'notifications', views.PaymentNotificationViewSet, basename='payment-notification')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Stripe webhook (CSRF exempt)
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Success and cancel pages (for frontend redirects)
    path('success/', views.PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
]

# Add custom actions to the router
rental_order_router = router.get_urls()
urlpatterns.extend(rental_order_router)
