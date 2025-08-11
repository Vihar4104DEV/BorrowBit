"""
Rental models for the rental backend application.

This module contains models for rental management including quotations, orders, and delivery.
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import BaseModel
from django.contrib.auth import get_user_model
from products.models import Product
import uuid

User = get_user_model()

def generate_quotation_number():
    """Generate a unique quotation number"""
    return f'QT{timezone.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}'

def generate_order_number():
    """Generate a unique order number"""
    return f'RO{timezone.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}'

class QuotationItem(BaseModel):
    """
    Items included in a rental quotation.
    This model must be defined before RentalQuotation due to the ManyToManyField relationship.
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT,
        verbose_name=_("Product"),
        related_name='quotation_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity")
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_("Price Per Unit")
    )
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name=_("Subtotal"),
        help_text=_("Price per unit * quantity")
    )

    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.price_per_unit * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Quotation Item")
        verbose_name_plural = _("Quotation Items")

class RentalQuotation(BaseModel):
    """Rental quotation model for managing rental requests"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CONVERTED', 'Converted to Order'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    DELIVERY_CHOICES = [
        ('PICKUP', 'Self Pickup'),
        ('DELIVERY', 'Home Delivery')
    ]
    
    quotation_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_quotation_number,
        verbose_name=_("Quotation Number")
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='rental_quotations',
        verbose_name=_("Customer")
    )
    products = models.ManyToManyField(
        Product,
        through=QuotationItem,
        verbose_name=_("Products")
    )
    items = models.ManyToManyField(
        QuotationItem,
        related_name='quotation',
        verbose_name=_("Quotation Items")
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Total Amount")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name=_("Status")
    )
    rental_start = models.DateTimeField(verbose_name=_("Rental Start Date"))
    rental_end = models.DateTimeField(verbose_name=_("Rental End Date"))
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        verbose_name=_("Delivery Type")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )

    class Meta:
        verbose_name = _("Rental Quotation")
        verbose_name_plural = _("Rental Quotations")
        indexes = [
            models.Index(fields=['quotation_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['rental_start', 'rental_end'])
        ]
        ordering = ['-created_at']

    def clean(self):
        """Validate the model data"""
        if self.rental_end <= self.rental_start:
            raise ValidationError({
                'rental_end': _("End date must be after start date")
            })

    def save(self, *args, **kwargs):
        """Calculate total amount before saving"""
        if self.pk:  # Only calculate if quotation exists
            self.total_amount = sum(item.subtotal for item in self.items.all())
        super().save(*args, **kwargs)

class RentalOrder(BaseModel):
    """Model for confirmed rental orders"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    order_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_order_number,
        verbose_name=_("Order Number")
    )
    quotation = models.OneToOneField(
        RentalQuotation,
        on_delete=models.PROTECT,
        related_name='order',
        verbose_name=_("Quotation")
    )
    delivery_partner = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='deliveries',
        verbose_name=_("Delivery Partner")
    )
    pickup_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_("Pickup Status")
    )
    return_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_("Return Status")
    )
    pickup_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Actual Pickup Date")
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Actual Return Date")
    )
    pickup_report = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Pickup Condition Report")
    )
    return_report = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Return Condition Report")
    )
    late_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Late Fees")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )

    class Meta:
        verbose_name = _("Rental Order")
        verbose_name_plural = _("Rental Orders")
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['pickup_status', 'return_status']),
            models.Index(fields=['pickup_date', 'return_date'])
        ]
        ordering = ['-created_at']

    def calculate_late_fees(self):
        """Calculate late fees if return is delayed"""
        if self.return_date and self.quotation.rental_end:
            if self.return_date > self.quotation.rental_end:
                # Calculate late fees logic here
                pass
        return self.late_fees


