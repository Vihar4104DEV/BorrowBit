"""
Serializers for payment models with comprehensive validation and security.

This module contains serializers for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade validation.
"""
from rest_framework import serializers
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db import transaction
from .models import (
    PaymentMethod, CheckoutSession, Payment, PaymentWebhook, PaymentRefund
)
from user.models import User
from core.utils import success_response, error_response


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods."""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'method_type', 'provider', 'description', 'icon',
            'is_active', 'is_default', 'sort_order', 'processing_fee_percentage',
            'processing_fee_fixed', 'minimum_amount', 'maximum_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate payment method data."""
        # Ensure only one default method per type
        if attrs.get('is_default', False):
            method_type = attrs.get('method_type')
            if method_type:
                existing_default = PaymentMethod.objects.filter(
                    method_type=method_type,
                    is_default=True,
                    is_deleted=False
                ).exclude(id=self.instance.id if self.instance else None)
                
                if existing_default.exists():
                    raise serializers.ValidationError(
                        f"A default payment method already exists for {method_type}"
                    )
        
        # Validate fee structure
        processing_fee_percentage = attrs.get('processing_fee_percentage', 0)
        if processing_fee_percentage > 100:
            raise serializers.ValidationError(
                "Processing fee percentage cannot exceed 100%"
            )
        
        # Validate amount limits
        minimum_amount = attrs.get('minimum_amount', 0)
        maximum_amount = attrs.get('maximum_amount', 999999.99)
        if minimum_amount >= maximum_amount:
            raise serializers.ValidationError(
                "Minimum amount must be less than maximum amount"
            )
        
        return attrs


class PaymentMethodListSerializer(serializers.ModelSerializer):
    """Simplified serializer for payment method listing."""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'method_type', 'provider', 'icon', 'is_active',
            'is_default', 'processing_fee_percentage', 'processing_fee_fixed',
            'minimum_amount', 'maximum_amount'
        ]


class CheckoutSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating checkout sessions."""
    
    payment_method_id = serializers.UUIDField(write_only=True)
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    currency = serializers.CharField(max_length=3, default='INR')
    description = serializers.CharField(max_length=500, required=False)
    metadata = serializers.JSONField(required=False, default=dict)
    
    class Meta:
        model = CheckoutSession
        fields = [
            'payment_method_id', 'amount', 'currency', 'description', 
            'metadata', 'expires_at'
        ]
    
    def validate(self, attrs):
        """Validate checkout session data."""
        user = self.context['request'].user
        payment_method_id = attrs.get('payment_method_id')
        amount = attrs.get('amount')
        
        # Validate payment method
        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                is_active=True,
                is_deleted=False
            )
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("Invalid payment method")
        
        # Validate amount limits
        if not payment_method.is_valid_for_amount(amount):
            raise serializers.ValidationError(
                f"Amount must be between {payment_method.minimum_amount} and {payment_method.maximum_amount}"
            )
        
        # Set expires_at if not provided (default 30 minutes)
        if 'expires_at' not in attrs:
            attrs['expires_at'] = timezone.now() + timezone.timedelta(minutes=30)
        
        # Validate expiration time
        if attrs['expires_at'] <= timezone.now():
            raise serializers.ValidationError("Expiration time must be in the future")
        
        # Add payment method to attrs
        attrs['payment_method'] = payment_method
        attrs['user'] = user
        
        return attrs
    
    def create(self, validated_data):
        """Create checkout session with calculated fees."""
        payment_method = validated_data.pop('payment_method')
        user = validated_data.pop('user')
        
        # Calculate processing fee
        amount = validated_data['amount']
        processing_fee = payment_method.calculate_processing_fee(amount)
        total_amount = amount + processing_fee
        
        checkout_session = CheckoutSession.objects.create(
            user=user,
            payment_method=payment_method,
            processing_fee=processing_fee,
            total_amount=total_amount,
            **validated_data
        )
        
        return checkout_session


class CheckoutSessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for checkout session details."""
    
    payment_method = PaymentMethodListSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    payment_url = serializers.SerializerMethodField()
    can_be_paid = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'session_id', 'user', 'payment_method', 'amount', 'currency',
            'processing_fee', 'total_amount', 'status', 'expires_at',
            'payment_intent_id', 'checkout_url', 'payment_url', 'metadata',
            'description', 'can_be_paid', 'is_expired', 'paid_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'session_id', 'user', 'payment_method', 'processing_fee',
            'total_amount', 'status', 'payment_intent_id', 'checkout_url',
            'payment_url', 'can_be_paid', 'is_expired', 'paid_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]
    
    def get_user(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }
    
    def get_payment_url(self, obj):
        """Get payment URL."""
        return obj.get_payment_url()
    
    def get_can_be_paid(self, obj):
        """Check if session can be paid."""
        return obj.can_be_paid()
    
    def get_is_expired(self, obj):
        """Check if session is expired."""
        return obj.is_expired()


class CheckoutSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for checkout session listing."""
    
    payment_method = PaymentMethodListSerializer(read_only=True)
    can_be_paid = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'session_id', 'payment_method', 'amount', 'currency',
            'total_amount', 'status', 'expires_at', 'can_be_paid', 'is_expired',
            'created_at'
        ]
    
    def get_can_be_paid(self, obj):
        """Check if session can be paid."""
        return obj.can_be_paid()
    
    def get_is_expired(self, obj):
        """Check if session is expired."""
        return obj.is_expired()


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    checkout_session_id = serializers.UUIDField(write_only=True)
    payment_method_details = serializers.JSONField(required=False, default=dict)
    
    class Meta:
        model = Payment
        fields = [
            'checkout_session_id', 'transaction_type', 'description',
            'payment_method_details', 'metadata'
        ]
    
    def validate(self, attrs):
        """Validate payment data."""
        checkout_session_id = attrs.get('checkout_session_id')
        user = self.context['request'].user
        
        # Validate checkout session
        try:
            checkout_session = CheckoutSession.objects.get(
                id=checkout_session_id,
                user=user,
                is_deleted=False
            )
        except CheckoutSession.DoesNotExist:
            raise serializers.ValidationError("Invalid checkout session")
        
        # Check if session can be paid
        if not checkout_session.can_be_paid():
            raise serializers.ValidationError("Checkout session cannot be paid")
        
        # Add checkout session to attrs
        attrs['checkout_session'] = checkout_session
        attrs['user'] = user
        attrs['payment_method'] = checkout_session.payment_method
        attrs['amount'] = checkout_session.amount
        attrs['currency'] = checkout_session.currency
        attrs['processing_fee'] = checkout_session.processing_fee
        attrs['total_amount'] = checkout_session.total_amount
        
        return attrs
    
    def create(self, validated_data):
        """Create payment and update checkout session."""
        checkout_session = validated_data.pop('checkout_session')
        
        with transaction.atomic():
            # Create payment
            payment = Payment.objects.create(
                checkout_session=checkout_session,
                created_by=self.context['request'].user,
                **validated_data
            )
            
            # Mark checkout session as processing
            checkout_session.status = 'PROCESSING'
            checkout_session.save(update_fields=['status', 'updated_at'])
            
            # Mark payment as processing
            payment.mark_as_processing()
        
        return payment


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment details."""
    
    checkout_session = CheckoutSessionDetailSerializer(read_only=True)
    payment_method = PaymentMethodListSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    can_be_refunded = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'checkout_session', 'user', 'payment_method',
            'amount', 'currency', 'processing_fee', 'total_amount',
            'transaction_type', 'status', 'provider_payment_id',
            'provider_transaction_id', 'payment_intent_id',
            'payment_method_details', 'processed_at', 'completed_at',
            'failed_at', 'error_code', 'error_message', 'metadata',
            'description', 'can_be_refunded', 'refund_amount', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'payment_id', 'checkout_session', 'user', 'payment_method',
            'amount', 'currency', 'processing_fee', 'total_amount',
            'provider_payment_id', 'provider_transaction_id',
            'payment_intent_id', 'processed_at', 'completed_at', 'failed_at',
            'error_code', 'error_message', 'can_be_refunded', 'refund_amount',
            'created_at', 'updated_at'
        ]
    
    def get_user(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }
    
    def get_can_be_refunded(self, obj):
        """Check if payment can be refunded."""
        return obj.can_be_refunded()
    
    def get_refund_amount(self, obj):
        """Get refund amount."""
        return obj.get_refund_amount()


