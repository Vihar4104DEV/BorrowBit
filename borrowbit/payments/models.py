# """
# Enhanced Payment models for the rental backend application.

# This module contains models for payment processing, invoices, and financial transactions
# specifically designed for rental management with deposits, late fees, and flexible pricing.
# """

# from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.utils import timezone
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
# from decimal import Decimal
# import uuid
# from core.models import BaseModel
# from products.models import Product
# from rentals.models import RentalOrder, RentalQuotation
# from user.models import User


# class PaymentGateway(BaseModel):
#     """Payment gateway configuration and settings."""
    
#     GATEWAY_TYPE_CHOICES = [
#         ('STRIPE', 'Stripe'),
#         ('RAZORPAY', 'Razorpay'),
#         ('PAYPAL', 'PayPal'),
#         ('PAYU', 'PayU'),
#         ('CASHFREE', 'Cashfree'),
#         ('CUSTOM', 'Custom Gateway'),
#     ]
    
#     name = models.CharField(max_length=100, unique=True, verbose_name=_("Gateway Name"))
#     gateway_type = models.CharField(
#         max_length=20, 
#         choices=GATEWAY_TYPE_CHOICES, 
#         verbose_name=_("Gateway Type")
#     )
#     is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
#     is_test_mode = models.BooleanField(default=True, verbose_name=_("Is Test Mode"))
    
#     # Configuration
#     api_key = models.CharField(max_length=255, verbose_name=_("API Key"))
#     secret_key = models.CharField(max_length=255, verbose_name=_("Secret Key"))
#     webhook_secret = models.CharField(max_length=255, blank=True, verbose_name=_("Webhook Secret"))
    
#     # Settings
#     supported_currencies = models.JSONField(
#         default=lambda: ['INR', 'USD'], 
#         verbose_name=_("Supported Currencies")
#     )
#     processing_fee_percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         default=Decimal('2.50'),
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         verbose_name=_("Processing Fee Percentage")
#     )
#     processing_fee_fixed = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Fixed Processing Fee")
#     )
    
#     # Endpoints
#     api_endpoint = models.URLField(verbose_name=_("API Endpoint"))
#     webhook_endpoint = models.URLField(blank=True, verbose_name=_("Webhook Endpoint"))
    
#     # Additional configuration
#     configuration = models.JSONField(default=dict, blank=True, verbose_name=_("Additional Configuration"))
    
#     class Meta:
#         verbose_name = _("Payment Gateway")
#         verbose_name_plural = _("Payment Gateways")
#         ordering = ['name']
    
#     def __str__(self):
#         return f"{self.name} ({'Test' if self.is_test_mode else 'Live'})"
    
#     def get_processing_fee(self, amount):
#         """Calculate processing fee for a given amount."""
#         percentage_fee = amount * (self.processing_fee_percentage / 100)
#         return percentage_fee + self.processing_fee_fixed
    
#     def is_currency_supported(self, currency):
#         """Check if a currency is supported."""
#         return currency in self.supported_currencies


# class Invoice(BaseModel):
#     """Invoice model for rental orders and quotations."""
    
#     INVOICE_TYPE_CHOICES = [
#         ('RENTAL', 'Rental Invoice'),
#         ('DEPOSIT', 'Security Deposit'),
#         ('LATE_FEE', 'Late Return Fee'),
#         ('DAMAGE', 'Damage Fee'),
#         ('SETUP', 'Setup Fee'),
#         ('DELIVERY', 'Delivery Fee'),
#         ('PICKUP', 'Pickup Fee'),
#         ('CLEANING', 'Cleaning Fee'),
#         ('REFUND', 'Refund Invoice'),
#         ('ADJUSTMENT', 'Adjustment'),
#         ('OTHER', 'Other Charges'),
#     ]
    
#     STATUS_CHOICES = [
#         ('DRAFT', 'Draft'),
#         ('SENT', 'Sent'),
#         ('PAID', 'Paid'),
#         ('OVERDUE', 'Overdue'),
#         ('CANCELLED', 'Cancelled'),
#         ('PARTIALLY_PAID', 'Partially Paid'),
#         ('REFUNDED', 'Refunded'),
#         ('VOID', 'Void'),
#     ]
    