class RentalQuotation(BaseModel):
    """Rental quotation model for customer inquiries."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Customer'),
        ('REVIEWED', 'Reviewed by Customer'),
        ('CONFIRMED', 'Confirmed by Customer'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Basic information
    quotation_number = models.CharField(max_length=50, unique=True, verbose_name=_("Quotation Number"))
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='rental_quotations',
        verbose_name=_("Customer")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='DRAFT',
        verbose_name=_("Status")
    )
    
    # Rental details
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    pickup_location = models.TextField(verbose_name=_("Pickup Location"))
    return_location = models.TextField(verbose_name=_("Return Location"))
    delivery_required = models.BooleanField(default=False, verbose_name=_("Delivery Required"))
    setup_required = models.BooleanField(default=False, verbose_name=_("Setup Required"))
    
    # Pricing and terms
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Subtotal")
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Tax Amount")
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Discount Amount")
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Total Amount")
    )
    
    # Terms and conditions
    terms_and_conditions = models.TextField(blank=True, verbose_name=_("Terms and Conditions"))
    special_instructions = models.TextField(blank=True, verbose_name=_("Special Instructions"))
    cancellation_policy = models.TextField(blank=True, verbose_name=_("Cancellation Policy"))
    
    # Validity and expiry
    valid_until = models.DateTimeField(verbose_name=_("Valid Until"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent At"))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reviewed At"))
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Confirmed At"))
    
    # Conversion to order
    # converted_to_order = models.ForeignKey(
    #     'RentalOrder', 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     blank=True,
    #     related_name='source_quotation_converted',
    #     verbose_name=_("Converted To Order")
    # )
    
    class Meta:
        verbose_name = _("Rental Quotation")
        verbose_name_plural = _("Rental Quotations")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['quotation_number']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'valid_until']),
        ]
    
    def __str__(self):
        return f"Quotation {self.quotation_number} for {self.customer.get_full_name()}"
    
    def get_duration_hours(self):
        """Calculate rental duration in hours."""
        duration = self.end_date - self.start_date
        return int(duration.total_seconds() / 3600)
    
    def get_duration_days(self):
        """Calculate rental duration in days."""
        duration = self.end_date - self.start_date
        return duration.days
    
    def calculate_totals(self):
        """Calculate quotation totals."""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'total_amount'])
    
    def is_expired(self):
        """Check if quotation has expired."""
        return timezone.now() > self.valid_until
    
    def can_be_confirmed(self):
        """Check if quotation can be confirmed."""
        return (
            self.status == 'REVIEWED' and 
            not self.is_expired() and
            self.items.exists()
        )
    
    def confirm(self):
        """Confirm the quotation."""
        if self.can_be_confirmed():
            self.status = 'CONFIRMED'
            self.confirmed_at = timezone.now()
            self.save(update_fields=['status', 'confirmed_at'])
            return True
        return False
    
    def send_to_customer(self):
        """Mark quotation as sent to customer."""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])


class RentalQuotationItem(BaseModel):
    """Individual items in a rental quotation."""
    
    quotation = models.ForeignKey(
        RentalQuotation, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_("Quotation")
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity")
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Unit Price")
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_("Total Price")
    )
    
    # Additional services
    setup_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Setup Fee")
    )
    delivery_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Delivery Fee")
    )
    
    # Notes
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Quotation Item")
        verbose_name_plural = _("Quotation Items")
        ordering = ['quotation', 'product']
        unique_together = ['quotation', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.quotation.quotation_number}"
    
    def calculate_total_price(self):
        """Calculate total price for this item."""
        self.total_price = (self.unit_price * self.quantity) + self.setup_fee + self.delivery_fee
        self.save(update_fields=['total_price'])
        return self.total_price


class RentalOrder(BaseModel):
    """Rental order model for confirmed rentals."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('READY_FOR_PICKUP', 'Ready for Pickup'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Payment Failed'),
    ]
    
    # Basic information
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_("Order Number"))
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='rental_orders',
        verbose_name=_("Customer")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Status")
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='PENDING',
        verbose_name=_("Payment Status")
    )
    
    # Rental details
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    actual_start_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual Start Date"))
    actual_end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual End Date"))
    
    # Location information
    pickup_location = models.TextField(verbose_name=_("Pickup Location"))
    return_location = models.TextField(verbose_name=_("Return Location"))
    delivery_required = models.BooleanField(default=False, verbose_name=_("Delivery Required"))
    setup_required = models.BooleanField(default=False, verbose_name=_("Setup Required"))
    
    # Pricing and payment
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Subtotal")
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Tax Amount")
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Discount Amount")
    )
    delivery_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Delivery Fee")
    )
    setup_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Setup Fee")
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Total Amount")
    )
    amount_paid = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Amount Paid")
    )
    balance_due = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Balance Due")
    )
    
    # Security and deposits
    security_deposit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Security Deposit")
    )
    security_deposit_paid = models.BooleanField(default=False, verbose_name=_("Security Deposit Paid"))
    security_deposit_refunded = models.BooleanField(default=False, verbose_name=_("Security Deposit Refunded"))
    
    # Late fees
    late_return_fee = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Late Return Fee")
    )
    late_return_fee_paid = models.BooleanField(default=False, verbose_name=_("Late Return Fee Paid"))
    
    # Terms and conditions
    terms_accepted = models.BooleanField(default=False, verbose_name=_("Terms Accepted"))
    terms_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Terms Accepted At"))
    
    # Customer information
    customer_signature = models.TextField(blank=True, verbose_name=_("Customer Signature"))
    customer_notes = models.TextField(blank=True, verbose_name=_("Customer Notes"))
    
    # Staff information
    assigned_staff = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_orders',
        verbose_name=_("Assigned Staff")
    )
    staff_notes = models.TextField(blank=True, verbose_name=_("Staff Notes"))
    
    # Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Confirmed At"))
    prepared_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Prepared At"))
    picked_up_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Picked Up At"))
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Returned At"))
    
    class Meta:
        verbose_name = _("Rental Order")
        verbose_name_plural = _("Rental Orders")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status', 'payment_status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} for {self.customer.get_full_name()}"
    
    def get_duration_hours(self):
        """Calculate rental duration in hours."""
        duration = self.end_date - self.start_date
        return int(duration.total_seconds() / 3600)
    
    def get_duration_days(self):
        """Calculate rental duration in days."""
        duration = self.end_date - self.start_date
        return duration.days
    
    def calculate_totals(self):
        """Calculate order totals."""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.delivery_fee + 
            self.setup_fee - 
            self.discount_amount
        )
        self.balance_due = self.total_amount - self.amount_paid
        self.save(update_fields=['subtotal', 'total_amount', 'balance_due'])
    
    def is_overdue(self):
        """Check if rental is overdue."""
        if self.status == 'ACTIVE' and self.actual_start_date:
            return timezone.now() > self.end_date
        return False
    
    def calculate_late_fees(self):
        """Calculate late return fees."""
        if self.is_overdue() and self.actual_start_date:
            overdue_days = (timezone.now() - self.end_date).days
            if overdue_days > 0:
                # Calculate late fees based on product pricing
                total_late_fee = 0
                for item in self.items.all():
                    if hasattr(item.product, 'pricing_rules'):
                        pricing = item.product.pricing_rules.filter(
                            customer_type='REGULAR'
                        ).first()
                        if pricing:
                            total_late_fee += pricing.late_return_fee_per_day * overdue_days * item.quantity
                
                self.late_return_fee = total_late_fee
                self.save(update_fields=['late_return_fee'])
                return total_late_fee
        return 0
    
    def confirm_order(self):
        """Confirm the rental order."""
        if self.status == 'PENDING':
            self.status = 'CONFIRMED'
            self.confirmed_at = timezone.now()
            self.save(update_fields=['status', 'confirmed_at'])
            
            # Reserve products
            for item in self.items.all():
                item.product.reserve_quantity(item.quantity)
            
            return True
        return False
    
    def start_rental(self):
        """Start the rental period."""
        if self.status == 'READY_FOR_PICKUP':
            self.status = 'ACTIVE'
            self.actual_start_date = timezone.now()
            self.save(update_fields=['status', 'actual_start_date'])
            return True
        return False
    
    def complete_rental(self):
        """Complete the rental period."""
        if self.status == 'ACTIVE':
            self.status = 'COMPLETED'
            self.actual_end_date = timezone.now()
            self.save(update_fields=['status', 'actual_end_date'])
            
            # Release product reservations
            for item in self.items.all():
                item.product.release_reservation(item.quantity)
            
            return True
        return False


