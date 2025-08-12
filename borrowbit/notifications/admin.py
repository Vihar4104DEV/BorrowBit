from django.contrib import admin
from .models import Notification, EmailTemplate

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'template_type')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'category', 'status', 'created_at', 'sent_at')
    list_filter = ('notification_type', 'category', 'status', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'subject', 'recipient')
    readonly_fields = ('created_at', 'sent_at', 'retry_count')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'category', 'status')
        }),
        ('Content', {
            'fields': ('recipient', 'subject', 'message', 'html_content')
        }),
        ('Related Objects', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'error_message', 'retry_count', 'max_retries'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        # Notifications are typically created programmatically
        return False
    
    actions = ['retry_failed_notifications', 'mark_as_sent']
    
    def retry_failed_notifications(self, request, queryset):
        """Retry sending failed notifications"""
        failed_notifications = queryset.filter(status__in=['FAILED', 'RETRYING'])
        retried_count = 0
        
        for notification in failed_notifications:
            if notification.can_retry:
                notification.mark_retrying()
                retried_count += 1
        
        self.message_user(
            request, 
            f"Retried {retried_count} failed notifications."
        )
    
    retry_failed_notifications.short_description = "Retry failed notifications"
    
    def mark_as_sent(self, request, queryset):
        """Mark notifications as sent (for testing purposes)"""
        updated_count = queryset.update(status='SENT')
        self.message_user(
            request, 
            f"Marked {updated_count} notifications as sent."
        )
    
    mark_as_sent.short_description = "Mark as sent (for testing)"