#     PAYMENT_TYPE_CHOICES = [
#         ('FULL', 'Full Payment'),
#         ('DEPOSIT', 'Deposit/Partial Payment'),
#         ('REMAINING', 'Remaining Payment'),
#         ('LATE_FEE', 'Late Fee'),
#     ]
    
#     # Basic information
#     invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_("Invoice Number"))
#     invoice_type = models.CharField(
#         max_length=20, 
#         choices=INVOICE_TYPE_CHOICES, 
#         verbose_name=_("Invoice Type")
#     )
#     payment_type = models.CharField(
#         max_length=20,
#         choices=PAYMENT_TYPE_CHOICES,
#         default='FULL',
#         verbose_name=_("Payment Type")
#     )
#     status = models.CharField(
#         max_length=20, 
#         choices=STATUS_CHOICES, 
#         default='DRAFT',
#         verbose_name=_("Status")
#     )
    
#     # Related objects
#     rental_order = models.ForeignKey(
#         RentalOrder, 
#         on_delete=models.CASCADE, 
#         null=True, 
#         blank=True,
#         related_name='invoices',
#         verbose_name=_("Rental Order")
#     )
#     rental_quotation = models.ForeignKey(
#         RentalQuotation, 
#         on_delete=models.CASCADE, 
#         null=True, 
#         blank=True,
#         related_name='invoices',
#         verbose_name=_("Rental Quotation")
#     )
#     parent_invoice = models.ForeignKey(
#         'self',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='child_invoices',
#         verbose_name=_("Parent Invoice")
#     )
    
#     # Customer information
#     customer = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='invoices',
#         verbose_name=_("Customer")
#     )
#     billing_address = models.TextField(verbose_name=_("Billing Address"))
    
#     # Invoice details
#     issue_date = models.DateField(default=timezone.now, verbose_name=_("Issue Date"))
#     due_date = models.DateField(verbose_name=_("Due Date"))
#     paid_date = models.DateField(null=True, blank=True, verbose_name=_("Paid Date"))
    
#     # Financial amounts
#     subtotal = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Subtotal")
#     )
#     tax_amount = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Tax Amount")
#     )
#     discount_amount = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Discount Amount")
#     )
#     total_amount = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Total Amount")
#     )
#     amount_paid = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Amount Paid")
#     )
#     balance_due = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Balance Due")
#     )
    
#     # Rental specific amounts
#     deposit_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal('0.00'),
#         verbose_name=_("Deposit Amount")
#     )
#     rental_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal('0.00'),
#         verbose_name=_("Rental Amount")
#     )
    
#     # Terms and notes
#     terms_and_conditions = models.TextField(blank=True, verbose_name=_("Terms and Conditions"))
#     notes = models.TextField(blank=True, verbose_name=_("Notes"))
#     internal_notes = models.TextField(blank=True, verbose_name=_("Internal Notes"))
    
#     # Payment information
#     payment_terms = models.CharField(max_length=100, default='Net 30', verbose_name=_("Payment Terms"))
#     late_fee_percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         default=Decimal('1.50'),
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         verbose_name=_("Late Fee Percentage")
#     )
#     late_fee_grace_days = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Late Fee Grace Days")
#     )
    
#     # Currency
#     currency = models.CharField(max_length=3, default='INR', verbose_name=_("Currency"))
    
#     # Timestamps
#     sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent At"))
#     reminder_sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reminder Sent At"))
    
#     class Meta:
#         verbose_name = _("Invoice")
#         verbose_name_plural = _("Invoices")
#         ordering = ['-issue_date', '-created_at']
#         indexes = [
#             models.Index(fields=['customer', 'status']),
#             models.Index(fields=['invoice_number']),
#             models.Index(fields=['due_date', 'status']),
#             models.Index(fields=['rental_order', 'invoice_type']),
#             models.Index(fields=['status', 'issue_date']),
#         ]
    
#     def __str__(self):
#         return f"Invoice {self.invoice_number} - {self.customer.get_full_name() if hasattr(self.customer, 'get_full_name') else self.customer}"
    
