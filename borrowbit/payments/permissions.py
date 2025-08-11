"""
Permission classes for payment models with role-based access control.

This module contains permission classes for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade security.
"""
from rest_framework import permissions
from user.models import UserRole


class PaymentMethodPermission(permissions.BasePermission):
    """Base permission for payment methods."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access payment methods."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Admins and staff can access all payment methods
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return True
        
        # Customers can only view active payment methods
        if request.method in permissions.SAFE_METHODS:
            return 'CUSTOMER' in role_names
        
        return False


class PaymentMethodCreatePermission(permissions.BasePermission):
    """Permission for creating payment methods."""
    
    def has_permission(self, request, view):
        """Check if user can create payment methods."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins can create payment methods
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names


class PaymentMethodUpdatePermission(permissions.BasePermission):
    """Permission for updating payment methods."""
    
    def has_permission(self, request, view):
        """Check if user can update payment methods."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins can update payment methods
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names


class PaymentMethodDeletePermission(permissions.BasePermission):
    """Permission for deleting payment methods."""
    
    def has_permission(self, request, view):
        """Check if user can delete payment methods."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only super admins can delete payment methods
        return 'SUPER_ADMIN' in role_names


class CheckoutSessionPermission(permissions.BasePermission):
    """Base permission for checkout sessions."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access checkout sessions."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # All authenticated users can access checkout sessions
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific checkout session."""
        # Users can only access their own checkout sessions
        if obj.user == request.user:
            return True
        
        # Admins and staff can access all checkout sessions
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class CheckoutSessionCreatePermission(permissions.BasePermission):
    """Permission for creating checkout sessions."""
    
    def has_permission(self, request, view):
        """Check if user can create checkout sessions."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Customers and staff can create checkout sessions
        return 'CUSTOMER' in role_names or 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names


class CheckoutSessionUpdatePermission(permissions.BasePermission):
    """Permission for updating checkout sessions."""
    
    def has_permission(self, request, view):
        """Check if user can update checkout sessions."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Staff and admins can update checkout sessions
        return 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names
    
    def has_object_permission(self, request, view, obj):
        """Check if user can update specific checkout session."""
        # Users can update their own checkout sessions if not completed
        if obj.user == request.user and obj.status not in ['COMPLETED', 'FAILED']:
            return True
        
        # Admins and staff can update all checkout sessions
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentPermission(permissions.BasePermission):
    """Base permission for payments."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access payments."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # All authenticated users can access payments
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific payment."""
        # Users can only access their own payments
        if obj.user == request.user:
            return True
        
        # Admins and staff can access all payments
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentCreatePermission(permissions.BasePermission):
    """Permission for creating payments."""
    
    def has_permission(self, request, view):
        """Check if user can create payments."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Customers and staff can create payments
        return 'CUSTOMER' in role_names or 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names


class PaymentUpdatePermission(permissions.BasePermission):
    """Permission for updating payments."""
    
    def has_permission(self, request, view):
        """Check if user can update payments."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Staff and admins can update payments
        return 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names
    
    def has_object_permission(self, request, view, obj):
        """Check if user can update specific payment."""
        # Users can update their own payments if not completed
        if obj.user == request.user and obj.status not in ['COMPLETED', 'FAILED', 'REFUNDED']:
            return True
        
        # Admins and staff can update all payments
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentRefundPermission(permissions.BasePermission):
    """Base permission for payment refunds."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access payment refunds."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # All authenticated users can access refunds
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific refund."""
        # Users can only access their own refunds
        if obj.user == request.user:
            return True
        
        # Admins and staff can access all refunds
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentRefundCreatePermission(permissions.BasePermission):
    """Permission for creating payment refunds."""
    
    def has_permission(self, request, view):
        """Check if user can create payment refunds."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Customers can request refunds for their own payments
        # Staff and admins can create refunds for any payment
        return 'CUSTOMER' in role_names or 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names


class PaymentRefundUpdatePermission(permissions.BasePermission):
    """Permission for updating payment refunds."""
    
    def has_permission(self, request, view):
        """Check if user can update payment refunds."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Staff and admins can update refunds
        return 'STAFF' in role_names or 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names
    
    def has_object_permission(self, request, view, obj):
        """Check if user can update specific refund."""
        # Users can update their own refunds if not completed
        if obj.user == request.user and obj.status not in ['COMPLETED', 'FAILED']:
            return True
        
        # Admins and staff can update all refunds
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentWebhookPermission(permissions.BasePermission):
    """Permission for payment webhooks."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access webhooks."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins and staff can access webhooks
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentWebhookCreatePermission(permissions.BasePermission):
    """Permission for creating webhooks (external providers)."""
    
    def has_permission(self, request, view):
        """Check if webhook can be created (for external providers)."""
        # Allow webhook creation from external providers
        # This should be validated with signature verification
        return True


class PaymentAnalyticsPermission(permissions.BasePermission):
    """Permission for payment analytics."""
    
    def has_permission(self, request, view):
        """Check if user has permission to access payment analytics."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins and staff can access analytics
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names


class PaymentBulkActionPermission(permissions.BasePermission):
    """Permission for bulk payment actions."""
    
    def has_permission(self, request, view):
        """Check if user has permission for bulk actions."""
        if not request.user.is_authenticated:
            return False
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=request.user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins and staff can perform bulk actions
        return 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names

