from django.db import models
from django.utils import timezone
from user.models import User

# Create your models here.

class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE)
    recipient = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def mark_sent(self):
        self.status = "SENT"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at"])

    def mark_failed(self, error):
        self.status = "FAILED"
        self.error_message = error
        self.save(update_fields=["status", "error_message"])