#     def save(self, *args, **kwargs):
#         if not self.invoice_number:
#             self.invoice_number = self.generate_invoice_number()
#         super().save(*args, **kwargs)
    
#     def generate_invoice_number(self):
#         """Generate unique invoice number."""
#         today = timezone.now().date()
#         prefix = f"INV-{today.strftime('%Y%m%d')}"
        
#         # Get the last invoice for today
#         last_invoice = Invoice.objects.filter(
#             invoice_number__startswith=prefix
#         ).order_by('-invoice_number').first()
        
#         if last_invoice:
#             # Extract sequence number and increment
#             try:
#                 sequence = int(last_invoice.invoice_number.split('-')[-1]) + 1
#             except (ValueError, IndexError):
#                 sequence = 1
#         else:
#             sequence = 1
        
#         return f"{prefix}-{sequence:04d}"
    
#     def calculate_totals(self):
#         """Calculate invoice totals."""
#         self.subtotal = sum(item.total_price for item in self.items.all())
        
#         # Apply discount
#         if self.discount_amount > 0:
#             discounted_subtotal = self.subtotal - self.discount_amount
#         else:
#             discounted_subtotal = self.subtotal
        
#         # Calculate total
#         self.total_amount = discounted_subtotal + self.tax_amount
#         self.balance_due = self.total_amount - self.amount_paid
        
#         # Update rental and deposit amounts based on invoice type
#         if self.invoice_type == 'DEPOSIT':
#             self.deposit_amount = self.total_amount
#         elif self.invoice_type == 'RENTAL':
#             self.rental_amount = self.total_amount
        
#         self.save(update_fields=[
#             'subtotal', 'total_amount', 'balance_due', 
#             'deposit_amount', 'rental_amount'
#         ])
    
#     def is_overdue(self):
#         """Check if invoice is overdue."""
#         if self.status not in ['SENT', 'PARTIALLY_PAID']:
#             return False
        
#         today = timezone.now().date()
#         grace_end_date = self.due_date + timezone.timedelta(days=self.late_fee_grace_days)
#         return today > grace_end_date
    
#     def calculate_late_fees(self):
#         """Calculate late fees for overdue invoice."""
#         if not self.is_overdue():
#             return Decimal('0.00')
        
#         today = timezone.now().date()
#         grace_end_date = self.due_date + timezone.timedelta(days=self.late_fee_grace_days)
#         overdue_days = (today - grace_end_date).days
        
#         if overdue_days > 0:
#             # Calculate late fee based on balance due
#             daily_rate = self.late_fee_percentage / 100 / 30  # Monthly rate converted to daily
#             late_fee = self.balance_due * daily_rate * overdue_days
#             return late_fee
        
#         return Decimal('0.00')
    
#     def apply_late_fees(self):
#         """Apply late fees to the invoice."""
#         late_fee = self.calculate_late_fees()
#         if late_fee > 0:
#             # Create late fee item
#             InvoiceItem.objects.create(
#                 invoice=self,
#                 description=f"Late Fee - {(timezone.now().date() - self.due_date).days} days overdue",
#                 quantity=1,
#                 unit_price=late_fee,
#                 total_price=late_fee
#             )
            
#             # Recalculate totals
#             self.calculate_totals()
            
#             # Update status to overdue
#             self.status = 'OVERDUE'
#             self.save(update_fields=['status'])
    
#     def mark_as_paid(self, amount=None, payment_date=None):
#         """Mark invoice as paid."""
#         if amount is None:
#             amount = self.balance_due
        
#         if payment_date is None:
#             payment_date = timezone.now().date()
        
#         self.amount_paid += amount
#         self.balance_due = self.total_amount - self.amount_paid
        
#         if self.balance_due <= 0:
#             self.status = 'PAID'
#             self.paid_date = payment_date
#         elif self.amount_paid > 0:
#             self.status = 'PARTIALLY_PAID'
        
#         self.save(update_fields=['amount_paid', 'balance_due', 'status', 'paid_date'])
    
