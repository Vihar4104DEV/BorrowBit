#!/usr/bin/env python
"""
Test script for invoice PDF generation.

This script demonstrates how to create invoices and generate PDFs.
Run this script to test the invoice functionality.
"""
import os
import sys
import django
from decimal import Decimal
from django.utils import timezone

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borrowbit.settings')
django.setup()

from django.contrib.auth import get_user_model
from invoices.models import Invoice, InvoiceItem, InvoiceTemplate
from invoices.services import InvoiceService

User = get_user_model()


def create_test_user():
    """Create a test user for demonstration."""
    user, created = User.objects.get_or_create(
        email='test@borrowbit.com',
        defaults={
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    if created:
        print(f"Created test user: {user.email}")
    else:
        print(f"Using existing test user: {user.email}")
    return user


def create_test_invoice(user):
    """Create a test invoice with sample data."""
    # Create invoice
    invoice = Invoice.objects.create(
        customer=user,
        invoice_type='RENTAL',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timezone.timedelta(days=30),
        subtotal=Decimal('2500.00'),
        tax_amount=Decimal('250.00'),
        discount_amount=Decimal('100.00'),
        total_amount=Decimal('2650.00'),
        currency='INR',
        notes='This is a test invoice for demonstration purposes.',
        terms_and_conditions='Test terms and conditions for demonstration.',
    )
    
    # Create invoice items
    InvoiceItem.objects.create(
        invoice=invoice,
        description='Professional Camera Equipment Rental',
        quantity=1,
        unit_price=Decimal('1500.00'),
        duration='5 days',
        rate_type='Daily',
        notes='High-end camera with lenses',
    )
    
    InvoiceItem.objects.create(
        invoice=invoice,
        description='Lighting Equipment Rental',
        quantity=2,
        unit_price=Decimal('400.00'),
        duration='5 days',
        rate_type='Daily',
        notes='Professional lighting setup',
    )
    
    InvoiceItem.objects.create(
        invoice=invoice,
        description='Tripod and Stands',
        quantity=3,
        unit_price=Decimal('100.00'),
        duration='5 days',
        rate_type='Daily',
        notes='Sturdy tripods and camera stands',
    )
    
    print(f"Created test invoice: {invoice.invoice_number}")
    return invoice


def create_default_template():
    """Create a default invoice template if none exists."""
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
        print("Created default invoice template")
        return template
    else:
        template = InvoiceTemplate.objects.filter(is_default=True).first()
        print("Using existing default invoice template")
        return template


def test_pdf_generation(invoice):
    """Test PDF generation for the invoice."""
    try:
        print(f"Generating PDF for invoice {invoice.invoice_number}...")
        
        # Generate PDF
        pdf_file = InvoiceService.generate_pdf_for_invoice(invoice)
        
        if pdf_file:
            print(f"✅ PDF generated successfully!")
            print(f"📄 PDF file: {pdf_file.name}")
            print(f"📁 File size: {pdf_file.size} bytes")
            print(f"🕒 Generated at: {invoice.pdf_generated_at}")
            
            # Get file path
            file_path = pdf_file.path if hasattr(pdf_file, 'path') else 'File stored in media'
            print(f"📍 File location: {file_path}")
            
            return True
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return False


def test_pdf_bytes_generation(invoice):
    """Test PDF bytes generation for the invoice."""
    try:
        print(f"Generating PDF bytes for invoice {invoice.invoice_number}...")
        
        # Generate PDF bytes
        pdf_bytes = InvoiceService.get_invoice_pdf_bytes(invoice)
        
        if pdf_bytes:
            print(f"✅ PDF bytes generated successfully!")
            print(f"📄 PDF size: {len(pdf_bytes)} bytes")
            
            # Save to a test file
            test_file_path = f"test_invoice_{invoice.invoice_number}.pdf"
            with open(test_file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"💾 Test PDF saved to: {test_file_path}")
            return True
        else:
            print("❌ PDF bytes generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error generating PDF bytes: {str(e)}")
        return False


def main():
    """Main function to run the test."""
    print("🚀 Starting Invoice PDF Generation Test")
    print("=" * 50)
    
    try:
        # Create test user
        user = create_test_user()
        print()
        
        # Create default template
        template = create_default_template()
        print()
        
        # Create test invoice
        invoice = create_test_invoice(user)
        print()
        
        # Test PDF generation
        print("Testing PDF Generation:")
        print("-" * 30)
        success1 = test_pdf_generation(invoice)
        print()
        
        # Test PDF bytes generation
        print("Testing PDF Bytes Generation:")
        print("-" * 30)
        success2 = test_pdf_bytes_generation(invoice)
        print()
        
        # Summary
        print("Test Summary:")
        print("=" * 50)
        print(f"✅ PDF Generation: {'PASSED' if success1 else 'FAILED'}")
        print(f"✅ PDF Bytes Generation: {'PASSED' if success2 else 'FAILED'}")
        
        if success1 and success2:
            print("\n🎉 All tests passed! Invoice PDF generation is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the error messages above.")
        
        # Display invoice details
        print(f"\n📋 Invoice Details:")
        print(f"   Invoice Number: {invoice.invoice_number}")
        print(f"   Customer: {invoice.customer.get_full_name()}")
        print(f"   Total Amount: {invoice.currency} {invoice.total_amount}")
        print(f"   Status: {invoice.get_status_display()}")
        print(f"   Items: {invoice.items.count()}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
