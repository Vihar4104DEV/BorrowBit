"""
Invoice views for handling invoice-related requests.

This module contains views for invoice management, PDF generation, and download.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
import logging

from .models import Invoice, InvoiceItem, InvoiceTemplate
from .services import InvoiceService, InvoiceItemService
from .pdf_generator import generate_invoice_pdf_bytes

logger = logging.getLogger(__name__)


@login_required
def invoice_list(request):
    """Display list of invoices for the current user."""
    try:
        # Get user's invoices
        invoices = InvoiceService.get_customer_invoices(request.user)
        
        # Apply filters
        status_filter = request.GET.get('status')
        invoice_type_filter = request.GET.get('invoice_type')
        search_query = request.GET.get('search')
        
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        if invoice_type_filter:
            invoices = invoices.filter(invoice_type=invoice_type_filter)
        
        if search_query:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(invoices, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'invoices': page_obj,
            'status_choices': Invoice.STATUS_CHOICES,
            'invoice_type_choices': Invoice.INVOICE_TYPE_CHOICES,
            'current_filters': {
                'status': status_filter,
                'invoice_type': invoice_type_filter,
                'search': search_query,
            }
        }
        
        return render(request, 'invoices/invoice_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in invoice_list view: {str(e)}")
        messages.error(request, "An error occurred while loading invoices.")
        return render(request, 'invoices/invoice_list.html', {'invoices': []})


@login_required
def invoice_detail(request, invoice_id):
    """Display detailed view of an invoice."""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Mark as viewed
        if not invoice.viewed_at:
            invoice.viewed_at = timezone.now()
            invoice.save(update_fields=['viewed_at'])
        
        context = {
            'invoice': invoice,
            'invoice_items': invoice.items.all(),
        }
        
        return render(request, 'invoices/invoice_detail.html', context)
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('invoice_list')
    except Exception as e:
        logger.error(f"Error in invoice_detail view: {str(e)}")
        messages.error(request, "An error occurred while loading the invoice.")
        return redirect('invoice_list')


@login_required
def invoice_pdf_download(request, invoice_id):
    """Download PDF for an invoice."""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Generate PDF if it doesn't exist
        if not invoice.pdf_file:
            InvoiceService.generate_pdf_for_invoice(invoice)
        
        # Return PDF file
        if invoice.pdf_file:
            response = HttpResponse(invoice.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            return response
        else:
            messages.error(request, "PDF could not be generated.")
            return redirect('invoice_detail', invoice_id=invoice_id)
            
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('invoice_list')
    except Exception as e:
        logger.error(f"Error in invoice_pdf_download view: {str(e)}")
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('invoice_detail', invoice_id=invoice_id)


@login_required
def invoice_pdf_view(request, invoice_id):
    """View PDF for an invoice in browser."""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Generate PDF bytes
        pdf_bytes = InvoiceService.get_invoice_pdf_bytes(invoice)
        
        # Return PDF for viewing
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('invoice_list')
    except Exception as e:
        logger.error(f"Error in invoice_pdf_view view: {str(e)}")
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('invoice_detail', invoice_id=invoice_id)


@login_required
def regenerate_invoice_pdf(request, invoice_id):
    """Regenerate PDF for an invoice."""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Regenerate PDF
        InvoiceService.generate_pdf_for_invoice(invoice, force_regenerate=True)
        
        messages.success(request, "PDF regenerated successfully.")
        return redirect('invoice_detail', invoice_id=invoice_id)
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('invoice_list')
    except Exception as e:
        logger.error(f"Error in regenerate_invoice_pdf view: {str(e)}")
        messages.error(request, "An error occurred while regenerating the PDF.")
        return redirect('invoice_detail', invoice_id=invoice_id)


# Admin views (for staff only)
@login_required
def admin_invoice_list(request):
    """Admin view for listing all invoices."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        invoices = Invoice.objects.all().order_by('-invoice_date', '-created_at')
        
        # Apply filters
        status_filter = request.GET.get('status')
        invoice_type_filter = request.GET.get('invoice_type')
        customer_filter = request.GET.get('customer')
        search_query = request.GET.get('search')
        
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        if invoice_type_filter:
            invoices = invoices.filter(invoice_type=invoice_type_filter)
        
        if customer_filter:
            invoices = invoices.filter(customer__email__icontains=customer_filter)
        
        if search_query:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search_query) |
                Q(customer__email__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(invoices, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'invoices': page_obj,
            'status_choices': Invoice.STATUS_CHOICES,
            'invoice_type_choices': Invoice.INVOICE_TYPE_CHOICES,
            'current_filters': {
                'status': status_filter,
                'invoice_type': invoice_type_filter,
                'customer': customer_filter,
                'search': search_query,
            }
        }
        
        return render(request, 'invoices/admin_invoice_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_invoice_list view: {str(e)}")
        messages.error(request, "An error occurred while loading invoices.")
        return render(request, 'invoices/admin_invoice_list.html', {'invoices': []})


@login_required
def admin_invoice_detail(request, invoice_id):
    """Admin view for detailed invoice information."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        context = {
            'invoice': invoice,
            'invoice_items': invoice.items.all(),
        }
        
        return render(request, 'invoices/admin_invoice_detail.html', context)
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('admin_invoice_list')
    except Exception as e:
        logger.error(f"Error in admin_invoice_detail view: {str(e)}")
        messages.error(request, "An error occurred while loading the invoice.")
        return redirect('admin_invoice_list')


@login_required
def admin_invoice_pdf_download(request, invoice_id):
    """Admin PDF download for any invoice."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        # Generate PDF if it doesn't exist
        if not invoice.pdf_file:
            InvoiceService.generate_pdf_for_invoice(invoice)
        
        # Return PDF file
        if invoice.pdf_file:
            response = HttpResponse(invoice.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            return response
        else:
            messages.error(request, "PDF could not be generated.")
            return redirect('admin_invoice_detail', invoice_id=invoice_id)
            
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('admin_invoice_list')
    except Exception as e:
        logger.error(f"Error in admin_invoice_pdf_download view: {str(e)}")
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('admin_invoice_detail', invoice_id=invoice_id)


@login_required
def mark_invoice_as_paid(request, invoice_id):
    """Mark an invoice as paid (admin only)."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        if request.method == 'POST':
            amount = request.POST.get('amount')
            if amount:
                InvoiceService.mark_invoice_as_paid(invoice, amount=amount)
                messages.success(request, "Invoice marked as paid successfully.")
            else:
                InvoiceService.mark_invoice_as_paid(invoice)
                messages.success(request, "Invoice marked as paid successfully.")
        
        return redirect('admin_invoice_detail', invoice_id=invoice_id)
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('admin_invoice_list')
    except Exception as e:
        logger.error(f"Error in mark_invoice_as_paid view: {str(e)}")
        messages.error(request, "An error occurred while marking the invoice as paid.")
        return redirect('admin_invoice_detail', invoice_id=invoice_id)


@login_required
def send_invoice(request, invoice_id):
    """Mark an invoice as sent (admin only)."""
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        
        if request.method == 'POST':
            InvoiceService.send_invoice(invoice)
            messages.success(request, "Invoice marked as sent successfully.")
        
        return redirect('admin_invoice_detail', invoice_id=invoice_id)
        
    except Http404:
        messages.error(request, "Invoice not found.")
        return redirect('admin_invoice_list')
    except Exception as e:
        logger.error(f"Error in send_invoice view: {str(e)}")
        messages.error(request, "An error occurred while sending the invoice.")
        return redirect('admin_invoice_detail', invoice_id=invoice_id)


# Demo/Test views for development
def demo_invoice_pdf(request):
    """Demo view to generate a sample invoice PDF for testing."""
    try:
        from django.contrib.auth import get_user_model
        from decimal import Decimal
        
        User = get_user_model()
        
        # Get or create a test user
        test_user, created = User.objects.get_or_create(
            email='demo@borrowbit.com',
            defaults={
                'username': 'demo_user',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        
        # Create a sample invoice
        invoice = Invoice.objects.create(
            customer=test_user,
            invoice_type='RENTAL',
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            subtotal=Decimal('1500.00'),
            tax_amount=Decimal('150.00'),
            discount_amount=Decimal('100.00'),
            total_amount=Decimal('1550.00'),
            currency='INR',
            notes='This is a demo invoice for testing purposes.',
            terms_and_conditions='Demo terms and conditions for testing.',
        )
        
        # Create sample invoice items
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Camera Equipment Rental',
            quantity=1,
            unit_price=Decimal('1000.00'),
            duration='3 days',
            rate_type='Daily',
        )
        
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Lighting Equipment Rental',
            quantity=2,
            unit_price=Decimal('250.00'),
            duration='3 days',
            rate_type='Daily',
        )
        
        # Generate PDF
        pdf_bytes = InvoiceService.get_invoice_pdf_bytes(invoice)
        
        # Return PDF for viewing
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="demo_invoice_{invoice.invoice_number}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error in demo_invoice_pdf view: {str(e)}")
        return HttpResponse(f"Error generating demo PDF: {str(e)}", status=500)


# API endpoints for AJAX requests
@login_required
@require_http_methods(["POST"])
def ajax_generate_pdf(request, invoice_id):
    """AJAX endpoint to generate PDF for an invoice."""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Generate PDF
        InvoiceService.generate_pdf_for_invoice(invoice)
        
        return HttpResponse(
            f'{{"success": true, "message": "PDF generated successfully", "pdf_url": "{invoice.pdf_file.url}"}}',
            content_type='application/json'
        )
        
    except Http404:
        return HttpResponse(
            '{"success": false, "message": "Invoice not found"}',
            content_type='application/json',
            status=404
        )
    except Exception as e:
        logger.error(f"Error in ajax_generate_pdf view: {str(e)}")
        return HttpResponse(
            f'{{"success": false, "message": "Error generating PDF: {str(e)}"}}',
            content_type='application/json',
            status=500
        )


# Class-based views
class InvoiceListView(LoginRequiredMixin, ListView):
    """Class-based view for invoice list."""
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter invoices for current user."""
        return InvoiceService.get_customer_invoices(self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add additional context."""
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Invoice.STATUS_CHOICES
        context['invoice_type_choices'] = Invoice.INVOICE_TYPE_CHOICES
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Class-based view for invoice detail."""
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        """Filter invoices for current user."""
        return Invoice.objects.filter(customer=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add invoice items to context."""
        context = super().get_context_data(**kwargs)
        context['invoice_items'] = self.object.items.all()
        return context
