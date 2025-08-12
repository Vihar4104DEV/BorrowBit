from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'delivery-partners', views.DeliveryPartnerViewSet, basename='delivery-partner')
router.register(r'delivery-jobs', views.DeliveryJobViewSet, basename='delivery-job')
router.register(r'job-assignments', views.JobAssignmentViewSet, basename='job-assignment')
router.register(r'delivery-tracking', views.DeliveryTrackingViewSet, basename='delivery-tracking')
router.register(r'partner-earnings', views.PartnerEarningsViewSet, basename='partner-earning')

app_name = 'delivery_partners'

urlpatterns = [
    path('', include(router.urls)),
]
