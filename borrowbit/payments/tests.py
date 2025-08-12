"""
Tests for payment management system.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json
import stripe

from .models import (
    RentalOrder, RentalOrderItem, Payment, PaymentGateway, 
    PaymentSchedule, PaymentNotification
)
from products.models import Product, ProductCategory
from user.models import UserRole

User = get_user_model()


class PaymentModelsTestCase(TestCase):
    """Test cases for payment models."""
    
    def setUp(self):
        """Set up test data."""
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
            role='CUSTOMER',
            is_active=True
        )
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.user,
            category=self.category,
            short_description='Test product description',
            description='Detailed test product description',
            condition='GOOD',
            status='AVAILABLE',
            total_quantity=10,
            available_quantity=10,
            deposit_amount=Decimal('100.00'),
            is_rentable=True,
            admin_approved=True
        )
        
        # Create payment gateway
        self.gateway = PaymentGateway.objects.create(
            name='Test Stripe Gateway',
            gateway_type='STRIPE',
            is_active=True,
            is_test_mode=True
        )
    
    def test_rental_order_creation(self):
        """Test rental order creation."""
        order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, 'DRAFT')
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.total_amount, Decimal('154.25'))
    
    def test_rental_order_item_creation(self):
        """Test rental order item creation."""
        order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        item = RentalOrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('25.00'),
            deposit_per_unit=Decimal('50.00')
        )
        
        self.assertEqual(item.total_price, Decimal('50.00'))
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product, self.product)
    
    def test_payment_creation(self):
        """Test payment creation."""
        order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        payment = Payment.objects.create(
            order=order,
            payment_type='FULL_UPFRONT',
            amount=Decimal('154.25'),
            gateway=self.gateway,
            status='PENDING'
        )
        
        self.assertIsNotNone(payment.payment_id)
        self.assertEqual(payment.amount, Decimal('154.25'))
        self.assertEqual(payment.status, 'PENDING')
        self.assertEqual(payment.order, order)


class PaymentAPITestCase(APITestCase):
    """Test cases for payment API endpoints."""
    
    def setUp(self):
        """Set up test data."""
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
            role='CUSTOMER',
            is_active=True
        )
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.user,
            category=self.category,
            short_description='Test product description',
            description='Detailed test product description',
            condition='GOOD',
            status='AVAILABLE',
            total_quantity=10,
            available_quantity=10,
            deposit_amount=Decimal('100.00'),
            is_rentable=True,
            admin_approved=True
        )
        
        # Create payment gateway
        self.gateway = PaymentGateway.objects.create(
            name='Test Stripe Gateway',
            gateway_type='STRIPE',
            is_active=True,
            is_test_mode=True
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    @patch('stripe.checkout.Session.create')
    def test_create_rental_order_from_cart(self, mock_stripe_create):
        """Test creating rental order from cart."""
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.id = 'cs_test_123'
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_session.payment_intent = 'pi_test_123'
        mock_stripe_create.return_value = mock_session
        
        # Test data
        cart_data = {
            'cart_items': [
                {
                    'product_id': str(self.product.id),
                    'quantity': 2
                }
            ],
            'rental_start_date': (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
            'rental_end_date': (timezone.now() + timezone.timedelta(hours=25)).isoformat(),
            'notes': 'Test rental order'
        }
        
        url = reverse('rental-order-create-from-cart')
        response = self.client.post(url, cart_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify order was created
        self.assertEqual(RentalOrder.objects.count(), 1)
        order = RentalOrder.objects.first()
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.status, 'DRAFT')
        
        # Verify order items were created
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        
        # Verify payment was created
        self.assertEqual(order.payments.count(), 1)
        payment = order.payments.first()
        self.assertEqual(payment.status, 'PENDING')
        self.assertEqual(payment.gateway, self.gateway)
    
    def test_create_rental_order_invalid_data(self):
        """Test creating rental order with invalid data."""
        # Test data with invalid dates
        cart_data = {
            'cart_items': [
                {
                    'product_id': str(self.product.id),
                    'quantity': 2
                }
            ],
            'rental_start_date': (timezone.now() + timezone.timedelta(hours=25)).isoformat(),
            'rental_end_date': (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
            'notes': 'Test rental order'
        }
        
        url = reverse('rental-order-create-from-cart')
        response = self.client.post(url, cart_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_list_user_orders(self):
        """Test listing user orders."""
        # Create test order
        order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        url = reverse('rental-order-my-orders')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['order_number'], order.order_number)
    
    def test_cancel_rental_order(self):
        """Test cancelling a rental order."""
        # Create test order
        order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        # Create order item
        RentalOrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('25.00'),
            deposit_per_unit=Decimal('50.00')
        )
        
        # Reserve quantity
        self.product.reserve_quantity(2)
        
        url = reverse('rental-order-cancel-order', kwargs={'pk': order.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify order was cancelled
        order.refresh_from_db()
        self.assertEqual(order.status, 'CANCELLED')
        
        # Verify quantities were released
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_quantity, 10)


class StripeWebhookTestCase(TestCase):
    """Test cases for Stripe webhook handling."""
    
    def setUp(self):
        """Set up test data."""
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
            role='CUSTOMER',
            is_active=True
        )
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.user,
            category=self.category,
            short_description='Test product description',
            description='Detailed test product description',
            condition='GOOD',
            status='AVAILABLE',
            total_quantity=10,
            available_quantity=10,
            deposit_amount=Decimal('100.00'),
            is_rentable=True,
            admin_approved=True
        )
        
        # Create payment gateway
        self.gateway = PaymentGateway.objects.create(
            name='Test Stripe Gateway',
            gateway_type='STRIPE',
            is_active=True,
            is_test_mode=True
        )
        
        # Create test order
        self.order = RentalOrder.objects.create(
            customer=self.user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        # Create test payment
        self.payment = Payment.objects.create(
            order=self.order,
            payment_type='FULL_UPFRONT',
            amount=Decimal('154.25'),
            gateway=self.gateway,
            status='PENDING',
            gateway_transaction_id='cs_test_123'
        )
        
        # Create client
        self.client = Client()
    
    @patch('stripe.Webhook.construct_event')
    def test_webhook_checkout_session_completed(self, mock_construct_event):
        """Test webhook handling for completed checkout session."""
        # Mock webhook event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'metadata': {
                        'order_id': str(self.order.id),
                        'payment_id': str(self.payment.payment_id)
                    }
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Create webhook payload
        payload = json.dumps(mock_event).encode()
        
        # Make webhook request
        response = self.client.post(
            reverse('stripe-webhook'),
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify payment was updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CONFIRMED')
    
    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_intent_failed(self, mock_construct_event):
        """Test webhook handling for failed payment intent."""
        # Mock webhook event
        mock_event = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'metadata': {
                        'session_id': 'cs_test_123'
                    },
                    'last_payment_error': {
                        'message': 'Card declined'
                    }
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Reserve quantity for the order
        self.product.reserve_quantity(1)
        
        # Create webhook payload
        payload = json.dumps(mock_event).encode()
        
        # Make webhook request
        response = self.client.post(
            reverse('stripe-webhook'),
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify payment was updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'FAILED')
        
        # Verify quantities were released
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_quantity, 10)


class PaymentPermissionsTestCase(APITestCase):
    """Test cases for payment permissions."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users with different roles
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            first_name='Customer',
            last_name='User'
        )
        
        self.staff = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            first_name='Staff',
            last_name='User'
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create user roles
        UserRole.objects.create(user=self.customer, role='CUSTOMER', is_active=True)
        UserRole.objects.create(user=self.staff, role='STAFF', is_active=True)
        UserRole.objects.create(user=self.admin, role='ADMIN', is_active=True)
        
        # Create test data
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.customer,
            category=self.category,
            short_description='Test product description',
            description='Detailed test product description',
            condition='GOOD',
            status='AVAILABLE',
            total_quantity=10,
            available_quantity=10,
            deposit_amount=Decimal('100.00'),
            is_rentable=True,
            admin_approved=True
        )
        
        self.gateway = PaymentGateway.objects.create(
            name='Test Stripe Gateway',
            gateway_type='STRIPE',
            is_active=True,
            is_test_mode=True
        )
        
        self.order = RentalOrder.objects.create(
            customer=self.customer,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
    
    def test_customer_can_view_own_orders(self):
        """Test that customers can view their own orders."""
        self.client.force_authenticate(user=self.customer)
        
        url = reverse('rental-order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def test_customer_cannot_view_other_orders(self):
        """Test that customers cannot view other users' orders."""
        # Create another order for different customer
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        UserRole.objects.create(user=other_user, role='CUSTOMER', is_active=True)
        
        other_order = RentalOrder.objects.create(
            customer=other_user,
            rental_start_date=timezone.now() + timezone.timedelta(hours=1),
            rental_end_date=timezone.now() + timezone.timedelta(hours=25),
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('4.25'),
            total_amount=Decimal('154.25'),
            deposit_amount=Decimal('100.00')
        )
        
        self.client.force_authenticate(user=self.customer)
        
        url = reverse('rental-order-detail', kwargs={'pk': other_order.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_staff_can_view_all_orders(self):
        """Test that staff can view all orders."""
        self.client.force_authenticate(user=self.staff)
        
        url = reverse('rental-order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def test_admin_can_view_all_orders(self):
        """Test that admins can view all orders."""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('rental-order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
