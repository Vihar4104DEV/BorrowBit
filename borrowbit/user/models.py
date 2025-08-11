"""
User models for the rental backend application.

This module contains the custom user model and related user management models.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel



phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class OTPVerification(BaseModel):
    """Model to handle OTP verification"""
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    email = models.EmailField()
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'otp_type']),
            models.Index(fields=['phone_number', 'otp_type']),
            models.Index(fields=['expires_at']),
        ]


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    """Custom user model for the rental application."""
    
       
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    # Override username field to use email instead
    username = None
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Email Verified At"))
    phone_verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Phone Verified At"))
    
    # Personal information
    first_name = models.CharField(max_length=150, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=150, verbose_name=_("Last Name"))
    prefix = models.CharField(max_length=150, blank=True, verbose_name=_("Prefix"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name=_("Gender"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("Phone Number")
    )
    alternate_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("Alternate Phone Number")
    )
    
    # Address information
    country = models.CharField(
        max_length=100, 
        verbose_name=_("Country")
    )
    state = models.CharField(
        max_length=100, 
        verbose_name=_("State")
    )
    city = models.CharField(
        max_length=100, 
        verbose_name=_("City")
    )
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_("Postal Code"))
    address_line1 = models.TextField(blank=True, verbose_name=_("Address Line 1"))
    address_line2 = models.TextField(blank=True, verbose_name=_("Address Line 2"))
    
    # Business information (for corporate customers)
    company_name = models.CharField(max_length=200, blank=True, verbose_name=_("Company Name"))
    business_registration_number = models.CharField(max_length=100, blank=True, verbose_name=_("Business Registration Number"))
    tax_id = models.CharField(max_length=100, blank=True, verbose_name=_("Tax ID"))
    
    # Preferences and settings
    language = models.CharField(max_length=10, default='en', verbose_name=_("Language"))
    timezone = models.CharField(max_length=50, default='Asia/Kolkata', verbose_name=_("Timezone"))
    currency = models.CharField(max_length=3, default='INR', verbose_name=_("Currency"))
    
    # Security and privacy
    two_factor_enabled = models.BooleanField(default=False, verbose_name=_("Two Factor Enabled"))
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Last Login IP"))
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name=_("Failed Login Attempts"))
    account_locked_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Account Locked Until"))
    
    # Marketing and communication
    marketing_emails = models.BooleanField(default=True, verbose_name=_("Marketing Emails"))
    sms_notifications = models.BooleanField(default=True, verbose_name=_("SMS Notifications"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Push Notifications"))
    
    # Social media integration
    facebook_id = models.CharField(max_length=100, blank=True, verbose_name=_("Facebook ID"))
    google_id = models.CharField(max_length=100, blank=True, verbose_name=_("Google ID"))
    
    # Profile completion
    profile_completion_percentage = models.PositiveIntegerField(default=0, verbose_name=_("Profile Completion Percentage"))
    
    # Override default fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name of the user."""
        return self.first_name
    
    def get_profile_completion_percentage(self):
        """Calculate and return profile completion percentage."""
        fields = [
            'first_name', 'last_name', 'phone_number', 'country', 
            'state', 'city', 'address_line1', 'postal_code'
        ]
        
        completed_fields = sum(1 for field in fields if getattr(self, field))
        total_fields = len(fields)
        
        percentage = int((completed_fields / total_fields) * 100)
        self.profile_completion_percentage = percentage
        self.save(update_fields=['profile_completion_percentage'])
        
        return percentage
    
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock the account for a specified duration."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock the account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def record_failed_login(self):
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def record_successful_login(self, ip_address=None):
        """Record a successful login."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['failed_login_attempts', 'account_locked_until', 'last_login_ip'])
    
    def verify_email(self):
        """Mark email as verified."""
        self.is_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'email_verified_at'])
    
    def verify_phone(self):
        """Mark phone as verified."""
        self.phone_verified_at = timezone.now()
        self.save(update_fields=['phone_verified_at'])
    
    @property
    def is_corporate_customer(self):
        """Check if user is a corporate customer."""
        return bool(self.company_name and self.business_registration_number)
    
    @property
    def is_vip_customer(self):
        """Check if user is a VIP customer based on rental history."""
        # This would be implemented based on business logic
        return False


class UserProfile(BaseModel):
    """Extended user profile information."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name=_("User")
    )
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        verbose_name=_("Profile Picture")
    )
    
    # Additional personal information
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    linkedin_profile = models.URLField(blank=True, verbose_name=_("LinkedIn Profile"))
    
    # Professional information
    occupation = models.CharField(max_length=100, blank=True, verbose_name=_("Occupation"))
    company = models.CharField(max_length=200, blank=True, verbose_name=_("Company"))
    industry = models.CharField(max_length=100, blank=True, verbose_name=_("Industry"))
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name=_("Emergency Contact Name"))
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Emergency Contact Phone"))
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, verbose_name=_("Emergency Contact Relationship"))
    
    # Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('SMS', 'SMS'),
        ],
        default='EMAIL',
        verbose_name=_("Preferred Contact Method")
    )
    
        
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class UserRole(BaseModel):
    """User roles and permissions for the rental system."""
    
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('STAFF', 'Staff'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Administrator'),
        ('SUPER_ADMIN', 'Super Administrator'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='roles',
        verbose_name=_("User")
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_("Role"))
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_roles',
        verbose_name=_("Assigned By")
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Assigned At"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    class Meta:
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")
        unique_together = ['user', 'role']
        ordering = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"
    
    def is_expired(self):
        """Check if the role assignment has expired."""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

class Feature(BaseModel):
    """Model for feature flags to enable/disable features."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Feature Name"))
    is_enabled = models.BooleanField(default=False, verbose_name=_("Is Enabled"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _("Feature")
        verbose_name_plural = _("Features")
    
    def __str__(self):
        return self.name
    
class UserRoleFeaturePermission(BaseModel):
    """Model for managing feature permissions for user roles."""
    
    user_role = models.ForeignKey(
        UserRole, 
        on_delete=models.CASCADE, 
        related_name='feature_permissions',
        verbose_name=_("User Role")
    )
    feature = models.ForeignKey(
        Feature, 
        on_delete=models.CASCADE, 
        related_name='role_permissions',
        verbose_name=_("Feature")
    )
    can_read = models.BooleanField(default=False,verbose_name=_("Can Read"))
    can_write = models.BooleanField(default=False, verbose_name=_("Can Write"))
    can_delete = models.BooleanField(default=False, verbose_name=_("Can Delete"))
    
    is_allowed = models.BooleanField(default=False, verbose_name=_("Is Allowed"))


class AuditLog(BaseModel):
    """Model for tracking audit logs of sensitive operations."""
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PAYMENT', 'Payment'),
        ('RENTAL_CREATE', 'Rental Created'),
        ('RENTAL_UPDATE', 'Rental Updated'),
        ('RENTAL_CANCEL', 'Rental Cancelled'),
        ('PRODUCT_UPDATE', 'Product Updated'),
        ('USER_UPDATE', 'User Updated'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("User")
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name=_("Action"))
    model_name = models.CharField(max_length=100, verbose_name=_("Model Name"))
    object_id = models.CharField(max_length=100, verbose_name=_("Object ID"))
    object_repr = models.TextField(verbose_name=_("Object Representation"))
    changes = models.JSONField(default=dict, blank=True, verbose_name=_("Changes"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    
    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user} on {self.model_name} at {self.created_at}"
