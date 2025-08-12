"""
PDF Generator for Invoice generation.

This module handles the conversion of HTML invoice templates to PDF format.
"""
import os
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging

logger = logging.getLogger(__name__)


class InvoicePDFGenerator:
    """PDF generator for invoices using WeasyPrint."""
    
    def __init__(self, invoice, template=None):
        self.invoice = invoice
        self.template = template or self._get_default_template()
        self.font_config = FontConfiguration()
    
    def _get_default_template(self):
        """Get the default invoice template."""
        from .models import InvoiceTemplate
        return InvoiceTemplate.get_default_template()
    
    def _prepare_context(self):
        """Prepare context data for template rendering."""
        context = {
            'invoice': self.invoice,
            'customer': self.invoice.customer,
            'invoice_items': self.invoice.items.all(),
            'invoice_date': self.invoice.invoice_date,
            'due_date': self.invoice.due_date,
            'invoice_number': self.invoice.invoice_number,
            'invoice_type': self.invoice.get_invoice_type_display(),
            'subtotal': self.invoice.subtotal,
            'tax_amount': self.invoice.tax_amount,
            'discount_amount': self.invoice.discount_amount,
            'total_amount': self.invoice.total_amount,
            'amount_paid': self.invoice.amount_paid,
            'balance_due': self.invoice.balance_due,
            'currency': self.invoice.currency,
            'notes': self.invoice.notes,
            'terms_and_conditions': self.invoice.terms_and_conditions,
            'company_name': 'BorrowBit Pvt. Ltd.',
            'company_address': '123 Rental Street, Mumbai, India',
            'company_phone': '+91 9876543210',
            'company_email': 'support@borrowbit.com',
            'company_website': 'www.borrowbit.com',
            'generated_at': timezone.now(),
        }
        
        # Add rental order details if available
        if self.invoice.rental_order:
            context.update({
                'rental_order': self.invoice.rental_order,
                'rental_start': self.invoice.rental_order.start_date,
                'rental_end': self.invoice.rental_order.end_date,
                'duration_days': self.invoice.rental_order.get_duration_days(),
                'pickup_location': self.invoice.rental_order.pickup_location,
                'return_location': self.invoice.rental_order.return_location,
            })
        
        # Add payment details if available
        if self.invoice.payment:
            context.update({
                'payment': self.invoice.payment,
                'payment_method': self.invoice.payment.payment_method.name if self.invoice.payment.payment_method else '',
                'payment_date': self.invoice.payment.completed_at,
            })
        
        return context
    
    def _get_template_content(self):
        """Get the HTML template content."""
        if self.template:
            return self.template.html_template
        else:
            # Return default template
            return self._get_default_html_template()
    
    def _get_default_html_template(self):
        """Get the default HTML template."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ invoice_type }} - {{ company_name }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.6;
        }
        
        .invoice-container {
            max-width: 100%;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            background: linear-gradient(90deg, #00A86B, #02c27a);
            color: #fff;
            padding: 30px;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .company-info {
            flex: 1;
        }
        
        .company-name {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .company-details {
            font-size: 12px;
            line-height: 1.4;
        }
        
        .invoice-info {
            text-align: right;
            flex: 1;
        }
        
        .invoice-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .invoice-number {
            font-size: 16px;
            margin-bottom: 5px;
        }
        
        .invoice-date {
            font-size: 14px;
        }
        
        /* Customer and Invoice Details */
        .details-section {
            display: flex;
            justify-content: space-between;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .customer-details, .invoice-details {
            flex: 1;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: bold;
            color: #00A86B;
            margin-bottom: 15px;
            border-bottom: 2px solid #00A86B;
            padding-bottom: 5px;
        }
        
        .detail-row {
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .detail-label {
            font-weight: bold;
            color: #555;
            min-width: 120px;
            display: inline-block;
        }
        
        /* Items Table */
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            font-size: 14px;
        }
        
        .items-table th {
            background: #00A86B;
            color: white;
            text-align: left;
            padding: 12px;
            font-weight: bold;
        }
        
        .items-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .items-table tr:nth-child(even) td {
            background: #f9f9f9;
        }
        
        .items-table tr:last-child td {
            border-bottom: 2px solid #00A86B;
        }
        
        /* Totals */
        .totals-section {
            margin: 30px 0;
            text-align: right;
        }
        
        .total-row {
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .total-label {
            display: inline-block;
            width: 150px;
            text-align: right;
            margin-right: 20px;
            font-weight: bold;
        }
        
        .total-value {
            display: inline-block;
            width: 120px;
            text-align: right;
            font-weight: bold;
        }
        
        .grand-total {
            font-size: 18px;
            color: #00A86B;
            border-top: 2px solid #00A86B;
            padding-top: 10px;
            margin-top: 10px;
        }
        
        /* Footer */
        .footer {
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 12px;
            color: #666;
        }
        
        .footer-content {
            text-align: center;
        }
        
        .terms-section {
            margin-top: 20px;
            padding: 15px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        
        .terms-title {
            font-weight: bold;
            color: #00A86B;
            margin-bottom: 10px;
        }
        
        /* Print styles */
        @media print {
            body {
                background: white;
            }
            
            .header {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .items-table th {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
        }
    </style>
</head>
<body>
    <div class="invoice-container">
        <!-- Header -->
        <div class="header">
            <div class="company-info">
                <div class="company-name">{{ company_name }}</div>
                <div class="company-details">
                    {{ company_address }}<br>
                    Phone: {{ company_phone }}<br>
                    Email: {{ company_email }}<br>
                    {% if company_website %}Website: {{ company_website }}{% endif %}
                </div>
            </div>
            <div class="invoice-info">
                <div class="invoice-title">{{ invoice_type }}</div>
                <div class="invoice-number">Invoice #: {{ invoice_number }}</div>
                <div class="invoice-date">Date: {{ invoice_date|date:"F d, Y" }}</div>
                <div class="invoice-date">Due Date: {{ due_date|date:"F d, Y" }}</div>
            </div>
        </div>
        
        <!-- Customer and Invoice Details -->
        <div class="details-section">
            <div class="customer-details">
                <div class="section-title">Customer Information</div>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    {{ customer.get_full_name|default:customer.username }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    {{ customer.email }}
                </div>
                {% if customer.phone %}
                <div class="detail-row">
                    <span class="detail-label">Phone:</span>
                    {{ customer.phone }}
                </div>
                {% endif %}
                {% if customer.address %}
                <div class="detail-row">
                    <span class="detail-label">Address:</span>
                    {{ customer.address }}
                </div>
                {% endif %}
            </div>
            
            <div class="invoice-details">
                <div class="section-title">Invoice Details</div>
                <div class="detail-row">
                    <span class="detail-label">Invoice #:</span>
                    {{ invoice_number }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    {{ invoice_date|date:"F d, Y" }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Due Date:</span>
                    {{ due_date|date:"F d, Y" }}
                </div>
                {% if rental_order %}
                <div class="detail-row">
                    <span class="detail-label">Order #:</span>
                    {{ rental_order.order_number }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span>
                    {{ duration_days }} days
                </div>
                {% endif %}
                {% if payment %}
                <div class="detail-row">
                    <span class="detail-label">Payment Method:</span>
                    {{ payment_method }}
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Items Table -->
        <table class="items-table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Duration</th>
                    <th>Rate</th>
                    <th>Qty</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {% for item in invoice_items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td>{{ item.duration|default:"-" }}</td>
                    <td>{{ currency }} {{ item.unit_price }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ currency }} {{ item.total_price }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- Totals -->
        <div class="totals-section">
            <div class="total-row">
                <span class="total-label">Subtotal:</span>
                <span class="total-value">{{ currency }} {{ subtotal }}</span>
            </div>
            {% if tax_amount > 0 %}
            <div class="total-row">
                <span class="total-label">Tax:</span>
                <span class="total-value">{{ currency }} {{ tax_amount }}</span>
            </div>
            {% endif %}
            {% if discount_amount > 0 %}
            <div class="total-row">
                <span class="total-label">Discount:</span>
                <span class="total-value">-{{ currency }} {{ discount_amount }}</span>
            </div>
            {% endif %}
            <div class="total-row grand-total">
                <span class="total-label">Grand Total:</span>
                <span class="total-value">{{ currency }} {{ total_amount }}</span>
            </div>
            {% if amount_paid > 0 %}
            <div class="total-row">
                <span class="total-label">Amount Paid:</span>
                <span class="total-value">{{ currency }} {{ amount_paid }}</span>
            </div>
            <div class="total-row">
                <span class="total-label">Balance Due:</span>
                <span class="total-value">{{ currency }} {{ balance_due }}</span>
            </div>
            {% endif %}
        </div>
        
        <!-- Notes -->
        {% if notes %}
        <div class="terms-section">
            <div class="terms-title">Notes:</div>
            <div>{{ notes|linebreaks }}</div>
        </div>
        {% endif %}
        
        <!-- Terms and Conditions -->
        {% if terms_and_conditions %}
        <div class="terms-section">
            <div class="terms-title">Terms and Conditions:</div>
            <div>{{ terms_and_conditions|linebreaks }}</div>
        </div>
        {% endif %}
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-content">
                Thank you for choosing <strong>{{ company_name }}</strong>!<br>
                For any queries, please contact us at {{ company_email }}<br>
                Generated on {{ generated_at|date:"F d, Y at g:i A" }}
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    def generate_pdf(self):
        """Generate PDF from the invoice template."""
        try:
            # Prepare context
            context = self._prepare_context()
            
            # Get template content
            template_content = self._get_template_content()
            
            # Render HTML
            html_content = render_to_string(
                template_string=template_content,
                context=context
            )
            
            # Create PDF
            html_doc = HTML(string=html_content)
            css = CSS(string='', font_config=self.font_config)
            
            # Generate PDF
            pdf_bytes = html_doc.write_pdf(
                stylesheets=[css],
                font_config=self.font_config
            )
            
            # Save PDF to file
            filename = f"invoice_{self.invoice.invoice_number}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_file.flush()
                
                # Save to Django file field
                with open(tmp_file.name, 'rb') as f:
                    self.invoice.pdf_file.save(filename, File(f), save=True)
                
                # Update invoice
                self.invoice.pdf_generated_at = timezone.now()
                self.invoice.save(update_fields=['pdf_generated_at'])
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            logger.info(f"PDF generated successfully for invoice {self.invoice.invoice_number}")
            return self.invoice.pdf_file
            
        except Exception as e:
            logger.error(f"Error generating PDF for invoice {self.invoice.invoice_number}: {str(e)}")
            raise
    
    def generate_pdf_bytes(self):
        """Generate PDF bytes without saving to file."""
        try:
            # Prepare context
            context = self._prepare_context()
            
            # Get template content
            template_content = self._get_template_content()
            
            # Render HTML
            html_content = render_to_string(
                template_string=template_content,
                context=context
            )
            
            # Create PDF
            html_doc = HTML(string=html_content)
            css = CSS(string='', font_config=self.font_config)
            
            # Generate PDF bytes
            pdf_bytes = html_doc.write_pdf(
                stylesheets=[css],
                font_config=self.font_config
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF bytes for invoice {self.invoice.invoice_number}: {str(e)}")
            raise


def generate_invoice_pdf(invoice, template=None):
    """Convenience function to generate PDF for an invoice."""
    generator = InvoicePDFGenerator(invoice, template)
    return generator.generate_pdf()


def generate_invoice_pdf_bytes(invoice, template=None):
    """Convenience function to generate PDF bytes for an invoice."""
    generator = InvoicePDFGenerator(invoice, template)
    return generator.generate_pdf_bytes()
