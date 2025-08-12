from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, EmailTemplateViewSet, EmailServiceViewSet, 
    NotificationActionsViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'email-service', EmailServiceViewSet, basename='email-service')
router.register(r'actions', NotificationActionsViewSet, basename='notification-action')

urlpatterns = [
    path('', include(router.urls)),
]
