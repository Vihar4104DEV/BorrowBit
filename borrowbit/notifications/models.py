from django.db import models
from django.utils import timezone
from user.models import User

# Create your models here.

class EmailTemplate(models.Model):
    """Email templates for different notification types"""
    TEMPLATE_TYPE_CHOICES = [
        ("USER_REGISTRATION", "User Registration"),
        ("RENTAL_CONFIRMATION", "Rental Confirmation"),
        ("PRODUCT_DELIVERY", "Product Delivery"),
        ("PRODUCT_RETURN", "Product Return"),
        ("RENTAL_REMINDER", "Rental Reminder"),
        ("PAYMENT_SUCCESS", "Payment Success"),
        ("PAYMENT_FAILED", "Payment Failed"),
        ("DELIVERY_UPDATE", "Delivery Update"),
        ("WELCOME_EMAIL", "Welcome Email"),
        ("PASSWORD_RESET", "Password Reset"),
        ("OTP_VERIFICATION", "OTP Verification"),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES, unique=True)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
        ("PUSH", "Push"),
    ]
    
    NOTIFICATION_CATEGORY = [
        ("USER_REGISTRATION", "User Registration"),
        ("RENTAL_CONFIRMATION", "Rental Confirmation"),
        ("PRODUCT_DELIVERY", "Product Delivery"),
        ("PRODUCT_RETURN", "Product Return"),
        ("RENTAL_REMINDER", "Rental Reminder"),
        ("PAYMENT_SUCCESS", "Payment Success"),
        ("PAYMENT_FAILED", "Payment Failed"),
        ("DELIVERY_UPDATE", "Delivery Update"),
        ("WELCOME_EMAIL", "Welcome Email"),
        ("PASSWORD_RESET", "Password Reset"),
        ("OTP_VERIFICATION", "OTP Verification"),
        ("SYSTEM", "System"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE)
    category = models.CharField(max_length=50, choices=NOTIFICATION_CATEGORY)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Related objects for context
    related_object_type = models.CharField(max_length=50, blank=True)  # e.g., 'rental', 'product'
    related_object_id = models.CharField(max_length=100, null=True, blank=True)  # Changed to CharField to handle UUIDs
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.category} - {self.user.email} - {self.status}"
    
    def mark_sent(self):
        self.status = "SENT"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at"])

    def mark_failed(self, error):
        self.status = "FAILED"
        self.error_message = error
        self.save(update_fields=["status", "error_message"])
    
    def mark_retrying(self):
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = "FAILED"
            self.error_message = f"Max retries ({self.max_retries}) exceeded"
        else:
            self.status = "RETRYING"
        self.save(update_fields=["status", "retry_count", "error_message"])
    
    @property
    def can_retry(self):
        return self.status in ["FAILED", "RETRYING"] and self.retry_count < self.max_retries
