from django.db import models
from user.models import User
from core.models import BaseModel
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal
import uuid
from products.models import Product,ProductCategory


class RentalOrder(BaseModel):
    """Rental order model."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('PICKED_UP', 'Picked Up'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    # Basic info
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='rental_orders_payments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Dates
    rental_start_date = models.DateTimeField()
    rental_end_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['rental_start_date', 'rental_end_date']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        import datetime
        today = datetime.date.today()
        prefix = f"RO{today.strftime('%Y%m%d')}"
        
        last_order = RentalOrder.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()
        
        if last_order:
            last_number = int(last_order.order_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"


class RentalOrderItem(BaseModel):
    """Items in a rental order."""
    
    order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='items_payments')
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        indexes = [models.Index(fields=['order', 'product'])]
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class PaymentGateway(BaseModel):
    """Payment gateway configuration."""
    
    GATEWAY_TYPES = [
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
        ('RAZORPAY', 'Razorpay'),
        ('CASH', 'Cash'),
    ]
    
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    
    # Credentials (store encrypted in production)
    api_key = models.CharField(max_length=500, blank=True)
    secret_key = models.CharField(max_length=500, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    
    class Meta:
        indexes = [models.Index(fields=['gateway_type', 'is_active'])]
    
    def __str__(self):
        return self.name


class Payment(BaseModel):
    """Payment transactions."""
    
    PAYMENT_TYPES = [
        ('DEPOSIT', 'Security Deposit'),
        ('RENTAL', 'Rental Payment'),
        ('FULL_UPFRONT', 'Full Payment'),
        ('PARTIAL', 'Partial Payment'),
        ('LATE_FEE', 'Late Fee'),
        ('REFUND', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Basic info
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(RentalOrder, on_delete=models.PROTECT, related_name='payments')
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Gateway info
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'payment_type']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}"


class PaymentSchedule(BaseModel):
    """Payment schedule for orders with multiple payments."""
    
    order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='payment_schedule')
    payment_type = models.CharField(max_length=20, choices=Payment.PAYMENT_TYPES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    
    # Link to actual payment when made
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'due_date']),
            models.Index(fields=['is_paid']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.payment_type} - ${self.amount}"


# Notification model for payment reminders
class PaymentNotification(BaseModel):
    """Payment notifications and reminders."""
    
    NOTIFICATION_TYPES = [
        ('PAYMENT_DUE', 'Payment Due'),
        ('PAYMENT_OVERDUE', 'Payment Overdue'),
        ('RETURN_REMINDER', 'Return Reminder'),
        ('PAYMENT_CONFIRMED', 'Payment Confirmed'),
    ]
    
    order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Notification details
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Delivery
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'notification_type']),
            models.Index(fields=['is_sent', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.notification_type}"