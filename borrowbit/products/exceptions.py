"""
Custom exceptions for product management.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class ProductException(Exception):
    """Base exception for product-related errors."""
    pass


class ProductNotFoundError(ProductException):
    """Raised when a product is not found."""
    pass


class ProductNotAvailableError(ProductException):
    """Raised when a product is not available for rental."""
    pass


class ProductQuantityError(ProductException):
    """Raised when there's an issue with product quantity."""
    pass


class ProductApprovalError(ProductException):
    """Raised when there's an issue with product approval."""
    pass


class ProductPricingError(ProductException):
    """Raised when there's an issue with product pricing."""
    pass


class ProductReviewError(ProductException):
    """Raised when there's an issue with product reviews."""
    pass


class ProductMaintenanceError(ProductException):
    """Raised when there's an issue with product maintenance."""
    pass


class ProductCategoryError(ProductException):
    """Raised when there's an issue with product categories."""
    pass


class ProductPermissionError(ProductException):
    """Raised when there's a permission issue with products."""
    pass


class ProductBulkActionError(ProductException):
    """Raised when there's an issue with bulk actions."""
    pass


def product_exception_handler(exc, context):
    """
    Custom exception handler for product-related exceptions.
    """
    if isinstance(exc, ProductNotFoundError):
        return Response({
            'success': False,
            'message': _('Product not found.'),
            'error_code': 'PRODUCT_NOT_FOUND',
            'data': {}
        }, status=status.HTTP_404_NOT_FOUND)
    
    elif isinstance(exc, ProductNotAvailableError):
        return Response({
            'success': False,
            'message': _('Product is not available for rental.'),
            'error_code': 'PRODUCT_NOT_AVAILABLE',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductQuantityError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_QUANTITY_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductApprovalError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_APPROVAL_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductPricingError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_PRICING_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductReviewError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_REVIEW_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductMaintenanceError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_MAINTENANCE_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductCategoryError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_CATEGORY_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, ProductPermissionError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_PERMISSION_ERROR',
            'data': {}
        }, status=status.HTTP_403_FORBIDDEN)
    
    elif isinstance(exc, ProductBulkActionError):
        return Response({
            'success': False,
            'message': str(exc),
            'error_code': 'PRODUCT_BULK_ACTION_ERROR',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Call the default exception handler for other exceptions
    return exception_handler(exc, context)
    