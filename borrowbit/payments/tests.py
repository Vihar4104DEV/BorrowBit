"""
Tests for payment models, serializers, views, and permissions.

This module contains comprehensive test cases for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade testing.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    PaymentMethod, CheckoutSession, Payment, PaymentWebhook, PaymentRefund
)
from .serializers import (
    PaymentMethodSerializer, CheckoutSessionCreateSerializer, PaymentCreateSerializer
)
from user.models import UserRole

User = get_user_model()


class PaymentMethodModelTest(TestCase):
    """Test cases for PaymentMethod model."""
    
    def setUp(self):
        """Set up test data."""
        self.payment_method = PaymentMethod.objects.create(
            name="Test Credit Card",
            method_type="CREDIT_CARD",
            provider="STRIPE",
            description="Test credit card payment method",
            processing_fee_percentage=Decimal('2.5'),
            processing_fee_fixed=Decimal('1.00'),
            minimum_amount=Decimal('10.00'),
            maximum_amount=Decimal('10000.00')
        )
    
    def test_payment_method_creation(self):
        """Test payment method creation."""
        self.assertEqual(self.payment_method.name, "Test Credit Card")
        self.assertEqual(self.payment_method.method_type, "CREDIT_CARD")
        self.assertEqual(self.payment_method.provider, "STRIPE")
        self.assertTrue(self.payment_method.is_active)
        self.assertFalse(self.payment_method.is_deleted)
    
    def test_calculate_processing_fee(self):
        """Test processing fee calculation."""
        amount = Decimal('100.00')
        expected_fee = Decimal('2.5') + Decimal('1.00')  # 2.5% + 1.00
        calculated_fee = self.payment_method.calculate_processing_fee(amount)
        self.assertEqual(calculated_fee, expected_fee)
    
    def test_is_valid_for_amount(self):
        """Test amount validation."""
        # Valid amount
        self.assertTrue(self.payment_method.is_valid_for_amount(Decimal('100.00')))
        
        # Below minimum
        self.assertFalse(self.payment_method.is_valid_for_amount(Decimal('5.00')))
        
        # Above maximum
        self.assertFalse(self.payment_method.is_valid_for_amount(Decimal('15000.00')))
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        self.payment_method.soft_delete()
        self.assertTrue(self.payment_method.is_deleted)
        self.assertFalse(self.payment_method.is_active)
    
    def test_restore(self):
        """Test restore functionality."""
        self.payment_method.soft_delete()
        self.payment_method.restore()
        self.assertFalse(self.payment_method.is_deleted)
        self.assertTrue(self.payment_method.is_active)


class CheckoutSessionModelTest(TestCase):
    """Test cases for CheckoutSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            method_type="CREDIT_CARD",
            provider="STRIPE"
        )
        
        self.checkout_session = CheckoutSession.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
    
    def test_checkout_session_creation(self):
        """Test checkout session creation."""
        self.assertEqual(self.checkout_session.user, self.user)
        self.assertEqual(self.checkout_session.payment_method, self.payment_method)
        self.assertEqual(self.checkout_session.amount, Decimal('100.00'))
        self.assertEqual(self.checkout_session.currency, 'INR')
        self.assertEqual(self.checkout_session.status, 'PENDING')
        self.assertIsNotNone(self.checkout_session.session_id)
    
    def test_is_expired(self):
        """Test expiration check."""
        # Not expired
        self.assertFalse(self.checkout_session.is_expired())
        
        # Expired
        self.checkout_session.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        self.checkout_session.save()
        self.assertTrue(self.checkout_session.is_expired())
    
    def test_can_be_paid(self):
        """Test payment eligibility."""
        # Can be paid
        self.assertTrue(self.checkout_session.can_be_paid())
        
        # Cannot be paid if expired
        self.checkout_session.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        self.checkout_session.save()
        self.assertFalse(self.checkout_session.can_be_paid())
        
        # Cannot be paid if completed
        self.checkout_session.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        self.checkout_session.status = 'COMPLETED'
        self.checkout_session.save()
        self.assertFalse(self.checkout_session.can_be_paid())
    
    def test_mark_as_paid(self):
        """Test marking as paid."""
        self.checkout_session.mark_as_paid()
        self.assertEqual(self.checkout_session.status, 'COMPLETED')
        self.assertIsNotNone(self.checkout_session.paid_at)
    
    def test_mark_as_failed(self):
        """Test marking as failed."""
        self.checkout_session.mark_as_failed()
        self.assertEqual(self.checkout_session.status, 'FAILED')
    
    def test_mark_as_cancelled(self):
        """Test marking as cancelled."""
        self.checkout_session.mark_as_cancelled()
        self.assertEqual(self.checkout_session.status, 'CANCELLED')
        self.assertIsNotNone(self.checkout_session.cancelled_at)


