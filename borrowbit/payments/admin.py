"""
Admin configuration for payment models.

This module contains admin configurations for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade management features.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PaymentMethod, CheckoutSession, Payment, PaymentWebhook, PaymentRefund
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentMethod model."""
    
    list_display = [
        'name', 'method_type', 'provider', 'is_active', 'is_default', 
        'processing_fee_percentage', 'processing_fee_fixed', 'sort_order'
    ]
    list_filter = [
        'method_type', 'provider', 'is_active', 'is_default', 'created_at'
    ]
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'method_type', 'provider', 'description', 'icon')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_default', 'sort_order')
        }),
        ('Fee Structure', {
            'fields': ('processing_fee_percentage', 'processing_fee_fixed')
        }),
        ('Amount Limits', {
            'fields': ('minimum_amount', 'maximum_amount')
        }),
        ('Provider Configuration', {
            'fields': ('provider_config',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_payment_methods', 'deactivate_payment_methods']
    
    def activate_payment_methods(self, request, queryset):
        """Activate selected payment methods."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} payment method(s) activated successfully.')
    activate_payment_methods.short_description = "Activate selected payment methods"
    
    def deactivate_payment_methods(self, request, queryset):
        """Deactivate selected payment methods."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} payment method(s) deactivated successfully.')
    deactivate_payment_methods.short_description = "Deactivate selected payment methods"


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    """Admin configuration for CheckoutSession model."""
    
    list_display = [
        'session_id', 'user', 'payment_method', 'amount', 'total_amount', 
        'status', 'expires_at', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'currency', 'created_at', 'expires_at'
    ]
    search_fields = ['session_id', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'session_id', 'user', 'payment_method', 'amount', 'currency',
        'processing_fee', 'total_amount', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'user', 'payment_method', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency', 'processing_fee', 'total_amount')
        }),
        ('Session Details', {
            'fields': ('expires_at', 'payment_intent_id', 'checkout_url')
        }),
        ('Metadata', {
            'fields': ('metadata', 'description')
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'cancelled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected sessions as completed."""
        for session in queryset:
            if session.status == 'PENDING':
                session.mark_as_paid()
        self.message_user(request, f'{queryset.count()} session(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected sessions as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected sessions as failed."""
        for session in queryset:
            if session.status in ['PENDING', 'PROCESSING']:
                session.mark_as_failed()
        self.message_user(request, f'{queryset.count()} session(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected sessions as failed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected sessions as cancelled."""
        for session in queryset:
            if session.status in ['PENDING', 'PROCESSING']:
                session.mark_as_cancelled()
        self.message_user(request, f'{queryset.count()} session(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected sessions as cancelled"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = [
        'payment_id', 'user', 'transaction_type', 'amount', 'total_amount', 
        'status', 'payment_method', 'created_at'
    ]
    list_filter = [
        'status', 'transaction_type', 'payment_method', 'currency', 'created_at'
    ]
    search_fields = [
        'payment_id', 'user__email', 'user__first_name', 'user__last_name',
        'provider_payment_id', 'payment_intent_id'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'payment_id', 'user', 'checkout_session', 'payment_method',
        'amount', 'currency', 'processing_fee', 'total_amount', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'user', 'checkout_session', 'payment_method', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency', 'processing_fee', 'total_amount')
        }),
        ('Transaction Details', {
            'fields': ('transaction_type', 'provider_payment_id', 'provider_transaction_id', 'payment_intent_id')
        }),
        ('Payment Method Details', {
            'fields': ('payment_method_details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'completed_at', 'failed_at')
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'description')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_processing']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected payments as completed."""
        for payment in queryset:
            if payment.status == 'PROCESSING':
                payment.mark_as_completed()
        self.message_user(request, f'{queryset.count()} payment(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed."""
        for payment in queryset:
            if payment.status == 'PROCESSING':
                payment.mark_as_failed()
        self.message_user(request, f'{queryset.count()} payment(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected payments as failed"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected payments as processing."""
        for payment in queryset:
            if payment.status == 'PENDING':
                payment.mark_as_processing()
        self.message_user(request, f'{queryset.count()} payment(s) marked as processing.')
    mark_as_processing.short_description = "Mark selected payments as processing"


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentRefund model."""
    
    list_display = [
        'refund_id', 'payment', 'user', 'amount', 'status', 'reason', 'created_at'
    ]
    list_filter = [
        'status', 'reason', 'currency', 'created_at'
    ]
    search_fields = [
        'refund_id', 'payment__payment_id', 'user__email', 'user__first_name', 'user__last_name'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'refund_id', 'payment', 'user', 'amount', 'currency', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('refund_id', 'payment', 'user', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency')
        }),
        ('Refund Details', {
            'fields': ('reason', 'description', 'provider_refund_id')
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'completed_at', 'failed_at')
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_processing']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected refunds as completed."""
        for refund in queryset:
            if refund.status == 'PROCESSING':
                refund.mark_as_completed()
        self.message_user(request, f'{queryset.count()} refund(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected refunds as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected refunds as failed."""
        for refund in queryset:
            if refund.status == 'PROCESSING':
                refund.mark_as_failed()
        self.message_user(request, f'{queryset.count()} refund(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected refunds as failed"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected refunds as processing."""
        for refund in queryset:
            if refund.status == 'PENDING':
                refund.mark_as_processing()
        self.message_user(request, f'{queryset.count()} refund(s) marked as processing.')
    mark_as_processing.short_description = "Mark selected refunds as processing"


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentWebhook model."""
    
    list_display = [
        'webhook_id', 'provider', 'event_type', 'status', 'event_id', 'retry_count', 'created_at'
    ]
    list_filter = [
        'provider', 'event_type', 'status', 'created_at'
    ]
    search_fields = [
        'webhook_id', 'event_id', 'object_id'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'webhook_id', 'provider', 'event_type', 'event_id', 'object_id',
        'raw_payload', 'processed_payload', 'headers', 'signature', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Webhook Information', {
            'fields': ('webhook_id', 'provider', 'event_type', 'status')
        }),
        ('Event Details', {
            'fields': ('event_id', 'object_id')
        }),
        ('Payload Information', {
            'fields': ('raw_payload', 'processed_payload'),
            'classes': ('collapse',)
        }),
        ('Headers and Signature', {
            'fields': ('headers', 'signature'),
            'classes': ('collapse',)
        }),
        ('Processing Information', {
            'fields': ('processed_at', 'error_message', 'retry_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processed', 'mark_as_failed', 'mark_as_ignored']
    
    def mark_as_processed(self, request, queryset):
        """Mark selected webhooks as processed."""
        for webhook in queryset:
            if webhook.status == 'PENDING':
                webhook.mark_as_processed()
        self.message_user(request, f'{queryset.count()} webhook(s) marked as processed.')
    mark_as_processed.short_description = "Mark selected webhooks as processed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected webhooks as failed."""
        for webhook in queryset:
            if webhook.status == 'PENDING':
                webhook.mark_as_failed("Manually marked as failed")
        self.message_user(request, f'{queryset.count()} webhook(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected webhooks as failed"
    
    def mark_as_ignored(self, request, queryset):
        """Mark selected webhooks as ignored."""
        for webhook in queryset:
            if webhook.status == 'PENDING':
                webhook.mark_as_ignored()
        self.message_user(request, f'{queryset.count()} webhook(s) marked as ignored.')
    mark_as_ignored.short_description = "Mark selected webhooks as ignored"
