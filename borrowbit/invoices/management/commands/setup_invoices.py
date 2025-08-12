"""
Django management command to set up the invoice system.

This command creates default invoice templates and sample data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import logging

from invoices.models import InvoiceTemplate, Invoice, InvoiceItem
from invoices.services import InvoiceService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up the invoice system with default templates and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample invoices for testing',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of default template',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Invoice Management System...')
        )

        # Create default template
        self.create_default_template(force=options['force'])

        # Create sample data if requested
        if options['create_sample_data']:
            self.create_sample_data()

        self.stdout.write(
            self.style.SUCCESS('✅ Invoice system setup completed successfully!')
        )

    def create_default_template(self, force=False):
        """Create default invoice template."""
        self.stdout.write('📝 Creating default invoice template...')

        if InvoiceTemplate.objects.filter(is_default=True).exists() and not force:
            self.stdout.write(
                self.style.WARNING('⚠️  Default template already exists. Use --force to recreate.')
            )
            return

        # Remove existing default template if force is True
        if force:
            InvoiceTemplate.objects.filter(is_default=True).delete()

        # Create default template
        template = InvoiceTemplate.objects.create(
            name="BorrowBit Default Template",
            description="Default invoice template for BorrowBit rental platform",
            is_default=True,
            is_active=True,
            company_name="BorrowBit Pvt. Ltd.",
            company_address="123 Rental Street, Mumbai, Maharashtra, India - 400001",
            company_phone="+91 9876543210",
            company_email="support@borrowbit.com",
            company_website="www.borrowbit.com",
            html_template="",  # Will use default from PDF generator
            css_styles="",
            invoice_prefix="INV",
            show_tax=True,
            show_discount=True,
            show_terms=True,
            show_payment_info=True,
        )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Default template created: {template.name}')
        )

    def create_sample_data(self):
        """Create sample invoices for testing."""
        self.stdout.write('📊 Creating sample invoice data...')

        # Create test user
        user, created = User.objects.get_or_create(
            email='demo@borrowbit.com',
            defaults={
                'username': 'demo_user',
                'first_name': 'Demo',
                'last_name': 'Customer',
            }
        )

        if created:
            self.stdout.write(f'👤 Created demo user: {user.email}')
        else:
            self.stdout.write(f'👤 Using existing demo user: {user.email}')

        # Create sample invoices
        sample_invoices = [
            {
                'invoice_type': 'RENTAL',
                'subtotal': Decimal('3000.00'),
                'tax_amount': Decimal('300.00'),
                'discount_amount': Decimal('150.00'),
                'total_amount': Decimal('3150.00'),
                'notes': 'Professional camera equipment rental for wedding photography',
                'items': [
                    {
                        'description': 'Canon EOS R5 Camera Body',
                        'quantity': 1,
                        'unit_price': Decimal('2000.00'),
                        'duration': '3 days',
                        'rate_type': 'Daily',
                        'notes': 'Full-frame mirrorless camera with 45MP sensor',
                    },
                    {
                        'description': 'Canon RF 24-70mm f/2.8 Lens',
                        'quantity': 1,
                        'unit_price': Decimal('800.00'),
                        'duration': '3 days',
                        'rate_type': 'Daily',
                        'notes': 'Professional zoom lens for wedding photography',
                    },
                    {
                        'description': 'Professional Lighting Kit',
                        'quantity': 1,
                        'unit_price': Decimal('200.00'),
                        'duration': '3 days',
                        'rate_type': 'Daily',
                        'notes': 'LED lighting setup with stands and diffusers',
                    },
                ]
            },
            {
                'invoice_type': 'DEPOSIT',
                'subtotal': Decimal('5000.00'),
                'tax_amount': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'total_amount': Decimal('5000.00'),
                'notes': 'Security deposit for high-value equipment rental',
                'items': [
                    {
                        'description': 'Security Deposit',
                        'quantity': 1,
                        'unit_price': Decimal('5000.00'),
                        'duration': 'Refundable',
                        'rate_type': 'Fixed',
                        'notes': 'Refundable security deposit for equipment protection',
                    },
                ]
            },
            {
                'invoice_type': 'LATE_FEE',
                'subtotal': Decimal('500.00'),
                'tax_amount': Decimal('50.00'),
                'discount_amount': Decimal('0.00'),
                'total_amount': Decimal('550.00'),
                'notes': 'Late return fee for equipment returned after due date',
                'items': [
                    {
                        'description': 'Late Return Fee',
                        'quantity': 1,
                        'unit_price': Decimal('500.00'),
                        'duration': '2 days late',
                        'rate_type': 'Fixed',
                        'notes': 'Additional charges for late equipment return',
                    },
                ]
            },
        ]

        created_invoices = []
        for i, invoice_data in enumerate(sample_invoices, 1):
            # Create invoice
            invoice = Invoice.objects.create(
                customer=user,
                invoice_type=invoice_data['invoice_type'],
                invoice_date=timezone.now().date() - timezone.timedelta(days=i*7),
                due_date=timezone.now().date() - timezone.timedelta(days=i*7) + timezone.timedelta(days=30),
                subtotal=invoice_data['subtotal'],
                tax_amount=invoice_data['tax_amount'],
                discount_amount=invoice_data['discount_amount'],
                total_amount=invoice_data['total_amount'],
                currency='INR',
                notes=invoice_data['notes'],
                terms_and_conditions='Standard rental terms and conditions apply.',
            )

            # Create invoice items
            for item_data in invoice_data['items']:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    duration=item_data['duration'],
                    rate_type=item_data['rate_type'],
                    notes=item_data['notes'],
                )

            created_invoices.append(invoice)
            self.stdout.write(
                f'📄 Created invoice {i}: {invoice.invoice_number} - {invoice.get_invoice_type_display()}'
            )

        # Generate PDFs for sample invoices
        self.stdout.write('🔄 Generating PDFs for sample invoices...')
        for invoice in created_invoices:
            try:
                InvoiceService.generate_pdf_for_invoice(invoice)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ PDF generated for {invoice.invoice_number}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to generate PDF for {invoice.invoice_number}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {len(created_invoices)} sample invoices')
        )

        # Display summary
        self.stdout.write('\n📋 Sample Data Summary:')
        self.stdout.write(f'   👤 Demo User: {user.email}')
        self.stdout.write(f'   📄 Total Invoices: {len(created_invoices)}')
        self.stdout.write(f'   💰 Total Amount: INR {sum(inv.total_amount for inv in created_invoices)}')
        self.stdout.write(f'   📊 Invoice Types: {", ".join(set(inv.get_invoice_type_display() for inv in created_invoices))}')

        self.stdout.write('\n🔗 You can now:')
        self.stdout.write('   • View invoices in Django admin: /admin/invoices/')
        self.stdout.write('   • Test PDF generation: /invoices/demo/pdf/')
        self.stdout.write('   • Run the test script: python invoices/test_invoice_pdf.py')