#     def send_invoice(self):
#         """Mark invoice as sent."""
#         if self.status == 'DRAFT':
#             self.status = 'SENT'
#             self.sent_at = timezone.now()
#             self.save(update_fields=['status', 'sent_at'])
    
#     def void_invoice(self, reason=''):
#         """Void the invoice."""
#         self.status = 'VOID'
#         self.internal_notes += f"\nVoided on {timezone.now()}: {reason}"
#         self.save(update_fields=['status', 'internal_notes'])
    
#     def create_remaining_payment_invoice(self):
#         """Create invoice for remaining payment after deposit."""
#         if self.payment_type != 'DEPOSIT' or self.status != 'PAID':
#             return None
        
#         remaining_amount = self.rental_amount - self.deposit_amount
#         if remaining_amount <= 0:
#             return None
        
#         remaining_invoice = Invoice.objects.create(
#             invoice_type='RENTAL',
#             payment_type='REMAINING',
#             parent_invoice=self,
#             rental_order=self.rental_order,
#             rental_quotation=self.rental_quotation,
#             customer=self.customer,
#             billing_address=self.billing_address,
#             issue_date=timezone.now().date(),
#             due_date=self.rental_order.pickup_date if self.rental_order else timezone.now().date(),
#             total_amount=remaining_amount,
#             balance_due=remaining_amount,
#             rental_amount=remaining_amount,
#             currency=self.currency,
#             terms_and_conditions=self.terms_and_conditions,
#             payment_terms=self.payment_terms,
#             late_fee_percentage=self.late_fee_percentage,
#             late_fee_grace_days=self.late_fee_grace_days
#         )
        
#         # Create invoice item
#         InvoiceItem.objects.create(
#             invoice=remaining_invoice,
#             description=f"Remaining rental payment for Order #{self.rental_order.id if self.rental_order else 'N/A'}",
#             quantity=1,
#             unit_price=remaining_amount,
#             total_price=remaining_amount
#         )
        
#         return remaining_invoice


# class InvoiceItem(BaseModel):
#     """Individual items in an invoice."""
    
#     invoice = models.ForeignKey(
#         Invoice, 
#         on_delete=models.CASCADE, 
#         related_name='items',
#         verbose_name=_("Invoice")
#     )
#     description = models.CharField(max_length=200, verbose_name=_("Description"))
#     quantity = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('1.00'),
#         validators=[MinValueValidator(Decimal('0.01'))],
#         verbose_name=_("Quantity")
#     )
#     unit_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         verbose_name=_("Unit Price")
#     )
#     total_price = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         verbose_name=_("Total Price")
#     )
    
#     # Tax and discount
#     tax_rate = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         verbose_name=_("Tax Rate (%)")
#     )
#     tax_amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Tax Amount")
#     )
#     discount_percentage = models.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         verbose_name=_("Discount Percentage (%)")
#     )
#     discount_amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Discount Amount")
#     )
    
#     # Product reference (optional)
#     product_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Product ID"))
    
#     # Rental specific fields
#     rental_start_date = models.DateField(null=True, blank=True, verbose_name=_("Rental Start Date"))
#     rental_end_date = models.DateField(null=True, blank=True, verbose_name=_("Rental End Date"))
#     rental_duration_days = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Rental Duration (Days)"))
    
#     # Additional information
#     notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
#     class Meta:
#         verbose_name = _("Invoice Item")
#         verbose_name_plural = _("Invoice Items")
#         ordering = ['invoice', 'id']
    
#     def __str__(self):
#         return f"{self.description} in {self.invoice.invoice_number}"
    
#     def save(self, *args, **kwargs):
#         self.calculate_total_price()
#         super().save(*args, **kwargs)
        
#         # Recalculate invoice totals
#         self.invoice.calculate_totals()
    
#     def calculate_total_price(self):
#         """Calculate total price for this item."""
#         # Calculate base total
#         base_total = self.quantity * self.unit_price
        
#         # Apply discount
#         if self.discount_percentage > 0:
#             self.discount_amount = base_total * (self.discount_percentage / 100)
#         elif self.discount_amount > base_total:
#             self.discount_amount = base_total
        
#         discounted_total = base_total - self.discount_amount
        