class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for payment listing."""
    
    payment_method = PaymentMethodListSerializer(read_only=True)
    can_be_refunded = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'payment_method', 'amount', 'currency',
            'total_amount', 'transaction_type', 'status', 'completed_at',
            'can_be_refunded', 'created_at'
        ]
    
    def get_can_be_refunded(self, obj):
        """Check if payment can be refunded."""
        return obj.can_be_refunded()


class PaymentRefundCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment refunds."""
    
    payment_id = serializers.UUIDField(write_only=True)
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    class Meta:
        model = PaymentRefund
        fields = [
            'payment_id', 'amount', 'reason', 'description'
        ]
    
    def validate(self, attrs):
        """Validate refund data."""
        payment_id = attrs.get('payment_id')
        amount = attrs.get('amount')
        user = self.context['request'].user
        
        # Validate payment
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=user,
                is_deleted=False
            )
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Invalid payment")
        
        # Check if payment can be refunded
        if not payment.can_be_refunded():
            raise serializers.ValidationError("Payment cannot be refunded")
        
        # Validate refund amount
        max_refund_amount = payment.get_refund_amount()
        if amount > max_refund_amount:
            raise serializers.ValidationError(
                f"Refund amount cannot exceed {max_refund_amount}"
            )
        
        # Add payment and user to attrs
        attrs['payment'] = payment
        attrs['user'] = user
        attrs['currency'] = payment.currency
        attrs['created_by'] = self.context['request'].user
        
        return attrs
    
    def create(self, validated_data):
        """Create refund."""
        payment = validated_data.pop('payment')
        
        with transaction.atomic():
            # Create refund
            refund = PaymentRefund.objects.create(**validated_data)
            
            # Update payment status if full refund
            if refund.amount >= payment.amount:
                payment.status = 'REFUNDED'
            else:
                payment.status = 'PARTIALLY_REFUNDED'
            payment.save(update_fields=['status', 'updated_at'])
        
        return refund


class PaymentRefundDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment refund details."""
    
    payment = PaymentDetailSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'payment', 'user', 'amount', 'currency',
            'status', 'reason', 'description', 'provider_refund_id',
            'processed_at', 'completed_at', 'failed_at', 'error_code',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'refund_id', 'payment', 'user', 'currency', 'status',
            'provider_refund_id', 'processed_at', 'completed_at', 'failed_at',
            'error_code', 'error_message', 'created_at', 'updated_at'
        ]
    
    def get_user(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }


class PaymentRefundListSerializer(serializers.ModelSerializer):
    """Simplified serializer for payment refund listing."""
    
    payment = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'payment', 'amount', 'currency', 'status',
            'reason', 'completed_at', 'created_at'
        ]
    
    def get_payment(self, obj):
        """Get payment information."""
        return {
            'id': obj.payment.id,
            'payment_id': obj.payment.payment_id,
            'amount': obj.payment.amount,
            'transaction_type': obj.payment.transaction_type
        }


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer for payment webhooks."""
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'webhook_id', 'provider', 'event_type', 'status',
            'event_id', 'object_id', 'processed_payload', 'processed_at',
            'error_message', 'retry_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'webhook_id', 'provider', 'event_type', 'status',
            'event_id', 'object_id', 'processed_payload', 'processed_at',
            'error_message', 'retry_count', 'created_at'
        ]


class UserPaymentSummarySerializer(serializers.Serializer):
    """Serializer for user payment summary."""
    
    total_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    total_refunds = serializers.IntegerField()
    refunded_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()


class PaymentAnalyticsSerializer(serializers.Serializer):
    """Serializer for payment analytics."""
    
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_transaction_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    period = serializers.CharField()
    data_points = serializers.ListField(child=serializers.DictField())