class RentalOrderItem(BaseModel):
    """Individual items in a rental order."""
    
    order = models.ForeignKey(
        "RentalOrder", 
        on_delete=models.CASCADE, 
        related_name='rental_items',
        verbose_name=_("Order")
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity")
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Unit Price")
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_("Total Price")
    )
    
    # Additional services
    setup_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Setup Fee")
    )
    delivery_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Delivery Fee")
    )
    
    # Product condition
    condition_at_pickup = models.CharField(
        max_length=20,
        choices=Product.CONDITION_CHOICES,
        blank=True,
        verbose_name=_("Condition at Pickup")
    )
    condition_at_return = models.CharField(
        max_length=20,
        choices=Product.CONDITION_CHOICES,
        blank=True,
        verbose_name=_("Condition at Return")
    )
    
    # Notes
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ['order', 'product']
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.order.order_number}"
    
    def calculate_total_price(self):
        """Calculate total price for this item."""
        self.total_price = (self.unit_price * self.quantity) + self.setup_fee + self.delivery_fee
        self.save(update_fields=['total_price'])
        return self.total_price


class DeliverySchedule(BaseModel):
    """Delivery and pickup scheduling for rental orders."""
    
    TYPE_CHOICES = [
        ('DELIVERY', 'Delivery'),
        ('PICKUP', 'Pickup'),
        ('SETUP', 'Setup'),
        ('RETURN', 'Return'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('DELAYED', 'Delayed'),
    ]
    
    order = models.ForeignKey(
        "RentalOrder", 
        on_delete=models.CASCADE, 
        related_name='delivery_schedules',
        verbose_name=_("Order")
    )
    delivery_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        verbose_name=_("Delivery Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='SCHEDULED',
        verbose_name=_("Status")
    )
    
    # Scheduling
    scheduled_date = models.DateTimeField(verbose_name=_("Scheduled Date"))
    estimated_duration = models.PositiveIntegerField(
        default=60, 
        verbose_name=_("Estimated Duration (minutes)")
    )
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual Start Time"))
    actual_end_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual End Time"))
    
    # Location details
    address = models.TextField(verbose_name=_("Delivery Address"))
    contact_person = models.CharField(max_length=200, verbose_name=_("Contact Person"))
    contact_phone = models.CharField(max_length=20, verbose_name=_("Contact Phone"))
    special_instructions = models.TextField(blank=True, verbose_name=_("Special Instructions"))
    
    # Staff assignment
    assigned_driver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_deliveries',
        verbose_name=_("Assigned Driver")
    )
    driver_notes = models.TextField(blank=True, verbose_name=_("Driver Notes"))
    
    # Vehicle information
    vehicle_number = models.CharField(max_length=20, blank=True, verbose_name=_("Vehicle Number"))
    vehicle_type = models.CharField(max_length=50, blank=True, verbose_name=_("Vehicle Type"))
    
    class Meta:
        verbose_name = _("Delivery Schedule")
        verbose_name_plural = _("Delivery Schedules")
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['order', 'delivery_type']),
            models.Index(fields=['scheduled_date', 'status']),
            models.Index(fields=['assigned_driver']),
        ]
    
    def __str__(self):
        return f"{self.delivery_type} for {self.order.order_number} on {self.scheduled_date}"
    
    def is_overdue(self):
        """Check if delivery is overdue."""
        return (
            self.status == 'SCHEDULED' and 
            timezone.now() > self.scheduled_date
        )
    
    def start_delivery(self):
        """Start the delivery process."""
        self.status = 'IN_PROGRESS'
        self.actual_start_time = timezone.now()
        self.save(update_fields=['status', 'actual_start_time'])
    
    def complete_delivery(self):
        """Complete the delivery process."""
        self.status = 'COMPLETED'
        self.actual_end_time = timezone.now()
        self.save(update_fields=['status', 'actual_end_time'])
    
    def get_actual_duration(self):
        """Get actual duration of delivery in minutes."""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return int(duration.total_seconds() / 60)
        return None
