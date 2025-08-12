"""
Permission classes for product management with role-based access control.
"""
from rest_framework import permissions
from django.utils.translation import gettext_lazy as _
from user.models import UserRole


class ProductPermissionMixin:
    """Mixin for product-related permissions."""
    
    def _get_user_roles(self, user):
        """Get user's active roles."""
        if not user.is_authenticated:
            return []
        
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        return [role.role for role in user_roles]
    
    def _has_role(self, user, required_roles):
        """Check if user has any of the required roles."""
        user_roles = self._get_user_roles(user)
        return any(role in user_roles for role in required_roles)
    
    def _is_admin(self, user):
        """Check if user is admin or super admin."""
        return self._has_role(user, ['ADMIN', 'SUPER_ADMIN'])
    
    def _is_staff(self, user):
        """Check if user is staff or manager."""
        return self._has_role(user, ['STAFF', 'MANAGER'])
    
    def _is_customer(self, user):
        """Check if user is a customer."""
        return self._has_role(user, ['CUSTOMER'])


class ProductListPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for listing products.
    - All authenticated users can view approved products
    - Staff and admins can view all products
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All authenticated users can list products
        return True


class ProductDetailPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for viewing product details.
    - All authenticated users can view approved products
    - Staff and admins can view all products
    - Product owners can view their own products
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admins and staff can view all products
        if self._is_admin(request.user) or self._is_staff(request.user):
            return True
        
        # Product owners can view their own products
        if obj.owner == request.user:
            return True
        
        # Customers can only view approved products
        if self._is_customer(request.user):
            return obj.admin_approved and obj.is_active
        
        return False


class ProductCreatePermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for creating products.
    - All authenticated users can create products
    - Products need admin approval before being visible to customers
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All authenticated users can create products
        return True


class ProductUpdatePermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for updating products.
    - Product owners can update their own products
    - Staff and admins can update any product
    - Customers cannot update products
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff, admins, and product owners can update
        if self._is_admin(request.user) or self._is_staff(request.user):
            return True
        
        # Customers cannot update products
        if self._is_customer(request.user):
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admins and staff can update any product
        if self._is_admin(request.user) or self._is_staff(request.user):
            return True
        
        # Product owners can update their own products
        if obj.owner == request.user:
            return True
        
        return False


class ProductDeletePermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for deleting products.
    - Only admins can delete products
    - Product owners can soft delete their own products
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins can delete products
        if self._is_admin(request.user):
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Only admins can delete products
        if self._is_admin(request.user):
            return True
        
        return False


class ProductAdminPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for admin-only product operations.
    - Only admins can approve/unapprove, feature/unfeature products
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins can perform admin operations
        return self._is_admin(request.user)
    
    def has_object_permission(self, request, view, obj):
        # Only admins can perform admin operations
        return self._is_admin(request.user)


class ProductBulkActionPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for bulk product actions.
    - Admins can perform all bulk actions
    - Staff can perform most actions except delete
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can perform bulk actions
        return self._is_admin(request.user) or self._is_staff(request.user)


class ProductReviewPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for product reviews.
    - All authenticated users can create reviews
    - Only admins can approve/reject reviews
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # All authenticated users can create reviews
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Review owners can update their own reviews
        if obj.user == request.user:
            return True
        
        # Admins can approve/reject reviews
        if self._is_admin(request.user):
            return True
        
        return False


class ProductMaintenancePermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for product maintenance.
    - Only staff and admins can manage maintenance
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can manage maintenance
        return self._is_admin(request.user) or self._is_staff(request.user)
    
    def has_object_permission(self, request, view, obj):
        # Only staff and admins can manage maintenance
        return self._is_admin(request.user) or self._is_staff(request.user)


class ProductCategoryPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for product categories.
    - All users can view categories
    - Only admins can manage categories
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Only admins can manage categories
        return self._is_admin(request.user)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only admins can manage categories
        return self._is_admin(request.user)


class ProductPricingPermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for product pricing.
    - All users can view pricing
    - Product owners can manage their own product pricing
    - Staff and admins can manage all pricing
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Staff, admins, and product owners can manage pricing
        return self._is_admin(request.user) or self._is_staff(request.user)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admins and staff can manage all pricing
        if self._is_admin(request.user) or self._is_staff(request.user):
            return True
        
        # Product owners can manage their own product pricing
        if obj.product.owner == request.user:
            return True
        
        return False


class ProductImagePermission(permissions.BasePermission, ProductPermissionMixin):
    """
    Permission for product images.
    - All users can view images
    - Product owners can manage their own product images
    - Staff and admins can manage all images
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Staff, admins, and product owners can manage images
        return self._is_admin(request.user) or self._is_staff(request.user)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admins and staff can manage all images
        if self._is_admin(request.user) or self._is_staff(request.user):
            return True
        
        # Product owners can manage their own product images
        if obj.product.owner == request.user:
            return True
        
        return False