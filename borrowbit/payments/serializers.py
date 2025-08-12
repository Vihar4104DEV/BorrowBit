"""
Serializers for payment management with role-based access control.
"""
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from decimal import Decimal
import uuid
from django.utils import timezone

from .models import (
    RentalOrder, RentalOrderItem, Payment, PaymentGateway, 
    PaymentSchedule, PaymentNotification
)
from products.models import Product, ProductPricing
from user.models import User
from core.utils import cache_key_generator, set_cache_data, get_cache_data, delete_cache_data


class RentalOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for rental order items."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalOrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_image',
            'quantity', 'unit_price', 'total_price', 'deposit_per_unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'total_price', 'created_at', 'updated_at']
    
    def get_product_image(self, obj):
        """Get product main image URL."""
        if obj.product.main_image:
            return self.context['request'].build_absolute_uri(obj.product.main_image.url)
        return None


class RentalOrderCreateSerializer(serializers.Serializer):
    """Serializer for creating rental orders from cart."""
    
    cart_items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text=_("List of cart items with product_id, quantity, and rental dates")
    )
    rental_start_date = serializers.DateTimeField()
    rental_end_date = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate cart items and rental dates."""
        cart_items = data['cart_items']
        start_date = data['rental_start_date']
        end_date = data['rental_end_date']
        
        if start_date >= end_date:
            raise ValidationError(_("Rental end date must be after start date."))
        
        if start_date <= timezone.now():
            raise ValidationError(_("Rental start date must be in the future."))
        
        # Validate each cart item
        for item in cart_items:
            if 'product_id' not in item or 'quantity' not in item:
                raise ValidationError(_("Each cart item must have product_id and quantity."))
            
            try:
                product = Product.objects.get(id=item['product_id'], is_active=True, is_deleted=False)
            except Product.DoesNotExist:
                raise ValidationError(_(f"Product with ID {item['product_id']} not found."))
            
            if not product.is_rentable:
                raise ValidationError(_(f"Product {product.name} is not available for rental."))
            
            if product.available_quantity < item['quantity']:
                raise ValidationError(_(f"Insufficient quantity available for {product.name}."))
            
            # Check if product is available for the specified dates
            if not product.is_available_for_rental(start_date, end_date, item['quantity']):
                raise ValidationError(_(f"Product {product.name} is not available for the specified dates."))
        
        return data


class RentalOrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for rental orders."""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    items = RentalOrderItemSerializer(many=True, read_only=True)
    payments = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RentalOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'customer_email',
            'status', 'status_display', 'rental_start_date', 'rental_end_date',
            'actual_return_date', 'subtotal', 'tax_amount', 'late_fee_amount',
            'total_amount', 'deposit_amount', 'notes', 'items', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
        
    def get_payments(self, obj):
        """Get related payments for the order."""
        payments = obj.payments.all()
        return PaymentSerializer(payments, many=True, context=self.context).data


class RentalOrderListSerializer(serializers.ModelSerializer):
    """List serializer for rental orders with minimal information."""
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RentalOrder
        fields = [
            'id', 'order_number', 'customer_name', 'status', 'status_display',
            'rental_start_date', 'rental_end_date', 'total_amount', 'items_count',
            'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
    
    def get_items_count(self, obj):
        """Get count of items in the order."""
        return obj.items.count()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions."""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'order', 'order_number', 'payment_type',
            'payment_type_display', 'amount', 'status', 'status_display',
            'gateway', 'gateway_name', 'gateway_transaction_id',
            'payment_date', 'due_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']


class StripeCheckoutSessionSerializer(serializers.Serializer):
    """Serializer for Stripe checkout session creation."""
    
    order_id = serializers.UUIDField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    
    def validate_order_id(self, value):
        """Validate that the order exists and belongs to the user."""
        try:
            order = RentalOrder.objects.get(
                id=value,
                customer=self.context['request'].user,
                status='DRAFT'
            )
        except RentalOrder.DoesNotExist:
            raise ValidationError(_("Order not found or not in draft status."))
        return value


class StripeWebhookSerializer(serializers.Serializer):
    """Serializer for Stripe webhook data."""
    
    id = serializers.CharField()
    object = serializers.CharField()
    type = serializers.CharField()
    data = serializers.DictField()
    
    def validate(self, data):
        """Basic validation for webhook data."""
        if data['object'] != 'event':
            raise ValidationError(_("Invalid webhook object type."))
        return data


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Serializer for payment gateways."""
    
    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'is_active', 'is_test_mode',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer for payment schedules."""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    
    class Meta:
        model = PaymentSchedule
        fields = [
            'id', 'order', 'payment_type', 'payment_type_display', 'amount',
            'due_date', 'is_paid', 'payment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentNotificationSerializer(serializers.ModelSerializer):
    """Serializer for payment notifications."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = PaymentNotification
        fields = [
            'id', 'order', 'notification_type', 'notification_type_display',
            'subject', 'message', 'is_sent', 'sent_at', 'scheduled_for',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
