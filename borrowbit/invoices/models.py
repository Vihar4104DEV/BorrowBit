"""
Invoice models for the rental backend application.

This module contains models for invoice generation, management, and PDF storage.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from core.models import BaseModel
from payments.models import Payment
from rentals.models import RentalOrder
import uuid

User = get_user_model()


class Invoice(BaseModel):
    """Invoice model for generating and managing rental invoices."""
    
    INVOICE_TYPE_CHOICES = [
        ('RENTAL', _('Rental Invoice')),
        ('DEPOSIT', _('Security Deposit Invoice')),
        ('LATE_FEE', _('Late Fee Invoice')),
        ('DAMAGE_FEE', _('Damage Fee Invoice')),
        ('ADJUSTMENT', _('Adjustment Invoice')),
        ('REFUND', _('Refund Invoice')),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('SENT', _('Sent')),
        ('PAID', _('Paid')),
        ('OVERDUE', _('Overdue')),
        ('CANCELLED', _('Cancelled')),
        ('VOID', _('Void')),
    ]
    
    # Basic information
    invoice_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name=_("Invoice Number")
    )
    invoice_type = models.CharField(
        max_length=20, 
        choices=INVOICE_TYPE_CHOICES, 
        verbose_name=_("Invoice Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='DRAFT',
        verbose_name=_("Status")
    )
    
    # Related objects
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='invoices',
        verbose_name=_("Customer")
    )
    rental_order = models.ForeignKey(
        RentalOrder, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='invoices',
        verbose_name=_("Rental Order")
    )
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='invoices',
        verbose_name=_("Payment")
    )
    
    # Dates
    invoice_date = models.DateField(default=timezone.now, verbose_name=_("Invoice Date"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    paid_date = models.DateField(null=True, blank=True, verbose_name=_("Paid Date"))
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Subtotal")
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tax Amount")
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Discount Amount")
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Total Amount")
    )
    amount_paid = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Amount Paid")
    )
    balance_due = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Balance Due")
    )
    
    # Additional information
    currency = models.CharField(max_length=3, default='INR', verbose_name=_("Currency"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    terms_and_conditions = models.TextField(blank=True, verbose_name=_("Terms and Conditions"))
    
    # PDF generation
    pdf_file = models.FileField(
        upload_to='invoices/pdfs/', 
        null=True, 
        blank=True,
        verbose_name=_("PDF File")
    )
    pdf_generated_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("PDF Generated At")
    )
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent At"))
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Viewed At"))
    
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['-invoice_date', '-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['invoice_date', 'due_date']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['rental_order']),
            models.Index(fields=['payment']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.get_invoice_type_display()}"
    
    def save(self, *args, **kwargs):
        """Generate invoice number and calculate totals if not set."""
        if not self.invoice_number:
            self.invoice_number = f"INV{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate totals
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_due = self.total_amount - self.amount_paid
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        return (
            self.status in ['SENT', 'DRAFT'] and 
            self.balance_due > 0 and 
            timezone.now().date() > self.due_date
        )
    
    def is_paid(self):
        """Check if invoice is fully paid."""
        return self.balance_due <= 0
    
    def mark_as_paid(self, amount=None, payment_date=None):
        """Mark invoice as paid."""
        if amount:
            self.amount_paid += amount
        else:
            self.amount_paid = self.total_amount
        
        self.balance_due = self.total_amount - self.amount_paid
        
        if self.is_paid():
            self.status = 'PAID'
            self.paid_date = payment_date or timezone.now().date()
        
        self.save(update_fields=[
            'amount_paid', 'balance_due', 'status', 'paid_date', 'updated_at'
        ])
    
    def mark_as_sent(self):
        """Mark invoice as sent."""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def get_duration_days(self):
        """Get rental duration in days if rental order exists."""
        if self.rental_order:
            return self.rental_order.get_duration_days()
        return 0


class InvoiceItem(BaseModel):
    """Individual items in an invoice."""
    
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_("Invoice")
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        verbose_name=_("Product")
    )
    description = models.CharField(max_length=500, verbose_name=_("Description"))
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity")
    )
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
    
    # Additional details
    duration = models.CharField(max_length=100, blank=True, verbose_name=_("Duration"))
    rate_type = models.CharField(max_length=50, blank=True, verbose_name=_("Rate Type"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Invoice Item")
        verbose_name_plural = _("Invoice Items")
        ordering = ['invoice', 'created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.total_price}"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class InvoiceTemplate(BaseModel):
    """Templates for invoice generation."""
    
    name = models.CharField(max_length=100, verbose_name=_("Template Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    # Template content
    html_template = models.TextField(verbose_name=_("HTML Template"))
    css_styles = models.TextField(blank=True, verbose_name=_("CSS Styles"))
    
    # Company information
    company_name = models.CharField(max_length=200, verbose_name=_("Company Name"))
    company_address = models.TextField(verbose_name=_("Company Address"))
    company_phone = models.CharField(max_length=20, verbose_name=_("Company Phone"))
    company_email = models.EmailField(verbose_name=_("Company Email"))
    company_website = models.URLField(blank=True, verbose_name=_("Company Website"))
    company_logo = models.ImageField(
        upload_to='invoice_templates/logos/', 
        null=True, 
        blank=True,
        verbose_name=_("Company Logo")
    )
    
    # Invoice settings
    invoice_prefix = models.CharField(max_length=10, default='INV', verbose_name=_("Invoice Prefix"))
    show_tax = models.BooleanField(default=True, verbose_name=_("Show Tax"))
    show_discount = models.BooleanField(default=True, verbose_name=_("Show Discount"))
    show_terms = models.BooleanField(default=True, verbose_name=_("Show Terms"))
    show_payment_info = models.BooleanField(default=True, verbose_name=_("Show Payment Info"))
    
    class Meta:
        verbose_name = _("Invoice Template")
        verbose_name_plural = _("Invoice Templates")
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Ensure only one default template."""
        if self.is_default:
            InvoiceTemplate.objects.filter(is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_default_template():
        """Get the default invoice template."""
        return InvoiceTemplate.objects.filter(is_default=True, is_active=True).first()