class PaymentModelTest(TestCase):
    """Test cases for Payment model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            method_type="CREDIT_CARD",
            provider="STRIPE"
        )
        
        self.checkout_session = CheckoutSession.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        self.payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            created_by=self.user
        )
    
    def test_payment_creation(self):
        """Test payment creation."""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.checkout_session, self.checkout_session)
        self.assertEqual(self.payment.amount, Decimal('100.00'))
        self.assertEqual(self.payment.transaction_type, 'RENTAL_PAYMENT')
        self.assertEqual(self.payment.status, 'PENDING')
        self.assertIsNotNone(self.payment.payment_id)
    
    def test_mark_as_completed(self):
        """Test marking as completed."""
        self.payment.mark_as_completed(
            provider_payment_id='prov_123',
            provider_transaction_id='txn_456'
        )
        self.assertEqual(self.payment.status, 'COMPLETED')
        self.assertEqual(self.payment.provider_payment_id, 'prov_123')
        self.assertEqual(self.payment.provider_transaction_id, 'txn_456')
        self.assertIsNotNone(self.payment.completed_at)
    
    def test_mark_as_failed(self):
        """Test marking as failed."""
        self.payment.mark_as_failed(
            error_code='CARD_DECLINED',
            error_message='Card was declined'
        )
        self.assertEqual(self.payment.status, 'FAILED')
        self.assertEqual(self.payment.error_code, 'CARD_DECLINED')
        self.assertEqual(self.payment.error_message, 'Card was declined')
        self.assertIsNotNone(self.payment.failed_at)
    
    def test_mark_as_processing(self):
        """Test marking as processing."""
        self.payment.mark_as_processing()
        self.assertEqual(self.payment.status, 'PROCESSING')
        self.assertIsNotNone(self.payment.processed_at)
    
    def test_can_be_refunded(self):
        """Test refund eligibility."""
        # Cannot be refunded if not completed
        self.assertFalse(self.payment.can_be_refunded())
        
        # Can be refunded if completed
        self.payment.status = 'COMPLETED'
        self.payment.save()
        self.assertTrue(self.payment.can_be_refunded())
    
    def test_get_refund_amount(self):
        """Test refund amount calculation."""
        self.payment.status = 'COMPLETED'
        self.payment.save()
        self.assertEqual(self.payment.get_refund_amount(), Decimal('100.00'))


class PaymentRefundModelTest(TestCase):
    """Test cases for PaymentRefund model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            method_type="CREDIT_CARD",
            provider="STRIPE"
        )
        
        self.checkout_session = CheckoutSession.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        self.payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            status='COMPLETED',
            created_by=self.user
        )
        
        self.refund = PaymentRefund.objects.create(
            payment=self.payment,
            user=self.user,
            amount=Decimal('50.00'),
            currency='INR',
            reason='REQUESTED_BY_CUSTOMER',
            created_by=self.user
        )
    
    def test_refund_creation(self):
        """Test refund creation."""
        self.assertEqual(self.refund.payment, self.payment)
        self.assertEqual(self.refund.user, self.user)
        self.assertEqual(self.refund.amount, Decimal('50.00'))
        self.assertEqual(self.refund.reason, 'REQUESTED_BY_CUSTOMER')
        self.assertEqual(self.refund.status, 'PENDING')
        self.assertIsNotNone(self.refund.refund_id)
    
    def test_mark_as_completed(self):
        """Test marking as completed."""
        self.refund.mark_as_completed(provider_refund_id='ref_123')
        self.assertEqual(self.refund.status, 'COMPLETED')
        self.assertEqual(self.refund.provider_refund_id, 'ref_123')
        self.assertIsNotNone(self.refund.completed_at)
    
    def test_mark_as_failed(self):
        """Test marking as failed."""
        self.refund.mark_as_failed(
            error_code='REFUND_FAILED',
            error_message='Refund processing failed'
        )
        self.assertEqual(self.refund.status, 'FAILED')
        self.assertEqual(self.refund.error_code, 'REFUND_FAILED')
        self.assertEqual(self.refund.error_message, 'Refund processing failed')
        self.assertIsNotNone(self.refund.failed_at)
    
    def test_mark_as_processing(self):
        """Test marking as processing."""
        self.refund.mark_as_processing()
        self.assertEqual(self.refund.status, 'PROCESSING')
        self.assertIsNotNone(self.refund.processed_at)


