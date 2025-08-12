# Invoice Management App

A comprehensive Django app for generating, managing, and downloading professional PDF invoices for the BorrowBit rental platform.

## Features

### 🎯 Core Features
- **PDF Invoice Generation**: Generate professional PDF invoices using WeasyPrint
- **Multiple Invoice Types**: Support for rental, deposit, late fee, damage fee, and refund invoices
- **Template System**: Customizable invoice templates with company branding
- **Invoice Management**: Complete CRUD operations for invoices
- **Payment Integration**: Automatic invoice creation from payments
- **Rental Order Integration**: Generate invoices from rental orders

### 📊 Invoice Types
- **Rental Invoice**: Standard rental equipment invoices
- **Security Deposit Invoice**: Refundable security deposits
- **Late Fee Invoice**: Charges for late returns
- **Damage Fee Invoice**: Charges for equipment damage
- **Adjustment Invoice**: Manual adjustments and corrections
- **Refund Invoice**: Refund documentation

### 🎨 Design Features
- **Professional Layout**: Clean, modern invoice design
- **Company Branding**: Customizable header with logo and company details
- **Responsive Design**: Optimized for both screen and print
- **Color Scheme**: BorrowBit green theme (#00A86B)
- **Typography**: Professional font stack with proper spacing

## Installation

### 1. Add to Django Settings

Add the app to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'invoices',
]
```

### 2. Install Dependencies

```bash
pip install weasyprint==60.2
```

### 3. Run Migrations

```bash
python manage.py makemigrations invoices
python manage.py migrate
```

### 4. Add URL Patterns

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('invoices/', include('invoices.urls')),
]
```

## Usage

### Basic Invoice Creation

```python
from invoices.services import InvoiceService
from invoices.models import Invoice, InvoiceItem
from decimal import Decimal

# Create invoice from rental order
invoice = InvoiceService.create_invoice_from_rental_order(
    rental_order=rental_order,
    invoice_type='RENTAL',
    notes='Thank you for your business!'
)

# Create invoice from payment
invoice = InvoiceService.create_invoice_from_payment(
    payment=payment,
    invoice_type='RENTAL'
)

# Create deposit invoice
invoice = InvoiceService.create_deposit_invoice(
    rental_order=rental_order,
    notes='Security deposit for rental equipment'
)
```

### PDF Generation

```python
from invoices.services import InvoiceService

# Generate PDF and save to file
pdf_file = InvoiceService.generate_pdf_for_invoice(invoice)

# Generate PDF bytes (for immediate download)
pdf_bytes = InvoiceService.get_invoice_pdf_bytes(invoice)
```

### Invoice Management

```python
# Mark invoice as paid
InvoiceService.mark_invoice_as_paid(invoice, amount=1000.00)

# Mark invoice as sent
InvoiceService.send_invoice(invoice)

# Get customer invoices
invoices = InvoiceService.get_customer_invoices(customer)

# Get overdue invoices
overdue = InvoiceService.get_overdue_invoices()
```

## API Endpoints

### Customer Endpoints
- `GET /invoices/` - List user's invoices
- `GET /invoices/<id>/` - View invoice details
- `GET /invoices/<id>/pdf/` - View PDF in browser
- `GET /invoices/<id>/pdf/download/` - Download PDF
- `POST /invoices/<id>/pdf/regenerate/` - Regenerate PDF

### Admin Endpoints
- `GET /invoices/admin/` - List all invoices (staff only)
- `GET /invoices/admin/<id>/` - Admin invoice details
- `GET /invoices/admin/<id>/pdf/` - Admin PDF download
- `POST /invoices/admin/<id>/mark-paid/` - Mark as paid
- `POST /invoices/admin/<id>/send/` - Mark as sent

### Demo Endpoints
- `GET /invoices/demo/pdf/` - Generate demo invoice PDF

## Models

### Invoice
Main invoice model with all invoice details and relationships.

