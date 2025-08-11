"""
Core models for the rental backend application.

This module contains base abstract models and common functionality.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    """Base abstract model for common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        """Soft delete the object by setting is_deleted and is_active."""
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=['is_deleted', 'is_active', 'updated_at'])
        
    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.is_active = True
        self.save(update_fields=['is_deleted', 'is_active', 'updated_at'])


    class Meta:
        abstract = True




class NotificationTemplate(BaseModel):
    """Model for storing notification templates."""
    
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('PORTAL', 'Portal Notification'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Template Name"))
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name=_("Template Type"))
    subject = models.CharField(max_length=200, blank=True, verbose_name=_("Subject"))
    content = models.TextField(verbose_name=_("Content"))
    variables = models.JSONField(default=list, blank=True, verbose_name=_("Template Variables"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    class Meta:
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