class PaymentWebhookModelTest(TestCase):
    """Test cases for PaymentWebhook model."""
    
    def setUp(self):
        """Set up test data."""
        self.webhook = PaymentWebhook.objects.create(
            provider='STRIPE',
            event_type='PAYMENT_INTENT_SUCCEEDED',
            event_id='evt_test_123',
            raw_payload='{"test": "data"}',
            headers={'test': 'header'},
            signature='test_signature'
        )
    
    def test_webhook_creation(self):
        """Test webhook creation."""
        self.assertEqual(self.webhook.provider, 'STRIPE')
        self.assertEqual(self.webhook.event_type, 'PAYMENT_INTENT_SUCCEEDED')
        self.assertEqual(self.webhook.event_id, 'evt_test_123')
        self.assertEqual(self.webhook.status, 'PENDING')
        self.assertIsNotNone(self.webhook.webhook_id)
    
    def test_mark_as_processed(self):
        """Test marking as processed."""
        self.webhook.mark_as_processed()
        self.assertEqual(self.webhook.status, 'PROCESSED')
        self.assertIsNotNone(self.webhook.processed_at)
    
    def test_mark_as_failed(self):
        """Test marking as failed."""
        self.webhook.mark_as_failed('Processing error')
        self.assertEqual(self.webhook.status, 'FAILED')
        self.assertEqual(self.webhook.error_message, 'Processing error')
        self.assertEqual(self.webhook.retry_count, 1)
    
    def test_mark_as_ignored(self):
        """Test marking as ignored."""
        self.webhook.mark_as_ignored()
        self.assertEqual(self.webhook.status, 'IGNORED')
    
    def test_can_retry(self):
        """Test retry eligibility."""
        # Can retry if failed and retry count < 3
        self.webhook.status = 'FAILED'
        self.webhook.retry_count = 1
        self.webhook.save()
        self.assertTrue(self.webhook.can_retry())
        
        # Cannot retry if retry count >= 3
        self.webhook.retry_count = 3
        self.webhook.save()
        self.assertFalse(self.webhook.can_retry())


