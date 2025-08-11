"""
Payment models for the rental backend application.

This module contains models for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade security.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from core.models import BaseModel
import uuid
import json

User = get_user_model()


class PaymentMethod(BaseModel):
    """Payment methods supported by the system."""
    
    METHOD_TYPE_CHOICES = [
        ('CREDIT_CARD', _('Credit Card')),
        ('DEBIT_CARD', _('Debit Card')),
        ('BANK_TRANSFER', _('Bank Transfer')),
        ('DIGITAL_WALLET', _('Digital Wallet')),
        ('UPI', _('UPI')),
        ('NET_BANKING', _('Net Banking')),
        ('CASH', _('Cash')),
        ('CHEQUE', _('Cheque')),
    ]
    
    PROVIDER_CHOICES = [
        ('STRIPE', _('Stripe')),
        ('RAZORPAY', _('Razorpay')),
        ('PAYTM', _('Paytm')),
        ('PHONEPE', _('PhonePe')),
        ('GOOGLE_PAY', _('Google Pay')),
        ('APPLE_PAY', _('Apple Pay')),
        ('BANK', _('Bank')),
        ('CASH', _('Cash')),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Method Name"))
    method_type = models.CharField(
        max_length=20, 
        choices=METHOD_TYPE_CHOICES, 
        verbose_name=_("Method Type")
    )
    provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES, 
        verbose_name=_("Provider")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class"))
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    
    # Fee structure
    processing_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Processing Fee Percentage")
    )
    processing_fee_fixed = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Fixed Processing Fee")
    )
    
    # Limits
    minimum_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Minimum Amount")
    )
    maximum_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=999999.99,
        validators=[MinValueValidator(0)],
        verbose_name=_("Maximum Amount")
    )
    
    # Provider configuration
    provider_config = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Provider Configuration")
    )
    
    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['method_type', 'is_active']),
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"
    
    def save(self, *args, **kwargs):
        """Ensure only one default payment method per type."""
        if self.is_default:
            PaymentMethod.objects.filter(
                method_type=self.method_type, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
    
    def calculate_processing_fee(self, amount):
        """Calculate processing fee for a given amount."""
        percentage_fee = amount * (self.processing_fee_percentage / 100)
        total_fee = percentage_fee + self.processing_fee_fixed
        return min(total_fee, amount)  # Fee cannot exceed amount
    
    def is_valid_for_amount(self, amount):
        """Check if payment method is valid for the given amount."""
        return self.minimum_amount <= amount <= self.maximum_amount


class CheckoutSession(BaseModel):
    """Checkout sessions for payment processing."""
    
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('CANCELLED', _('Cancelled')),
        ('EXPIRED', _('Expired')),
    ]
    
    session_id = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Session ID")
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='checkout_sessions',
        verbose_name=_("User")
    )
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.PROTECT, 
        related_name='checkout_sessions',
        verbose_name=_("Payment Method")
    )
    
    # Amount details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Amount")
    )
    currency = models.CharField(
        max_length=3, 
        default='INR', 
        verbose_name=_("Currency")
    )
    processing_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Processing Fee")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Total Amount")
    )
    
    # Session details
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Status")
    )
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    
    # Payment details
    payment_intent_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Payment Intent ID")
    )
    checkout_url = models.URLField(
        blank=True, 
        verbose_name=_("Checkout URL")
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Metadata")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Paid At"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled At"))
    
    class Meta:
        verbose_name = _("Checkout Session")
        verbose_name_plural = _("Checkout Sessions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['payment_intent_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Generate session ID and calculate fees if not set."""
        if not self.session_id:
            self.session_id = f"cs_{uuid.uuid4().hex[:16]}"
        
        if not self.processing_fee:
            self.processing_fee = self.payment_method.calculate_processing_fee(self.amount)
        
        if not self.total_amount:
            self.total_amount = self.amount + self.processing_fee
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if the session has expired."""
        return timezone.now() > self.expires_at
    
    def can_be_paid(self):
        """Check if the session can be paid."""
        return (
            self.status == 'PENDING' and 
            not self.is_expired() and 
            self.payment_method.is_valid_for_amount(self.amount)
        )
    
    def mark_as_paid(self):
        """Mark the session as paid."""
        self.status = 'COMPLETED'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark the session as failed."""
        self.status = 'FAILED'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_cancelled(self):
        """Mark the session as cancelled."""
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.save(update_fields=['status', 'cancelled_at', 'updated_at'])
    
    def get_payment_url(self):
        """Get the payment URL for this session."""
        if self.checkout_url:
            return self.checkout_url
        # Generate URL based on payment method provider
        return f"/payments/checkout/{self.session_id}/"


