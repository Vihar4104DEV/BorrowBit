"""
Unit tests for user authentication APIs.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, OTPVerification
from django.utils import timezone
import json

class UserAuthenticationTestCase(TestCase):
    """Test case for user authentication APIs."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.forgot_password_url = reverse('user-forgot-password')
        self.verify_otp_url = reverse('user-verify-otp')
        
        # Test user data
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+1234567890',
            'password': 'testpass123'
        }
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Registration successful. OTP sent to email and phone.')
        
        # Verify user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertEqual(user.phone_number, self.user_data['phone_number'])
        
        # Verify OTP was created
        otp_verifications = OTPVerification.objects.filter(user=user)
        self.assertEqual(otp_verifications.count(), 2)  # One for email, one for phone
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create first user
        User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Try to register with same email
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Email already exists', str(response.data['message']))
    
    def test_user_registration_duplicate_phone(self):
        """Test registration with duplicate phone number."""
        # Create first user with different email but same phone
        User.objects.create_user(
            email='jane.doe@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe',
            phone_number='+1234567890'
        )
        
        # Try to register with same phone
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Phone number already exists', str(response.data['message']))
    
    def test_email_login_success(self):
        """Test successful email login."""
        # Create and verify user
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        user.verify_email()
        user.verify_phone()
        
        login_data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'login_type': 'email'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['login_type'], 'email')
    
    def test_mobile_login_success(self):
        """Test successful mobile OTP login."""
        # Create user
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone_number='+1234567890'
        )
        
        # Create OTP verification
        otp_code = '123456'
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        OTPVerification.objects.create(
            user=user,
            email=user.email,
            phone_number=user.phone_number,
            otp=otp_code,
            otp_type='phone',
            expires_at=expires_at
        )
        
        login_data = {
            'phone_number': '+1234567890',
            'otp': '123456',
            'login_type': 'mobile'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['login_type'], 'mobile')
    
    def test_login_unverified_user(self):
        """Test login with unverified user."""
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        login_data = {
            'email': 'john.doe@example.com',
            'password': 'testpass123',
            'login_type': 'email'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('not verified', response.data['message'])
    
    def test_forgot_password_success(self):
        """Test successful forgot password request."""
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        forgot_data = {'email': 'john.doe@example.com'}
        response = self.client.post(self.forgot_password_url, forgot_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'OTP sent to email for password reset.')
        
        # Verify OTP was created
        otp_verifications = OTPVerification.objects.filter(user=user, otp_type='email')
        self.assertEqual(otp_verifications.count(), 1)
    
    def test_forgot_password_user_not_found(self):
        """Test forgot password with non-existent user."""
        forgot_data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.forgot_password_url, forgot_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('does not exist', response.data['message'])
    
    def test_otp_verification_success(self):
        """Test successful OTP verification."""
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone_number='+1234567890'
        )
        
        # Create OTP verification
        otp_code = '123456'
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        OTPVerification.objects.create(
            user=user,
            email=user.email,
            phone_number=user.phone_number,
            otp=otp_code,
            otp_type='email',
            expires_at=expires_at
        )
        
        verify_data = {
            'email': 'john.doe@example.com',
            'otp': '123456',
            'otp_type': 'email'
        }
        
        response = self.client.post(self.verify_otp_url, verify_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Email OTP verified successfully.')
        
        # Verify user email is now verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertIsNotNone(user.email_verified_at)
    
    def test_otp_verification_invalid_otp(self):
        """Test OTP verification with invalid OTP."""
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        verify_data = {
            'email': 'john.doe@example.com',
            'otp': '999999',
            'otp_type': 'email'
        }
        
        response = self.client.post(self.verify_otp_url, verify_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Invalid OTP', response.data['message'])
    
    def test_otp_verification_expired_otp(self):
        """Test OTP verification with expired OTP."""
        user = User.objects.create_user(
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create expired OTP
        otp_code = '123456'
        expires_at = timezone.now() - timezone.timedelta(minutes=10)  # Expired
        OTPVerification.objects.create(
            user=user,
            email=user.email,
            phone_number=user.phone_number,
            otp=otp_code,
            otp_type='email',
            expires_at=expires_at
        )
        
        verify_data = {
            'email': 'john.doe@example.com',
            'otp': '123456',
            'otp_type': 'email'
        }
        
        response = self.client.post(self.verify_otp_url, verify_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('OTP expired', response.data['message'])
