"""
Invoice services for business logic and invoice management.

This module contains services for creating invoices, generating PDFs, and managing invoice workflows.
"""
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
import logging

from .models import Invoice, InvoiceItem, InvoiceTemplate
from .pdf_generator import generate_invoice_pdf, generate_invoice_pdf_bytes

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service class for invoice management."""
    
    @staticmethod
    def create_invoice_from_rental_order(rental_order, invoice_type='RENTAL', **kwargs):
        """Create an invoice from a rental order."""
        try:
            with transaction.atomic():
                # Calculate due date (30 days from invoice date)
                invoice_date = kwargs.get('invoice_date', timezone.now().date())
                due_date = kwargs.get('due_date', invoice_date + timezone.timedelta(days=30))
                
                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_type=invoice_type,
                    customer=rental_order.customer,
                    rental_order=rental_order,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    subtotal=rental_order.subtotal,
                    tax_amount=rental_order.tax_amount,
                    discount_amount=rental_order.discount_amount,
                    total_amount=rental_order.total_amount,
                    currency=kwargs.get('currency', 'INR'),
                    notes=kwargs.get('notes', ''),
                    terms_and_conditions=kwargs.get('terms_and_conditions', ''),
                )
                
                # Create invoice items from rental order items
                for rental_item in rental_order.rental_items.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=rental_item.product,
                        description=f"{rental_item.product.name} - Rental",
                        quantity=rental_item.quantity,
                        unit_price=rental_item.unit_price,
                        duration=f"{rental_order.get_duration_days()} days",
                        rate_type="Daily",
                        notes=rental_item.notes,
                    )
                
                # Add delivery and setup fees if applicable
                if rental_order.delivery_fee > 0:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=None,  # No specific product for fees
                        description="Delivery Fee",
                        quantity=1,
                        unit_price=rental_order.delivery_fee,
                        rate_type="Fixed",
                    )
                
                if rental_order.setup_fee > 0:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=None,  # No specific product for fees
                        description="Setup Fee",
                        quantity=1,
                        unit_price=rental_order.setup_fee,
                        rate_type="Fixed",
                    )
                
                logger.info(f"Created invoice {invoice.invoice_number} for rental order {rental_order.order_number}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error creating invoice for rental order {rental_order.order_number}: {str(e)}")
            raise
    
    @staticmethod
    def create_invoice_from_payment(payment, invoice_type='RENTAL', **kwargs):
        """Create an invoice from a payment."""
        try:
            with transaction.atomic():
                # Calculate due date
                invoice_date = kwargs.get('invoice_date', timezone.now().date())
                due_date = kwargs.get('due_date', invoice_date + timezone.timedelta(days=30))
                
                # Get rental order from payment metadata or checkout session
                rental_order = None
                if hasattr(payment, 'checkout_session') and payment.checkout_session:
                    # Try to get rental order from checkout session metadata
                    metadata = payment.checkout_session.metadata
                    if 'rental_order_id' in metadata:
                        from rentals.models import RentalOrder
                        try:
                            rental_order = RentalOrder.objects.get(id=metadata['rental_order_id'])
                        except RentalOrder.DoesNotExist:
                            pass
                
                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_type=invoice_type,
                    customer=payment.user,
                    rental_order=rental_order,
                    payment=payment,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    subtotal=payment.amount,
                    tax_amount=kwargs.get('tax_amount', Decimal('0')),
                    discount_amount=kwargs.get('discount_amount', Decimal('0')),
                    total_amount=payment.total_amount,
                    amount_paid=payment.total_amount,
                    currency=payment.currency,
                    notes=kwargs.get('notes', ''),
                    terms_and_conditions=kwargs.get('terms_and_conditions', ''),
                )
                
                # Create invoice item for payment
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=None,  # No specific product for payment invoices
                    description=f"Payment for {payment.get_transaction_type_display()}",
                    quantity=1,
                    unit_price=payment.total_amount,
                    rate_type="Fixed",
                    notes=f"Payment ID: {payment.payment_id}",
                )
                
                # Mark as paid since payment is completed
                invoice.mark_as_paid()
                
                logger.info(f"Created invoice {invoice.invoice_number} for payment {payment.payment_id}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error creating invoice for payment {payment.payment_id}: {str(e)}")
            raise
    
    @staticmethod
    def create_deposit_invoice(rental_order, **kwargs):
        """Create a security deposit invoice."""
        try:
            with transaction.atomic():
                # Calculate due date
                invoice_date = kwargs.get('invoice_date', timezone.now().date())
                due_date = kwargs.get('due_date', invoice_date + timezone.timedelta(days=7))
                
                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_type='DEPOSIT',
                    customer=rental_order.customer,
                    rental_order=rental_order,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    subtotal=rental_order.security_deposit,
                    total_amount=rental_order.security_deposit,
                    currency=kwargs.get('currency', 'INR'),
                    notes=kwargs.get('notes', 'Security deposit for rental equipment'),
                    terms_and_conditions=kwargs.get('terms_and_conditions', ''),
                )
                
                # Create invoice item for security deposit
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=None,
                    description="Security Deposit",
                    quantity=1,
                    unit_price=rental_order.security_deposit,
                    rate_type="Fixed",
                    notes="Refundable security deposit",
                )
                
                logger.info(f"Created deposit invoice {invoice.invoice_number} for rental order {rental_order.order_number}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error creating deposit invoice for rental order {rental_order.order_number}: {str(e)}")
            raise
    
    @staticmethod
    def create_late_fee_invoice(rental_order, late_fee_amount, **kwargs):
        """Create a late fee invoice."""
        try:
            with transaction.atomic():
                # Calculate due date
                invoice_date = kwargs.get('invoice_date', timezone.now().date())
                due_date = kwargs.get('due_date', invoice_date + timezone.timedelta(days=7))
                
                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_type='LATE_FEE',
                    customer=rental_order.customer,
                    rental_order=rental_order,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    subtotal=late_fee_amount,
                    total_amount=late_fee_amount,
                    currency=kwargs.get('currency', 'INR'),
                    notes=kwargs.get('notes', 'Late return fee'),
                    terms_and_conditions=kwargs.get('terms_and_conditions', ''),
                )
                
                # Create invoice item for late fee
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=None,
                    description="Late Return Fee",
                    quantity=1,
                    unit_price=late_fee_amount,
                    rate_type="Fixed",
                    notes="Fee for late return of rental equipment",
                )
                
                logger.info(f"Created late fee invoice {invoice.invoice_number} for rental order {rental_order.order_number}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error creating late fee invoice for rental order {rental_order.order_number}: {str(e)}")
            raise
    
    @staticmethod
    def generate_pdf_for_invoice(invoice, force_regenerate=False):
        """Generate PDF for an invoice."""
        try:
            # Check if PDF already exists and force_regenerate is False
            if invoice.pdf_file and not force_regenerate:
                logger.info(f"PDF already exists for invoice {invoice.invoice_number}")
                return invoice.pdf_file
            
            # Generate PDF
            pdf_file = generate_invoice_pdf(invoice)
            
            logger.info(f"PDF generated successfully for invoice {invoice.invoice_number}")
            return pdf_file
            
        except Exception as e:
            logger.error(f"Error generating PDF for invoice {invoice.invoice_number}: {str(e)}")
            raise
    
    @staticmethod
    def get_invoice_pdf_bytes(invoice):
        """Get PDF bytes for an invoice without saving to file."""
        try:
            pdf_bytes = generate_invoice_pdf_bytes(invoice)
            logger.info(f"PDF bytes generated for invoice {invoice.invoice_number}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF bytes for invoice {invoice.invoice_number}: {str(e)}")
            raise
    
    @staticmethod
    def mark_invoice_as_paid(invoice, amount=None, payment_date=None):
        """Mark an invoice as paid."""
        try:
            invoice.mark_as_paid(amount, payment_date)
            logger.info(f"Invoice {invoice.invoice_number} marked as paid")
            return invoice
            
        except Exception as e:
            logger.error(f"Error marking invoice {invoice.invoice_number} as paid: {str(e)}")
            raise
    
    @staticmethod
    def send_invoice(invoice):
        """Mark an invoice as sent."""
        try:
            invoice.mark_as_sent()
            logger.info(f"Invoice {invoice.invoice_number} marked as sent")
            return invoice
            
        except Exception as e:
            logger.error(f"Error sending invoice {invoice.invoice_number}: {str(e)}")
            raise
    
    @staticmethod
    def get_customer_invoices(customer, status=None, invoice_type=None):
        """Get invoices for a customer with optional filters."""
        queryset = Invoice.objects.filter(customer=customer)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        return queryset.order_by('-invoice_date', '-created_at')
    
    @staticmethod
    def get_overdue_invoices():
        """Get all overdue invoices."""
        return Invoice.objects.filter(
            status__in=['DRAFT', 'SENT'],
            balance_due__gt=0,
            due_date__lt=timezone.now().date()
        ).order_by('due_date')
    
    @staticmethod
    def create_default_template():
        """Create a default invoice template if none exists."""
        try:
            if not InvoiceTemplate.objects.filter(is_default=True).exists():
                template = InvoiceTemplate.objects.create(
                    name="Default Invoice Template",
                    description="Default template for invoice generation",
                    is_default=True,
                    is_active=True,
                    company_name="BorrowBit Pvt. Ltd.",
                    company_address="123 Rental Street, Mumbai, India",
                    company_phone="+91 9876543210",
                    company_email="support@borrowbit.com",
                    company_website="www.borrowbit.com",
                    html_template="",  # Will use default from PDF generator
                    show_tax=True,
                    show_discount=True,
                    show_terms=True,
                    show_payment_info=True,
                )
                logger.info("Default invoice template created")
                return template
            else:
                return InvoiceTemplate.objects.filter(is_default=True).first()
                
        except Exception as e:
            logger.error(f"Error creating default invoice template: {str(e)}")
            raise


class InvoiceItemService:
    """Service class for invoice item management."""
    
    @staticmethod
    def add_item_to_invoice(invoice, product, description, quantity, unit_price, **kwargs):
        """Add an item to an invoice."""
        try:
            item = InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                duration=kwargs.get('duration', ''),
                rate_type=kwargs.get('rate_type', 'Fixed'),
                notes=kwargs.get('notes', ''),
            )
            
            # Recalculate invoice totals
            invoice.calculate_totals()
            
            logger.info(f"Added item to invoice {invoice.invoice_number}")
            return item
            
        except Exception as e:
            logger.error(f"Error adding item to invoice {invoice.invoice_number}: {str(e)}")
            raise
    
    @staticmethod
    def remove_item_from_invoice(invoice_item):
        """Remove an item from an invoice."""
        try:
            invoice = invoice_item.invoice
            invoice_item.delete()
            
            # Recalculate invoice totals
            invoice.calculate_totals()
            
            logger.info(f"Removed item from invoice {invoice.invoice_number}")
            
        except Exception as e:
            logger.error(f"Error removing item from invoice: {str(e)}")
            raise
    
    @staticmethod
    def update_invoice_item(invoice_item, **kwargs):
        """Update an invoice item."""
        try:
            for field, value in kwargs.items():
                if hasattr(invoice_item, field):
                    setattr(invoice_item, field, value)
            
            invoice_item.save()
            
            # Recalculate invoice totals
            invoice_item.invoice.calculate_totals()
            
            logger.info(f"Updated item in invoice {invoice_item.invoice.invoice_number}")
            return invoice_item
            
        except Exception as e:
            logger.error(f"Error updating invoice item: {str(e)}")
            raise
