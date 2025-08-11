"""
Serializers for user registration, login, OTP, and password reset.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, OTPVerification
from django.utils import timezone
from core.utils import error_response

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    prefix = serializers.CharField(max_length=10, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["prefix", "first_name", "last_name", "email", "phone_number", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login via email/password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        return {"user": user}

class MobileOTPLoginSerializer(serializers.Serializer):
    """
    Serializer for mobile login via OTP.
    """
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            otp_obj = OTPVerification.objects.get(phone_number=data["phone_number"], otp=data["otp"], is_verified=False)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")
        if otp_obj.expires_at < timezone.now():
            raise serializers.ValidationError("OTP expired.")
        otp_obj.is_verified = True
        otp_obj.save()
        return {"user": otp_obj.user}

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password (request OTP).
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification (email or phone).
    """
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    otp = serializers.CharField()
    otp_type = serializers.ChoiceField(choices=["email", "phone"])

    def validate(self, data):
        if data["otp_type"] == "email":
            otp_obj = OTPVerification.objects.filter(email=data["email"], otp=data["otp"], otp_type="email", is_verified=False).first()
        else:
            otp_obj = OTPVerification.objects.filter(phone_number=data["phone_number"], otp=data["otp"], otp_type="phone", is_verified=False).first()
        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP.")
        if otp_obj.expires_at < timezone.now():
            raise serializers.ValidationError("OTP expired.")
        otp_obj.is_verified = True
        otp_obj.save()
        return data
