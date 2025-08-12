from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, OTPVerificationSerializer
from .models import User, OTPVerification,UserRole
from core.utils import success_response, validation_error_response, error_response, prepare_user_data
# from notifications.tasks import send_otp_notification
import random
from django.db import transaction
class RegisterView(APIView):
    """
    API endpoint for user registration.
    """
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        
        user = serializer.save()
        
        UserRole.objects.create(user=user, role="ADMIN")

        # TODO: Currently OTP Related Code Is Commented But in Actual Production It will Be Uncommented.

        # # Generate OTP for email and phone
        # otp_code = str(random.randint(100000, 999999))
        # expires_at = timezone.now() + timezone.timedelta(minutes=10)
        
        # OTPVerification.objects.create(
        #     user=user,
        #     email=user.email,
        #     phone_number=user.phone_number,
        #     otp=otp_code,
        #     otp_type="email",
        #     expires_at=expires_at
        # )
        
        # OTPVerification.objects.create(
        #     user=user,
        #     email=user.email,
        #     phone_number=user.phone_number,
        #     otp=otp_code,
        #     otp_type="phone",
        #     expires_at=expires_at
        # )
        
        # Send OTP synchronously (no Celery)
        # send_otp_notification(user.email, user.phone_number, otp_code)
        
        refresh = RefreshToken.for_user(user)
        
        return success_response("Registration successful. OTP sent to email and phone.", data={
            "user": prepare_user_data(user),
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class LoginView(APIView):
    """
    API endpoint for user login via email/password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        print("request.data", request.data)
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        
        validated_data = serializer.validated_data
        user = validated_data["user"]
        
        if not user.is_verified:
            return error_response("User email/phone not verified.")
        
        refresh = RefreshToken.for_user(user)
        user.record_successful_login(request.META.get("REMOTE_ADDR"))
        
        return success_response("Login successful.", data={
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": prepare_user_data(user),
        })

class ForgotPasswordView(APIView):
    """
    API endpoint for forgot password (send OTP to email).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        
        user = User.objects.get(email=serializer.validated_data["email"])
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        
        OTPVerification.objects.create(
            user=user,
            email=user.email,
            phone_number=user.phone_number,
            otp=otp_code,
            otp_type="email",
            expires_at=expires_at
        )
        
        # Send OTP synchronously (no Celery)
        # send_otp_notification(user.email, user.phone_number, otp_code)
        
        return success_response("OTP sent to email for password reset.")

class OTPVerificationView(APIView):
    """
    API endpoint for OTP verification (email or phone).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        
        validated_data = serializer.validated_data
        otp_type = validated_data["otp_type"]
        
        # Mark user as verified if both email and phone are verified
        if otp_type == "email":

            # user = User.objects.get(email=validated_data["email"])
            user.verify_email()
        else:
            # user = User.objects.get(phone_number=validated_data["phone_number"])
            user.verify_phone()  
        
        return success_response(f"{otp_type.capitalize()} OTP verified successfully.",{"user": prepare_user_data(user)})


class UserProfileView(APIView):
    """
    API endpoint for user profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return success_response("User profile fetched successfully.",{"user": prepare_user_data(user)})
