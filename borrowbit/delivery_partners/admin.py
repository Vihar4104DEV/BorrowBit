from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    DeliveryPartner, DeliveryJob, JobAssignment, 
    DeliveryTracking, PartnerEarnings
)


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    """Admin interface for DeliveryPartner model."""
    list_display = [
        'partner_code', 'user_name', 'status', 'vehicle_type', 
        'city', 'rating', 'total_deliveries', 'is_available', 'created_at'
    ]
    list_filter = [
        'status', 'partner_type', 'vehicle_type', 'city', 'state', 
        'is_available', 'created_at'
    ]
    search_fields = [
        'partner_code', 'user__first_name', 'user__last_name', 
        'user__email', 'phone_number', 'vehicle_number'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'partner_code', 'rating', 'total_deliveries', 
        'successful_deliveries', 'failed_deliveries', 'created_at', 
        'updated_at', 'last_location_update'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'partner_code', 'partner_type', 'status')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'alternate_phone', 'emergency_contact')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_number', 'vehicle_model', 'vehicle_color')
        }),
        ('Service Area', {
            'fields': ('service_areas', 'max_delivery_distance')
        }),
        ('Performance Metrics', {
            'fields': ('rating', 'total_deliveries', 'successful_deliveries', 'failed_deliveries')
        }),
        ('Availability', {
            'fields': ('is_available', 'available_from', 'available_to', 'working_days')
        }),
        ('Financial Information', {
            'fields': ('commission_rate', 'minimum_payout')
        }),
        ('Location Tracking', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update')
        }),
        ('Documents', {
            'fields': ('documents',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        """Display user's full name."""
        if obj.user:
            return obj.user.get_full_name()
        return "N/A"
    user_name.short_description = "Partner Name"
    
    actions = ['activate_partners', 'deactivate_partners', 'suspend_partners']
    
    def activate_partners(self, request, queryset):
        """Activate selected delivery partners."""
        updated = queryset.update(status='active', is_available=True)
        self.message_user(request, f'{updated} delivery partners have been activated.')
    activate_partners.short_description = "Activate selected delivery partners"
    
    def deactivate_partners(self, request, queryset):
        """Deactivate selected delivery partners."""
        updated = queryset.update(status='inactive', is_available=False)
        self.message_user(request, f'{updated} delivery partners have been deactivated.')
    deactivate_partners.short_description = "Deactivate selected delivery partners"
    
    def suspend_partners(self, request, queryset):
        """Suspend selected delivery partners."""
        updated = queryset.update(status='suspended', is_available=False)
        self.message_user(request, f'{updated} delivery partners have been suspended.')
    suspend_partners.short_description = "Suspend selected delivery partners"


@admin.register(DeliveryJob)
class DeliveryJobAdmin(admin.ModelAdmin):
    """Admin interface for DeliveryJob model."""
    list_display = [
        'job_id', 'customer_name', 'job_type', 'status', 'priority',
        'pickup_city', 'delivery_city', 'total_fare', 'assigned_partner_code',
        'pickup_date', 'is_urgent', 'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'priority', 'is_urgent', 'pickup_city', 
        'delivery_city', 'pickup_date', 'delivery_date', 'created_at'
    ]
    search_fields = [
        'job_id', 'customer_name', 'customer_phone', 'tracking_number',
        'pickup_address', 'delivery_address'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'job_id', 'tracking_number', 'total_fare', 'assigned_at',
        'accepted_at', 'rejected_at', 'actual_pickup_time', 'actual_delivery_time',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'job_type', 'status', 'priority', 'tracking_number')
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_phone', 'customer_email')
        }),
        ('Pickup Information', {
            'fields': (
                'pickup_address', 'pickup_pincode', 'pickup_city', 'pickup_state',
                'pickup_latitude', 'pickup_longitude', 'pickup_instructions',
                'pickup_contact_name', 'pickup_contact_phone'
            )
        }),
        ('Delivery Information', {
            'fields': (
                'delivery_address', 'delivery_pincode', 'delivery_city', 'delivery_state',
                'delivery_latitude', 'delivery_longitude', 'delivery_instructions',
                'delivery_contact_name', 'delivery_contact_phone'
            )
        }),
        ('Package Information', {
            'fields': (
                'package_description', 'package_weight', 'package_dimensions',
                'package_value', 'is_fragile', 'is_urgent'
            )
        }),
        ('Timing Information', {
            'fields': (
                'pickup_date', 'pickup_time_slot', 'delivery_date', 'delivery_time_slot',
                'estimated_delivery_time', 'actual_pickup_time', 'actual_delivery_time'
            )
        }),
        ('Financial Information', {
            'fields': ('base_fare', 'distance_fare', 'priority_fare', 'total_fare', 'partner_commission')
        }),
        ('Assignment Information', {
            'fields': ('assigned_partner', 'assigned_at', 'accepted_at', 'rejected_at', 'rejection_reason')
        }),
        ('Tracking Information', {
            'fields': ('current_location', 'route_optimization')
        }),
        ('Additional Information', {
            'fields': ('special_requirements', 'insurance_required', 'insurance_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assigned_partner_code(self, obj):
        """Display assigned partner code."""
        if obj.assigned_partner:
            return obj.assigned_partner.partner_code
        return "Not Assigned"
    assigned_partner_code.short_description = "Assigned Partner"
    
    actions = ['mark_as_pending', 'mark_as_assigned', 'mark_as_delivered', 'mark_as_failed']
    
    def mark_as_pending(self, request, queryset):
        """Mark selected jobs as pending."""
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} jobs have been marked as pending.')
    mark_as_pending.short_description = "Mark selected jobs as pending"
    
    def mark_as_assigned(self, request, queryset):
        """Mark selected jobs as assigned."""
        updated = queryset.update(status='assigned')
        self.message_user(request, f'{updated} jobs have been marked as assigned.')
    mark_as_assigned.short_description = "Mark selected jobs as assigned"
    
    def mark_as_delivered(self, request, queryset):
        """Mark selected jobs as delivered."""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} jobs have been marked as delivered.')
    mark_as_delivered.short_description = "Mark selected jobs as delivered"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected jobs as failed."""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} jobs have been marked as failed.')
    mark_as_failed.short_description = "Mark selected jobs as failed"


@admin.register(JobAssignment)
class JobAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for JobAssignment model."""
    list_display = [
        'id', 'job_id', 'partner_code', 'status', 'assigned_at',
        'expires_at', 'responded_at', 'is_expired'
    ]
    list_filter = ['status', 'assigned_at', 'expires_at', 'responded_at']
    search_fields = ['job__job_id', 'partner__partner_code']
    ordering = ['-assigned_at']
    readonly_fields = [
        'id', 'assigned_at', 'expires_at', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Assignment Information', {
            'fields': ('job', 'partner', 'status')
        }),
        ('Timing Information', {
            'fields': ('assigned_at', 'expires_at', 'responded_at', 'response_time')
        }),
        ('Response Details', {
            'fields': ('rejection_reason', 'estimated_pickup_time', 'estimated_delivery_time', 'partner_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def job_id(self, obj):
        """Display job ID."""
        return obj.job.job_id if obj.job else "N/A"
    job_id.short_description = "Job ID"
    
    def partner_code(self, obj):
        """Display partner code."""
        return obj.partner.partner_code if obj.partner else "N/A"
    partner_code.short_description = "Partner Code"
    
    def is_expired(self, obj):
        """Check if assignment is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    """Admin interface for DeliveryTracking model."""
    list_display = [
        'id', 'job_id', 'partner_code', 'event_type', 'event_time',
        'has_location', 'created_at'
    ]
    list_filter = ['event_type', 'event_time', 'created_at']
    search_fields = ['job__job_id', 'partner__partner_code', 'description']
    ordering = ['-event_time']
    readonly_fields = [
        'id', 'event_time', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Tracking Information', {
            'fields': ('job', 'partner', 'event_type')
        }),
        ('Event Details', {
            'fields': ('description', 'additional_data')
        }),
        ('Location Information', {
            'fields': ('latitude', 'longitude', 'location_address')
        }),
        ('Timing', {
            'fields': ('event_time',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def job_id(self, obj):
        """Display job ID."""
        return obj.job.job_id if obj.job else "N/A"
    job_id.short_description = "Job ID"
    
    def partner_code(self, obj):
        """Display partner code."""
        return obj.partner.partner_code if obj.partner else "N/A"
    partner_code.short_description = "Partner Code"
    
    def has_location(self, obj):
        """Check if tracking has location data."""
        return bool(obj.latitude and obj.longitude)
    has_location.boolean = True
    has_location.short_description = "Has Location"


@admin.register(PartnerEarnings)
class PartnerEarningsAdmin(admin.ModelAdmin):
    """Admin interface for PartnerEarnings model."""
    list_display = [
        'id', 'partner_code', 'job_id', 'earning_type', 'status',
        'amount', 'commission_amount', 'net_amount', 'earned_date',
        'paid_at'
    ]
    list_filter = [
        'status', 'earning_type', 'earned_date', 'approved_at', 'paid_at'
    ]
    search_fields = [
        'partner__partner_code', 'job__job_id', 'payment_reference'
    ]
    ordering = ['-earned_date']
    readonly_fields = [
        'id', 'commission_amount', 'net_amount', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Earning Information', {
            'fields': ('partner', 'job', 'earning_type', 'status')
        }),
        ('Financial Details', {
            'fields': ('amount', 'commission_rate', 'commission_amount', 'net_amount')
        }),
        ('Timing Information', {
            'fields': ('earned_date', 'approved_at', 'paid_at')
        }),
        ('Additional Information', {
            'fields': ('description', 'payment_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def partner_code(self, obj):
        """Display partner code."""
        return obj.partner.partner_code if obj.partner else "N/A"
    partner_code.short_description = "Partner Code"
    
    def job_id(self, obj):
        """Display job ID."""
        return obj.job.job_id if obj.job else "N/A"
    job_id.short_description = "Job ID"
    
    actions = ['approve_earnings', 'mark_as_paid', 'mark_as_cancelled']
    
    def approve_earnings(self, request, queryset):
        """Approve selected earnings."""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} earnings have been approved.')
    approve_earnings.short_description = "Approve selected earnings"
    
    def mark_as_paid(self, request, queryset):
        """Mark selected earnings as paid."""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} earnings have been marked as paid.')
    mark_as_paid.short_description = "Mark selected earnings as paid"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected earnings as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} earnings have been marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected earnings as cancelled"