**Key Fields:**
- `invoice_number`: Unique invoice identifier
- `invoice_type`: Type of invoice (RENTAL, DEPOSIT, etc.)
- `status`: Invoice status (DRAFT, SENT, PAID, etc.)
- `customer`: Customer who owns the invoice
- `rental_order`: Associated rental order (optional)
- `payment`: Associated payment (optional)
- `total_amount`: Total invoice amount
- `pdf_file`: Generated PDF file

### InvoiceItem
Individual items within an invoice.

**Key Fields:**
- `invoice`: Parent invoice
- `product`: Associated product (optional)
- `description`: Item description
- `quantity`: Item quantity
- `unit_price`: Price per unit
- `total_price`: Total price for this item

### InvoiceTemplate
Customizable invoice templates.

**Key Fields:**
- `name`: Template name
- `html_template`: HTML template content
- `company_name`: Company name for branding
- `company_logo`: Company logo image
- `show_tax`: Whether to show tax information
- `show_discount`: Whether to show discount information

## PDF Generation

The app uses **WeasyPrint** for PDF generation, which provides:

- **High-quality output**: Professional-looking PDFs
- **CSS support**: Full CSS styling capabilities
- **Font support**: Custom fonts and typography
- **Print optimization**: Optimized for printing
- **Cross-platform**: Works on Windows, macOS, and Linux

### Template System

The default template includes:

- **Header**: Company logo, name, and contact information
- **Invoice Details**: Invoice number, dates, and customer information
- **Items Table**: Product details, quantities, and prices
- **Totals Section**: Subtotal, tax, discount, and grand total
- **Footer**: Terms, conditions, and company information

### Customization

You can customize the invoice appearance by:

1. **Creating a custom template** in the admin interface
2. **Modifying the HTML template** in `pdf_generator.py`
3. **Adding custom CSS styles** for branding
4. **Uploading company logo** in the template settings

## Testing

Run the test script to verify PDF generation:

```bash
cd borrowbit
python invoices/test_invoice_pdf.py
```

This will:
1. Create a test user
2. Create a sample invoice with items
3. Generate PDF files
4. Display test results

## Admin Interface

The Django admin provides comprehensive invoice management:

- **Invoice List**: View all invoices with filters and search
- **Invoice Details**: Edit invoice information and items
- **PDF Generation**: Generate PDFs directly from admin
- **Bulk Actions**: Mark multiple invoices as paid/sent
- **Template Management**: Create and edit invoice templates

## Configuration

### Settings

Add these settings to your `settings.py`:

```python
# Invoice settings
INVOICE_PDF_STORAGE_PATH = 'invoices/pdfs/'
INVOICE_TEMPLATE_STORAGE_PATH = 'invoice_templates/'

# WeasyPrint settings (optional)
WEASYPRINT_OPTIONS = {
    'encoding': 'utf-8',
    'presentational_hints': True,
}
```

### Media Files

Ensure your media files are properly configured:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Security

- **Authentication Required**: All invoice views require login
- **User Isolation**: Users can only access their own invoices
- **Admin Protection**: Admin views require staff permissions
- **File Validation**: PDF files are validated before storage

## Performance

- **Lazy PDF Generation**: PDFs are generated on-demand
- **Caching**: PDF files are cached to avoid regeneration
- **Database Optimization**: Efficient queries with select_related
- **File Storage**: PDFs stored in media directory for fast access

## Troubleshooting

### Common Issues

1. **WeasyPrint Installation**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
   
   # On macOS
   brew install cairo pango gdk-pixbuf libffi
   
   # On Windows
   # Download and install GTK+ runtime
   ```

2. **PDF Generation Fails**
   - Check WeasyPrint installation
   - Verify template syntax
   - Check file permissions for media directory

3. **Template Not Loading**
   - Ensure template is marked as active
   - Check HTML syntax in template
   - Verify company information is set

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This app is part of the BorrowBit project and follows the same license terms.

## Support

For support and questions:
- Email: support@borrowbit.com
- Documentation: Check the main project README
- Issues: Use the project issue tracker
