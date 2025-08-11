from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification, UserProfile, UserRole, Feature, UserRoleFeaturePermission, AuditLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'gender', 'country', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'middle_name', 'gender', 'date_of_birth')}),
        ('Contact Information', {'fields': ('phone_number', 'alternate_phone', 'country', 'state', 'city', 'postal_code', 'address_line1', 'address_line2')}),
        ('Business Information', {'fields': ('company_name', 'business_registration_number', 'tax_id')}),
        ('Preferences', {'fields': ('language', 'timezone', 'currency')}),
        ('Security', {'fields': ('two_factor_enabled', 'last_login_ip', 'failed_login_attempts', 'account_locked_until')}),
        ('Communication', {'fields': ('marketing_emails', 'sms_notifications', 'push_notifications')}),
        ('Social Media', {'fields': ('facebook_id', 'google_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number'),
        }),
    )

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """Admin configuration for OTPVerification model."""
    list_display = ('user', 'email', 'phone_number', 'otp_type', 'is_verified', 'expires_at', 'created_at')
    list_filter = ('otp_type', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'email', 'phone_number')
    ordering = ('-created_at',)
    
    readonly_fields = ('otp', 'created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = ('user', 'occupation', 'company', 'industry', 'preferred_contact_method')
    list_filter = ('industry', 'preferred_contact_method')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'occupation', 'company')
    ordering = ('user__first_name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin configuration for UserRole model."""
    list_display = ('user', 'role', 'assigned_by', 'assigned_at', 'expires_at', 'is_active')
    list_filter = ('role', 'is_active', 'assigned_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'role')
    ordering = ('user__first_name', 'role')

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Admin configuration for Feature model."""
    list_display = ('name', 'is_enabled', 'created_by', 'created_at')
    list_filter = ('is_enabled', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(UserRoleFeaturePermission)
class UserRoleFeaturePermissionAdmin(admin.ModelAdmin):
    """Admin configuration for UserRoleFeaturePermission model."""
    list_display = ('user_role', 'feature', 'can_read', 'can_write', 'can_delete', 'is_allowed')
    list_filter = ('can_read', 'can_write', 'can_delete', 'is_allowed')
    search_fields = ('user_role__user__email', 'feature__name')
    ordering = ('user_role__user__first_name', 'feature__name')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    list_display = ('user', 'action', 'model_name', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__email', 'action', 'model_name', 'object_id')
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Audit logs should not be manually created."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs should not be modified."""
        return False
