"""
Admin configuration for payment management.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    RentalOrder, RentalOrderItem, Payment, PaymentGateway, 
    PaymentSchedule, PaymentNotification
)


@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    """Admin configuration for rental orders."""
    
    list_display = [
        'order_number', 'customer', 'status', 'total_amount', 
        'rental_start_date', 'rental_end_date', 'created_at'
    ]
    list_filter = [
        'status', 'rental_start_date', 'rental_end_date', 
        'created_at', 'customer__is_active'
    ]
    search_fields = [
        'order_number', 'customer__email', 'customer__first_name', 
        'customer__last_name', 'notes'
    ]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'customer', 'status', 'notes')
        }),
        ('Rental Dates', {
            'fields': ('rental_start_date', 'rental_end_date', 'actual_return_date')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'late_fee_amount', 'total_amount', 'deposit_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('customer')
    
    def customer_link(self, obj):
        """Create a link to the customer admin page."""
        if obj.customer:
            url = reverse('admin:user_user_change', args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', url, obj.customer)
        return '-'
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer'


@admin.register(RentalOrderItem)
class RentalOrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for rental order items."""
    
    list_display = [
        'id', 'order', 'product', 'quantity', 'unit_price', 
        'total_price', 'deposit_per_unit'
    ]
    list_filter = ['order__status', 'created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('order', 'product')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for payments."""
    
    list_display = [
        'payment_id', 'order_link', 'payment_type', 'amount', 
        'status', 'gateway', 'payment_date', 'created_at'
    ]
    list_filter = [
        'status', 'payment_type', 'gateway', 'payment_date', 
        'created_at', 'order__status'
    ]
    search_fields = [
        'payment_id', 'gateway_transaction_id', 'order__order_number',
        'order__customer__email'
    ]
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'order', 'payment_type', 'amount', 'status')
        }),
        ('Gateway Information', {
            'fields': ('gateway', 'gateway_transaction_id', 'gateway_response')
        }),
        ('Timing', {
            'fields': ('payment_date', 'due_date')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('order', 'gateway')
    
    def order_link(self, obj):
        """Create a link to the order admin page."""
        if obj.order:
            url = reverse('admin:payments_rentalorder_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__order_number'


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    """Admin configuration for payment gateways."""
    
    list_display = [
        'name', 'gateway_type', 'is_active', 'is_test_mode', 
        'created_at'
    ]
    list_filter = ['gateway_type', 'is_active', 'is_test_mode', 'created_at']
    search_fields = ['name', 'gateway_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Gateway Information', {
            'fields': ('name', 'gateway_type', 'is_active', 'is_test_mode')
        }),
        ('Credentials', {
            'fields': ('api_key', 'secret_key'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for payment schedules."""
    
    list_display = [
        'id', 'order_link', 'payment_type', 'amount', 
        'due_date', 'is_paid', 'created_at'
    ]
    list_filter = [
        'payment_type', 'is_paid', 'due_date', 'created_at', 
        'order__status'
    ]
    search_fields = [
        'order__order_number', 'order__customer__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('order', 'payment')
    
    def order_link(self, obj):
        """Create a link to the order admin page."""
        if obj.order:
            url = reverse('admin:payments_rentalorder_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__order_number'


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    """Admin configuration for payment notifications."""
    
    list_display = [
        'id', 'order_link', 'notification_type', 'subject', 
        'is_sent', 'scheduled_for', 'sent_at'
    ]
    list_filter = [
        'notification_type', 'is_sent', 'scheduled_for', 
        'sent_at', 'created_at', 'order__status'
    ]
    search_fields = [
        'subject', 'message', 'order__order_number', 
        'order__customer__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('order', 'notification_type', 'subject', 'message')
        }),
        ('Delivery Status', {
            'fields': ('is_sent', 'sent_at', 'scheduled_for')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('order')
    
    def order_link(self, obj):
        """Create a link to the order admin page."""
        if obj.order:
            url = reverse('admin:payments_rentalorder_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__order_number'