#         # Apply tax
#         if self.tax_rate > 0:
#             self.tax_amount = discounted_total * (self.tax_rate / 100)
        
#         self.total_price = discounted_total + self.tax_amount
#         return self.total_price


# class PaymentTransaction(BaseModel):
#     """Payment transaction model for tracking all payment activities."""
    
#     PAYMENT_METHOD_CHOICES = [
#         ('CASH', 'Cash'),
#         ('CARD', 'Credit/Debit Card'),
#         ('BANK_TRANSFER', 'Bank Transfer'),
#         ('UPI', 'UPI'),
#         ('CHEQUE', 'Cheque'),
#         ('ONLINE', 'Online Payment'),
#         ('WALLET', 'Digital Wallet'),
#         ('NETBANKING', 'Net Banking'),
#         ('EMI', 'EMI'),
#         ('CRYPTO', 'Cryptocurrency'),
#     ]
    
#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('PROCESSING', 'Processing'),
#         ('COMPLETED', 'Completed'),
#         ('FAILED', 'Failed'),
#         ('CANCELLED', 'Cancelled'),
#         ('REFUNDED', 'Refunded'),
#         ('PARTIALLY_REFUNDED', 'Partially Refunded'),
#         ('DISPUTED', 'Disputed'),
#         ('CHARGEBACK', 'Chargeback'),
#     ]
    
#     TRANSACTION_TYPE_CHOICES = [
#         ('PAYMENT', 'Payment'),
#         ('REFUND', 'Refund'),
#         ('CHARGEBACK', 'Chargeback'),
#         ('ADJUSTMENT', 'Adjustment'),
#         ('DEPOSIT', 'Deposit'),
#         ('LATE_FEE', 'Late Fee'),
#         ('DAMAGE_FEE', 'Damage Fee'),
#     ]
    
#     # Basic information
#     transaction_id = models.CharField(max_length=100, unique=True, verbose_name=_("Transaction ID"))
#     transaction_type = models.CharField(
#         max_length=20, 
#         choices=TRANSACTION_TYPE_CHOICES, 
#         default='PAYMENT',
#         verbose_name=_("Transaction Type")
#     )
#     status = models.CharField(
#         max_length=20, 
#         choices=STATUS_CHOICES, 
#         default='PENDING',
#         verbose_name=_("Status")
#     )
    
#     # Related objects
#     invoice = models.ForeignKey(
#         Invoice, 
#         on_delete=models.CASCADE, 
#         null=True, 
#         blank=True,
#         related_name='payment_transactions',
#         verbose_name=_("Invoice")
#     )
#     rental_order = models.ForeignKey(
#         RentalOrder, 
#         on_delete=models.CASCADE, 
#         null=True, 
#         blank=True,
#         related_name='payment_transactions',
#         verbose_name=_("Rental Order")
#     )
#     payment_gateway = models.ForeignKey(
#         PaymentGateway,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Payment Gateway")
#     )
    
#     # Customer information
#     customer = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='payment_transactions',
#         verbose_name=_("Customer")
#     )
    
#     # Payment details
#     amount = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         validators=[MinValueValidator(Decimal('0.01'))],
#         verbose_name=_("Amount")
#     )
#     currency = models.CharField(max_length=3, default='INR', verbose_name=_("Currency"))
#     payment_method = models.CharField(
#         max_length=20, 
#         choices=PAYMENT_METHOD_CHOICES, 
#         verbose_name=_("Payment Method")
#     )
    
#     # Payment gateway information
#     gateway_transaction_id = models.CharField(
#         max_length=100, 
#         blank=True, 
#         verbose_name=_("Gateway Transaction ID")
#     )
#     gateway_response = models.JSONField(
#         default=dict, 
#         blank=True, 
#         verbose_name=_("Gateway Response")
#     )
    
#     # Additional charges
#     processing_fee = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Processing Fee")
#     )
#     tax_amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         verbose_name=_("Tax Amount")
#     )
#     net_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=Decimal('0.00'),
#         verbose_name=_("Net Amount")
#     )
    
#     # Timestamps
#     initiated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Initiated At"))
#     processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))
#     failed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Failed At"))
#     refunded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Refunded At"))
    
