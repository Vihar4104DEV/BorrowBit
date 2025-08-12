"""
Serializers for user registration, login, OTP, and password reset.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,OTPVerification

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
        # Bypass OTP verification for mobile: accept OTP '4567'
        if data.get("otp") == "4567":
            user = User.objects.filter(phone_number=data.get("phone_number")).first()
            if not user:
                raise serializers.ValidationError("User not found for this phone number.")
            return {"user": user}
        raise serializers.ValidationError("Invalid OTP.")

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
        # Bypass OTP verification:
        # - For email OTP, accept '1234'
        # - For phone OTP, accept '4567'
        otp_type = data.get("otp_type")
        otp_value = data.get("otp")
        if otp_type == "email":
            if not data.get("email"):
                raise serializers.ValidationError("Email is required for email OTP.")
            if otp_value != OTPVerification.objects.filter(email=data.get("email")).first().otp:
                raise serializers.ValidationError("Invalid OTP for email.")
            return data
        if otp_type == "phone" and otp_value == "4567":
            if not data.get("phone_number"):
                raise serializers.ValidationError("Phone number is required for phone OTP.")
            return data
        raise serializers.ValidationError("Invalid OTP.")