class PaymentMethodSerializerTest(TestCase):
    """Test cases for PaymentMethodSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.payment_method_data = {
            'name': 'Test Payment Method',
            'method_type': 'CREDIT_CARD',
            'provider': 'STRIPE',
            'description': 'Test payment method',
            'processing_fee_percentage': Decimal('2.5'),
            'processing_fee_fixed': Decimal('1.00'),
            'minimum_amount': Decimal('10.00'),
            'maximum_amount': Decimal('10000.00')
        }
    
    def test_valid_payment_method_serializer(self):
        """Test valid payment method serialization."""
        serializer = PaymentMethodSerializer(data=self.payment_method_data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_processing_fee_percentage(self):
        """Test invalid processing fee percentage."""
        self.payment_method_data['processing_fee_percentage'] = Decimal('150.0')
        serializer = PaymentMethodSerializer(data=self.payment_method_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('processing_fee_percentage', serializer.errors)
    
    def test_invalid_amount_limits(self):
        """Test invalid amount limits."""
        self.payment_method_data['minimum_amount'] = Decimal('10000.00')
        self.payment_method_data['maximum_amount'] = Decimal('10.00')
        serializer = PaymentMethodSerializer(data=self.payment_method_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class PaymentAPITest(APITestCase):
    """Test cases for Payment API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create user role
        self.user_role = UserRole.objects.create(
            user=self.user,
            role='CUSTOMER'
        )
        
        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            method_type="CREDIT_CARD",
            provider="STRIPE",
            is_active=True
        )
        
        # Create checkout session
        self.checkout_session = CheckoutSession.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_create_checkout_session(self):
        """Test creating a checkout session."""
        url = reverse('payments:checkout-session-list')
        data = {
            'payment_method_id': str(self.payment_method.id),
            'amount': '100.00',
            'currency': 'INR',
            'description': 'Test checkout session'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CheckoutSession.objects.count(), 2)
    
    def test_list_checkout_sessions(self):
        """Test listing checkout sessions."""
        url = reverse('payments:checkout-session-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_checkout_session(self):
        """Test retrieving a checkout session."""
        url = reverse('payments:checkout-session-detail', args=[self.checkout_session.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], self.checkout_session.session_id)
    
    def test_cancel_checkout_session(self):
        """Test cancelling a checkout session."""
        url = reverse('payments:checkout-session-cancel', args=[self.checkout_session.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.checkout_session.refresh_from_db()
        self.assertEqual(self.checkout_session.status, 'CANCELLED')
    
    def test_create_payment(self):
        """Test creating a payment."""
        url = reverse('payments:payment-list')
        data = {
            'checkout_session_id': str(self.checkout_session.id),
            'transaction_type': 'RENTAL_PAYMENT',
            'description': 'Test payment'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
    
    def test_list_payments(self):
        """Test listing payments."""
        # Create a payment first
        payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            created_by=self.user
        )
        
        url = reverse('payments:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_payment_summary(self):
        """Test payment summary endpoint."""
        # Create a payment first
        payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            status='COMPLETED',
            created_by=self.user
        )
        
        url = reverse('payments:payment-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_payments'], 1)
        self.assertEqual(response.data['total_amount'], '100.00')
    
    def test_unauthorized_access(self):
        """Test unauthorized access."""
        self.client.force_authenticate(user=None)
        
        url = reverse('payments:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaymentRefundAPITest(APITestCase):
    """Test cases for PaymentRefund API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create user role
        self.user_role = UserRole.objects.create(
            user=self.user,
            role='CUSTOMER'
        )
        
        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            method_type="CREDIT_CARD",
            provider="STRIPE",
            is_active=True
        )
        
        # Create checkout session
        self.checkout_session = CheckoutSession.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        # Create payment
        self.payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            status='COMPLETED',
            created_by=self.user
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_create_refund(self):
        """Test creating a refund."""
        url = reverse('payments:payment-refund-list')
        data = {
            'payment_id': str(self.payment.id),
            'amount': '50.00',
            'reason': 'REQUESTED_BY_CUSTOMER',
            'description': 'Test refund'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentRefund.objects.count(), 1)
    
    def test_list_refunds(self):
        """Test listing refunds."""
        # Create a refund first
        refund = PaymentRefund.objects.create(
            payment=self.payment,
            user=self.user,
            amount=Decimal('50.00'),
            currency='INR',
            reason='REQUESTED_BY_CUSTOMER',
            created_by=self.user
        )
        
        url = reverse('payments:payment-refund-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_refund_amount_validation(self):
        """Test refund amount validation."""
        url = reverse('payments:payment-refund-list')
        data = {
            'payment_id': str(self.payment.id),
            'amount': '150.00',  # More than payment amount
            'reason': 'REQUESTED_BY_CUSTOMER'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_refund_incomplete_payment(self):
        """Test refunding incomplete payment."""
        # Create pending payment
        pending_payment = Payment.objects.create(
            checkout_session=self.checkout_session,
            user=self.user,
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='INR',
            total_amount=Decimal('100.00'),
            transaction_type='RENTAL_PAYMENT',
            status='PENDING',
            created_by=self.user
        )
        
        url = reverse('payments:payment-refund-list')
        data = {
            'payment_id': str(pending_payment.id),
            'amount': '50.00',
            'reason': 'REQUESTED_BY_CUSTOMER'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentWebhookAPITest(APITestCase):
    """Test cases for PaymentWebhook API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create admin role
        self.admin_role = UserRole.objects.create(
            user=self.admin_user,
            role='ADMIN'
        )
        
        # Authenticate admin user
        self.client.force_authenticate(user=self.admin_user)
    
    def test_list_webhooks(self):
        """Test listing webhooks."""
        # Create a webhook
        webhook = PaymentWebhook.objects.create(
            provider='STRIPE',
            event_type='PAYMENT_INTENT_SUCCEEDED',
            event_id='evt_test_123',
            raw_payload='{"test": "data"}'
        )
        
        url = reverse('payments:payment-webhook-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_stripe_webhook_endpoint(self):
        """Test Stripe webhook endpoint."""
        url = reverse('payments:stripe-webhook')
        data = {'test': 'webhook_data'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PaymentWebhook.objects.count(), 1)
    
    def test_razorpay_webhook_endpoint(self):
        """Test Razorpay webhook endpoint."""
        url = reverse('payments:razorpay-webhook')
        data = {'test': 'webhook_data'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PaymentWebhook.objects.count(), 1)
    
    def test_unauthorized_webhook_access(self):
        """Test unauthorized webhook access."""
        # Create regular user
        regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        UserRole.objects.create(user=regular_user, role='CUSTOMER')
        self.client.force_authenticate(user=regular_user)
        
        url = reverse('payments:payment-webhook-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
