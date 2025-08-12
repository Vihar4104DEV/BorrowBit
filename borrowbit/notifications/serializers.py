from rest_framework import serializers
from .models import Notification, EmailTemplate

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for EmailTemplate model"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'subject', 
            'html_content', 'text_content', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_email', 'user_name', 'notification_type', 
            'category', 'recipient', 'subject', 'message', 'html_content',
            'status', 'created_at', 'sent_at', 'error_message', 
            'retry_count', 'max_retries', 'related_object_type', 
            'related_object_id'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_name', 'created_at', 'sent_at', 
            'error_message', 'retry_count'
        ]

class NotificationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for notification lists"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user_email', 'user_name', 'notification_type', 
            'category', 'subject', 'status', 'created_at', 'sent_at'
        ]
        read_only_fields = fields

class SendEmailRequestSerializer(serializers.Serializer):
    """Serializer for sending custom emails"""
    to_email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    html_content = serializers.CharField()
    text_content = serializers.CharField(required=False, allow_blank=True)
    from_email = serializers.EmailField(required=False)
    from_name = serializers.CharField(max_length=100, required=False)

class SendTemplateEmailRequestSerializer(serializers.Serializer):
    """Serializer for sending template emails"""
    to_email = serializers.EmailField()
    template_type = serializers.CharField(max_length=50)
    context = serializers.DictField(required=False, default=dict)
    from_email = serializers.EmailField(required=False)
    from_name = serializers.CharField(max_length=100, required=False)

class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_notifications = serializers.IntegerField()
    sent_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    retrying_notifications = serializers.IntegerField()
    notifications_by_category = serializers.DictField()
    notifications_by_type = serializers.DictField()
