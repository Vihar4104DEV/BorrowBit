from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='user-register'),
    path('login/', views.LoginView.as_view(), name='user-login'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='user-forgot-password'),
    path('verify-otp/', views.OTPVerificationView.as_view(), name='user-verify-otp'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
]