#     # Error information
#     error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
#     error_code = models.CharField(max_length=50, blank=True, verbose_name=_("Error Code"))
    
#     # Reference information
#     reference_number = models.CharField(max_length=100, blank=True, verbose_name=_("Reference Number"))
#     bank_reference = models.CharField(max_length=100, blank=True, verbose_name=_("Bank Reference"))
    
#     # Notes
#     notes = models.TextField(blank=True, verbose_name=_("Notes"))
#     internal_notes = models.TextField(blank=True, verbose_name=_("Internal Notes"))
    
#     class Meta:
#         verbose_name = _("Payment Transaction")
#         verbose_name_plural = _("Payment Transactions")
#         ordering = ['-initiated_at']
#         indexes = [
#             models.Index(fields=['customer', 'status']),
#             models.Index(fields=['transaction_id']),
#             models.Index(fields=['gateway_transaction_id']),
#             models.Index(fields=['status', 'initiated_at']),
#             models.Index(fields=['invoice', 'status']),
#             models.Index(fields=['rental_order', 'transaction_type']),
#         ]
    
#     def __str__(self):
#         return f"Transaction {self.transaction_id} - ₹{self.amount}"
    
#     def save(self, *args, **kwargs):
#         if not self.transaction_id:
#             self.transaction_id = self.generate_transaction_id()
        
#         # Calculate net amount
#         self.net_amount = self.amount - self.processing_fee - self.tax_amount
        
#         super().save(*args, **kwargs)
    
#     def generate_transaction_id(self):
#         """Generate unique transaction ID."""
#         today = timezone.now().date()
#         prefix = f"TXN-{today.strftime('%Y%m%d')}"
        
#         # Get the last transaction for today
#         last_txn = PaymentTransaction.objects.filter(
#             transaction_id__startswith=prefix
#         ).order_by('-transaction_id').first()
        
#         if last_txn:
#             try:
#                 sequence = int(last_txn.transaction_id.split('-')[-1]) + 1
#             except (ValueError, IndexError):
#                 sequence = 1
#         else:
#             sequence = 1
        
#         return f"{prefix}-{sequence:06d}"
    
#     def calculate_processing_fee(self):
#         """Calculate processing fee based on payment gateway."""
#         if self.payment_gateway and self.payment_method in ['CARD', 'ONLINE', 'UPI', 'NETBANKING']:
#             self.processing_fee = self.payment_gateway.get_processing_fee(self.amount)
#         else:
#             self.processing_fee = Decimal('0.00')
        
#         self.save(update_fields=['processing_fee'])
    
#     def process_payment(self):
#         """Process the payment transaction."""
#         try:
#             # Calculate processing fee
#             self.calculate_processing_fee()
            
#             # Update status
#             self.status = 'PROCESSING'
#             self.save(update_fields=['status'])
            
#             # Process payment based on method
#             if self.payment_method in ['CARD', 'ONLINE', 'UPI', 'NETBANKING'] and self.payment_gateway:
#                 # Gateway payment processing
#                 success = self._process_gateway_payment()
#             else:
#                 # Non-gateway payments (cash, cheque, etc.)
#                 success = self._process_offline_payment()
            
#             if success:
#                 self.status = 'COMPLETED'
#                 self.processed_at = timezone.now()
                
#                 # Update invoice if exists
#                 if self.invoice:
#                     self.invoice.mark_as_paid(self.amount, self.processed_at.date())
                
#                 self.save(update_fields=['status', 'processed_at'])
#                 return True
#             else:
#                 return False
                
#         except Exception as e:
#             self.status = 'FAILED'
#             self.failed_at = timezone.now()
#             self.error_message = str(e)
#             self.save(update_fields=['status', 'failed_at', 'error_message'])
#             return False
    
#     def _process_gateway_payment(self):
#         """Process payment through gateway (implement actual gateway integration)."""
#         # This is a placeholder for actual gateway integration
#         # In real implementation, you would integrate with actual payment gateways
        
#         if self.payment_gateway.is_test_mode:
#             # Simulate payment for test mode
#             import random
#             success_rate = 0.9  #