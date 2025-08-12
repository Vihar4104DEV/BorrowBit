"""
Admin configuration for invoice models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Invoice, InvoiceItem, InvoiceTemplate
from django.utils import timezone


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceItem model."""
    list_display = ['invoice', 'product', 'description', 'quantity', 'unit_price', 'total_price']
    list_filter = ['rate_type']
    search_fields = ['description', 'product__name', 'invoice__invoice_number']
    readonly_fields = ['total_price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice', 'product', 'description')
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total_price', 'rate_type')
        }),
        ('Additional Details', {
            'fields': ('duration', 'notes'),
            'classes': ('collapse',)
        }),
    )


class InvoiceItemInline(admin.TabularInline):
    """Inline admin for InvoiceItem."""
    model = InvoiceItem
    extra = 1
    readonly_fields = ['total_price']
    fields = ['product', 'description', 'quantity', 'unit_price', 'total_price', 'duration', 'rate_type']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model."""
    list_display = [
        'invoice_number', 'customer_name', 'invoice_type', 'status', 
        'total_amount', 'amount_paid', 'balance_due', 'invoice_date', 
        'due_date', 'pdf_status'
    ]
    list_filter = [
        'status', 'invoice_type', 'invoice_date', 'due_date', 
        'currency', 'created_at'
    ]
    search_fields = [
        'invoice_number', 'customer__email', 'customer__first_name', 
        'customer__last_name', 'notes'
    ]
    readonly_fields = [
        'invoice_number', 'total_amount', 'balance_due', 'pdf_file', 
        'pdf_generated_at', 'sent_at', 'viewed_at', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'invoice_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'invoice_type', 'status', 'customer')
        }),
        ('Related Objects', {
            'fields': ('rental_order', 'payment'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'amount_paid', 'balance_due')
        }),
        ('Additional Information', {
            'fields': ('currency', 'notes', 'terms_and_conditions'),
            'classes': ('collapse',)
        }),
        ('PDF Information', {
            'fields': ('pdf_file', 'pdf_generated_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'viewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InvoiceItemInline]
    
    actions = ['mark_as_paid', 'mark_as_sent', 'generate_pdfs', 'send_invoices']
    
    def customer_name(self, obj):
        """Display customer full name."""
        return f"{obj.customer.get_full_name() or obj.customer.username}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'
    
    def pdf_status(self, obj):
        """Display PDF generation status."""
        if obj.pdf_file:
            return format_html(
                '<span style="color: green;">✓ Generated</span><br>'
                '<small>{}</small>',
                obj.pdf_generated_at.strftime('%Y-%m-%d %H:%M') if obj.pdf_generated_at else 'Unknown'
            )
        else:
            return format_html('<span style="color: red;">✗ Not Generated</span>')
    pdf_status.short_description = 'PDF Status'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('customer', 'rental_order', 'payment')
    
    def mark_as_paid(self, request, queryset):
        """Mark selected invoices as paid."""
        updated = queryset.update(status='PAID', paid_date=timezone.now().date())
        self.message_user(request, f'{updated} invoice(s) marked as paid.')
    mark_as_paid.short_description = "Mark selected invoices as paid"
    
    def mark_as_sent(self, request, queryset):
        """Mark selected invoices as sent."""
        updated = queryset.update(status='SENT', sent_at=timezone.now())
        self.message_user(request, f'{updated} invoice(s) marked as sent.')
    mark_as_sent.short_description = "Mark selected invoices as sent"
    
    def generate_pdfs(self, request, queryset):
        """Generate PDFs for selected invoices."""
        from .services import InvoiceService
        generated = 0
        for invoice in queryset:
            try:
                InvoiceService.generate_pdf_for_invoice(invoice, force_regenerate=True)
                generated += 1
            except Exception as e:
                self.message_user(request, f'Error generating PDF for {invoice.invoice_number}: {str(e)}', level='ERROR')
        
        if generated > 0:
            self.message_user(request, f'PDFs generated for {generated} invoice(s).')
    generate_pdfs.short_description = "Generate PDFs for selected invoices"
    
    def send_invoices(self, request, queryset):
        """Send selected invoices."""
        sent = 0
        for invoice in queryset:
            try:
                from .services import InvoiceService
                InvoiceService.send_invoice(invoice)
                sent += 1
            except Exception as e:
                self.message_user(request, f'Error sending invoice {invoice.invoice_number}: {str(e)}', level='ERROR')
        
        if sent > 0:
            self.message_user(request, f'{sent} invoice(s) marked as sent.')
    send_invoices.short_description = "Send selected invoices"


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceTemplate model."""
    list_display = ['name', 'is_default', 'is_active', 'company_name', 'show_tax', 'show_discount']
    list_filter = ['is_default', 'is_active', 'show_tax', 'show_discount', 'show_terms', 'show_payment_info']
    search_fields = ['name', 'company_name', 'company_email']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_default', 'is_active')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_address', 'company_phone', 'company_email', 'company_website', 'company_logo')
        }),
        ('Template Content', {
            'fields': ('html_template', 'css_styles'),
            'classes': ('collapse',)
        }),
        ('Invoice Settings', {
            'fields': ('invoice_prefix', 'show_tax', 'show_discount', 'show_terms', 'show_payment_info')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Ensure only one default template."""
        if obj.is_default:
            InvoiceTemplate.objects.filter(is_default=True).exclude(id=obj.id).update(is_default=False)
        super().save_model(request, obj, form, change)


# Custom admin site configuration
admin.site.site_header = "BorrowBit Invoice Management"
admin.site.site_title = "BorrowBit Admin"
admin.site.index_title = "Invoice Management Dashboard"