class Payment(BaseModel):
    """Payment records for tracking all transactions."""
    
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('CANCELLED', _('Cancelled')),
        ('REFUNDED', _('Refunded')),
        ('PARTIALLY_REFUNDED', _('Partially Refunded')),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('RENTAL_PAYMENT', _('Rental Payment')),
        ('DEPOSIT', _('Security Deposit')),
        ('LATE_FEE', _('Late Return Fee')),
        ('DAMAGE_FEE', _('Damage Fee')),
        ('SUBSCRIPTION', _('Subscription Payment')),
        ('REFUND', _('Refund')),
        ('ADJUSTMENT', _('Adjustment')),
    ]
    
    payment_id = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Payment ID")
    )
    checkout_session = models.ForeignKey(
        CheckoutSession, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name=_("Checkout Session")
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name=_("User")
    )
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.PROTECT, 
        related_name='payments',
        verbose_name=_("Payment Method")
    )
    
    # Amount details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Amount")
    )
    currency = models.CharField(
        max_length=3, 
        default='INR', 
        verbose_name=_("Currency")
    )
    processing_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Processing Fee")
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Total Amount")
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE_CHOICES, 
        verbose_name=_("Transaction Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Status")
    )
    
    # Provider details
    provider_payment_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Provider Payment ID")
    )
    provider_transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Provider Transaction ID")
    )
    
    # Payment details
    payment_intent_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Payment Intent ID")
    )
    payment_method_details = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Payment Method Details")
    )
    
    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Failed At"))
    
    # Error handling
    error_code = models.CharField(max_length=50, blank=True, verbose_name=_("Error Code"))
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
    
    # Metadata
    metadata = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Metadata")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Audit fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_payments',
        verbose_name=_("Created By")
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_payments',
        verbose_name=_("Updated By")
    )
    
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['provider_payment_id']),
            models.Index(fields=['payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Generate payment ID if not set."""
        if not self.payment_id:
            self.payment_id = f"pay_{uuid.uuid4().hex[:16]}"
        super().save(*args, **kwargs)
    
    def mark_as_completed(self, provider_payment_id=None, provider_transaction_id=None):
        """Mark payment as completed."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if provider_payment_id:
            self.provider_payment_id = provider_payment_id
        if provider_transaction_id:
            self.provider_transaction_id = provider_transaction_id
        self.save(update_fields=[
            'status', 'completed_at', 'provider_payment_id', 
            'provider_transaction_id', 'updated_at'
        ])
    
    def mark_as_failed(self, error_code=None, error_message=None):
        """Mark payment as failed."""
        self.status = 'FAILED'
        self.failed_at = timezone.now()
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save(update_fields=[
            'status', 'failed_at', 'error_code', 'error_message', 'updated_at'
        ])
    
    def mark_as_processing(self):
        """Mark payment as processing."""
        self.status = 'PROCESSING'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at', 'updated_at'])
    
    def can_be_refunded(self):
        """Check if payment can be refunded."""
        return self.status == 'COMPLETED' and self.amount > 0
    
    def get_refund_amount(self):
        """Get the maximum amount that can be refunded."""
        if self.status == 'COMPLETED':
            return self.amount
        return 0


class PaymentWebhook(BaseModel):
    """Webhook events from payment providers."""
    
    EVENT_TYPE_CHOICES = [
        ('PAYMENT_INTENT_CREATED', _('Payment Intent Created')),
        ('PAYMENT_INTENT_SUCCEEDED', _('Payment Intent Succeeded')),
        ('PAYMENT_INTENT_FAILED', _('Payment Intent Failed')),
        ('PAYMENT_INTENT_CANCELLED', _('Payment Intent Cancelled')),
        ('PAYMENT_METHOD_ATTACHED', _('Payment Method Attached')),
        ('PAYMENT_METHOD_DETACHED', _('Payment Method Detached')),
        ('REFUND_CREATED', _('Refund Created')),
        ('REFUND_SUCCEEDED', _('Refund Succeeded')),
        ('REFUND_FAILED', _('Refund Failed')),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSED', _('Processed')),
        ('FAILED', _('Failed')),
        ('IGNORED', _('Ignored')),
    ]
    
    webhook_id = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Webhook ID")
    )
    provider = models.CharField(
        max_length=20, 
        choices=PaymentMethod.PROVIDER_CHOICES, 
        verbose_name=_("Provider")
    )
    event_type = models.CharField(
        max_length=50, 
        choices=EVENT_TYPE_CHOICES, 
        verbose_name=_("Event Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Status")
    )
    
    # Event details
    event_id = models.CharField(
        max_length=100, 
        verbose_name=_("Event ID")
    )
    object_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Object ID")
    )
    
    # Payload
    raw_payload = models.TextField(verbose_name=_("Raw Payload"))
    processed_payload = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Processed Payload")
    )
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
    retry_count = models.PositiveIntegerField(default=0, verbose_name=_("Retry Count"))
    
    # Headers
    headers = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Headers")
    )
    signature = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name=_("Signature")
    )
    
    class Meta:
        verbose_name = _("Payment Webhook")
        verbose_name_plural = _("Payment Webhooks")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook_id']),
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['event_id']),
            models.Index(fields=['object_id']),
        ]
    
    def __str__(self):
        return f"Webhook {self.webhook_id} - {self.get_event_type_display()}"
    
    def save(self, *args, **kwargs):
        """Generate webhook ID if not set."""
        if not self.webhook_id:
            self.webhook_id = f"wh_{uuid.uuid4().hex[:16]}"
        super().save(*args, **kwargs)
    
    def mark_as_processed(self):
        """Mark webhook as processed."""
        self.status = 'PROCESSED'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at', 'updated_at'])
    
    def mark_as_failed(self, error_message):
        """Mark webhook as failed."""
        self.status = 'FAILED'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count', 'updated_at'])
    
    def mark_as_ignored(self):
        """Mark webhook as ignored."""
        self.status = 'IGNORED'
        self.save(update_fields=['status', 'updated_at'])
    
    def can_retry(self):
        """Check if webhook can be retried."""
        return self.status == 'FAILED' and self.retry_count < 3


class PaymentRefund(BaseModel):
    """Refund records for payments."""
    
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    REFUND_REASON_CHOICES = [
        ('REQUESTED_BY_CUSTOMER', _('Requested by Customer')),
        ('DUPLICATE', _('Duplicate Payment')),
        ('FRAUDULENT', _('Fraudulent Payment')),
        ('PRODUCT_NOT_RECEIVED', _('Product Not Received')),
        ('PRODUCT_DEFECTIVE', _('Product Defective')),
        ('SERVICE_NOT_PROVIDED', _('Service Not Provided')),
        ('ADMINISTRATIVE', _('Administrative')),
        ('OTHER', _('Other')),
    ]
    
    refund_id = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Refund ID")
    )
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='refunds',
        verbose_name=_("Payment")
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='refunds',
        verbose_name=_("User")
    )
    
    # Amount details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Refund Amount")
    )
    currency = models.CharField(
        max_length=3, 
        default='INR', 
        verbose_name=_("Currency")
    )
    
    # Refund details
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Status")
    )
    reason = models.CharField(
        max_length=30, 
        choices=REFUND_REASON_CHOICES, 
        verbose_name=_("Refund Reason")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Provider details
    provider_refund_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Provider Refund ID")
    )
    
    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Failed At"))
    
    # Error handling
    error_code = models.CharField(max_length=50, blank=True, verbose_name=_("Error Code"))
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
    
    # Audit fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_refunds',
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Payment Refund")
        verbose_name_plural = _("Payment Refunds")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['refund_id']),
            models.Index(fields=['payment', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_refund_id']),
        ]
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Generate refund ID if not set and validate amount."""
        if not self.refund_id:
            self.refund_id = f"ref_{uuid.uuid4().hex[:16]}"
        
        # Validate refund amount
        if self.amount > self.payment.amount:
            raise ValidationError(_("Refund amount cannot exceed payment amount."))
        
        super().save(*args, **kwargs)
    
    def mark_as_completed(self, provider_refund_id=None):
        """Mark refund as completed."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if provider_refund_id:
            self.provider_refund_id = provider_refund_id
        self.save(update_fields=[
            'status', 'completed_at', 'provider_refund_id', 'updated_at'
        ])
    
    def mark_as_failed(self, error_code=None, error_message=None):
        """Mark refund as failed."""
        self.status = 'FAILED'
        self.failed_at = timezone.now()
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save(update_fields=[
            'status', 'failed_at', 'error_code', 'error_message', 'updated_at'
        ])
    
    def mark_as_processing(self):
        """Mark refund as processing."""
        self.status = 'PROCESSING'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at', 'updated_at'])
