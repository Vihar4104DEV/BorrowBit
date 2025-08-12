from rest_framework import permissions
from user.models import UserRole


class DeliveryPartnerPermission(permissions.BasePermission):
    """
    Base permission class for DeliveryPartner model.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own profile
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        # Customers can view available delivery partners
        if request.user.role == UserRole.CUSTOMER and request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own profile
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.user == request.user
        
        # Customers can view delivery partner profiles
        if request.user.role == UserRole.CUSTOMER and request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class DeliveryPartnerCreatePermission(permissions.BasePermission):
    """
    Permission class for creating DeliveryPartner.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create delivery partner."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can create delivery partners
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Users can create their own delivery partner profile
        if request.user.role == UserRole.USER:
            return True
        
        return False


class DeliveryPartnerUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating DeliveryPartner.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update delivery partner."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any delivery partner
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own profile
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any delivery partner
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own profile
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.user == request.user
        
        return False


class DeliveryPartnerDeletePermission(permissions.BasePermission):
    """
    Permission class for deleting DeliveryPartner.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to delete delivery partner."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can delete delivery partners
        return request.user.is_staff or request.user.role == UserRole.ADMIN
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to delete the object."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can delete delivery partners
        return request.user.is_staff or request.user.role == UserRole.ADMIN


class DeliveryJobPermission(permissions.BasePermission):
    """
    Base permission class for DeliveryJob model.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        # Customers can access their own jobs
        if request.user.role == UserRole.CUSTOMER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.assigned_partner and obj.assigned_partner.user == request.user
        
        # Customers can access their own jobs
        if request.user.role == UserRole.CUSTOMER:
            return obj.customer == request.user
        
        return False


class DeliveryJobCreatePermission(permissions.BasePermission):
    """
    Permission class for creating DeliveryJob.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create delivery job."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can create jobs
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Customers can create jobs
        if request.user.role == UserRole.CUSTOMER:
            return True
        
        return False


class DeliveryJobUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating DeliveryJob.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update delivery job."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any job
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        # Customers can update their own jobs (limited fields)
        if request.user.role == UserRole.CUSTOMER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any job
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.assigned_partner and obj.assigned_partner.user == request.user
        
        # Customers can update their own jobs (limited fields)
        if request.user.role == UserRole.CUSTOMER:
            return obj.customer == request.user
        
        return False


class DeliveryJobDeletePermission(permissions.BasePermission):
    """
    Permission class for deleting DeliveryJob.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to delete delivery job."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can delete jobs
        return request.user.is_staff or request.user.role == UserRole.ADMIN
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to delete the object."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can delete jobs
        return request.user.is_staff or request.user.role == UserRole.ADMIN


class JobAssignmentPermission(permissions.BasePermission):
    """
    Base permission class for JobAssignment model.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.partner.user == request.user
        
        return False


class JobAssignmentCreatePermission(permissions.BasePermission):
    """
    Permission class for creating JobAssignment.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create job assignment."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can create assignments
        return request.user.is_staff or request.user.role == UserRole.ADMIN


class JobAssignmentUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating JobAssignment.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update job assignment."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any assignment
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any assignment
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.partner.user == request.user
        
        return False


class DeliveryTrackingPermission(permissions.BasePermission):
    """
    Base permission class for DeliveryTracking model.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access tracking for their jobs
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        # Customers can access tracking for their jobs
        if request.user.role == UserRole.CUSTOMER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access tracking for their jobs
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.partner.user == request.user
        
        # Customers can access tracking for their jobs
        if request.user.role == UserRole.CUSTOMER:
            return obj.job.customer == request.user
        
        return False


class DeliveryTrackingCreatePermission(permissions.BasePermission):
    """
    Permission class for creating DeliveryTracking.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create tracking entry."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can create tracking entries
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can create tracking entries for their jobs
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False


class PartnerEarningsPermission(permissions.BasePermission):
    """
    Base permission class for PartnerEarnings model.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their earnings
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins have full access
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own earnings
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.partner.user == request.user
        
        return False


class PartnerEarningsCreatePermission(permissions.BasePermission):
    """
    Permission class for creating PartnerEarnings.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create earnings entry."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can create earnings entries
        return request.user.is_staff or request.user.role == UserRole.ADMIN


class PartnerEarningsUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating PartnerEarnings.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update earnings entry."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can update earnings entries
        return request.user.is_staff or request.user.role == UserRole.ADMIN
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can update earnings entries
        return request.user.is_staff or request.user.role == UserRole.ADMIN


class DeliveryPartnerDashboardPermission(permissions.BasePermission):
    """
    Permission class for delivery partner dashboard.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access dashboard."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can access any dashboard
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own dashboard
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False


class DeliveryPartnerLocationUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating delivery partner location.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update location."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any partner's location
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own location
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any partner's location
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own location
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.user == request.user
        
        return False


class DeliveryPartnerAvailabilityUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating delivery partner availability.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update availability."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any partner's availability
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own availability
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any partner's availability
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update their own availability
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.user == request.user
        
        return False


class DeliveryJobStatusUpdatePermission(permissions.BasePermission):
    """
    Permission class for updating delivery job status.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to update job status."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any job status
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update status of jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to update the object."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can update any job status
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can update status of jobs assigned to them
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.assigned_partner and obj.assigned_partner.user == request.user
        
        return False


class JobAssignmentResponsePermission(permissions.BasePermission):
    """
    Permission class for responding to job assignments.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to respond to assignments."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can respond to any assignment
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can respond to their assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to respond to the assignment."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can respond to any assignment
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can respond to their assignments
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return obj.partner.user == request.user
        
        return False


class DeliveryPartnerAnalyticsPermission(permissions.BasePermission):
    """
    Permission class for delivery partner analytics.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access analytics."""
        if not request.user.is_authenticated:
            return False
        
        # Staff and admins can access any analytics
        if request.user.is_staff or request.user.role == UserRole.ADMIN:
            return True
        
        # Delivery partners can access their own analytics
        if request.user.role == UserRole.DELIVERY_PARTNER:
            return True
        
        return False


class DeliveryPartnerBulkActionPermission(permissions.BasePermission):
    """
    Permission class for bulk actions on delivery partners.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to perform bulk actions."""
        if not request.user.is_authenticated:
            return False
        
        # Only staff and admins can perform bulk actions
        return request.user.is_staff or request.user.role == UserRole.ADMIN
