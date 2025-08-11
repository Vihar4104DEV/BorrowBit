"""
Views for payment management with role-based access control and caching.

This module contains views for payment processing, checkout sessions, 
payment methods, and webhook handling with enterprise-grade security.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import HttpResponse
import json
import logging

from .models import (
    PaymentMethod, CheckoutSession, Payment, PaymentWebhook, PaymentRefund
)
from .serializers import (
    PaymentMethodSerializer, PaymentMethodListSerializer,
    CheckoutSessionCreateSerializer, CheckoutSessionDetailSerializer, CheckoutSessionListSerializer,
    PaymentCreateSerializer, PaymentDetailSerializer, PaymentListSerializer,
    PaymentRefundCreateSerializer, PaymentRefundDetailSerializer, PaymentRefundListSerializer,
    PaymentWebhookSerializer, UserPaymentSummarySerializer, PaymentAnalyticsSerializer
)
from .permissions import (
    PaymentMethodPermission, PaymentMethodCreatePermission, PaymentMethodUpdatePermission, PaymentMethodDeletePermission,
    CheckoutSessionPermission, CheckoutSessionCreatePermission, CheckoutSessionUpdatePermission,
    PaymentPermission, PaymentCreatePermission, PaymentUpdatePermission,
    PaymentRefundPermission, PaymentRefundCreatePermission, PaymentRefundUpdatePermission,
    PaymentWebhookPermission, PaymentWebhookCreatePermission, PaymentAnalyticsPermission, PaymentBulkActionPermission
)
from user.models import UserRole
from core.utils import (
    success_response, error_response, cache_key_generator, 
    set_cache_data, get_cache_data, delete_cache_data
)

logger = logging.getLogger(__name__)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment method management with role-based access control.
    
    Provides CRUD operations for payment methods with different permission levels:
    - Customers: Can view active payment methods
    - Staff/Managers: Can manage payment methods
    - Admins: Full access to all operations
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method_type', 'provider', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return PaymentMethod.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset
        queryset = PaymentMethod.objects.filter(is_deleted=False)
        
        # Admins and staff can see all payment methods
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Customers can only see active payment methods
        if 'CUSTOMER' in role_names:
            return queryset.filter(is_active=True)
        
        return PaymentMethod.objects.none()
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'list':
            return PaymentMethodListSerializer
        elif self.action == 'retrieve':
            return PaymentMethodSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PaymentMethodSerializer
        return PaymentMethodListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'list':
            permission_classes = [PaymentMethodPermission]
        elif self.action == 'retrieve':
            permission_classes = [PaymentMethodPermission]
        elif self.action == 'create':
            permission_classes = [PaymentMethodCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [PaymentMethodUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [PaymentMethodDeletePermission]
        else:
            permission_classes = [PaymentMethodPermission]
        
        return [permission() for permission in permission_classes]
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def list(self, request, *args, **kwargs):
        """List payment methods with caching."""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve payment method details with caching."""
        payment_method_id = kwargs.get('pk')
        cache_key = cache_key_generator('payment_method_detail', str(payment_method_id))
        
        # Try to get from cache
        cached_data = get_cache_data(cache_key)
        if cached_data:
            return success_response("Payment method retrieved successfully", cached_data)
        
        # Get from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the response
        set_cache_data(cache_key, response.data, timeout=600)  # Cache for 10 minutes
        
        return response
    
    def create(self, request, *args, **kwargs):
        """Create a new payment method."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        payment_method = serializer.save()
        
        # Clear related caches
        self._clear_payment_method_caches(payment_method)
        
        return success_response(
            "Payment method created successfully",
            PaymentMethodSerializer(payment_method, context={'request': request}).data
        )
    
    def update(self, request, *args, **kwargs):
        """Update an existing payment method."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        payment_method = serializer.save()
        
        # Clear related caches
        self._clear_payment_method_caches(payment_method)
        
        return success_response(
            "Payment method updated successfully",
            PaymentMethodSerializer(payment_method, context={'request': request}).data
        )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a payment method."""
        payment_method = self.get_object()
        payment_method.soft_delete()
        
        # Clear related caches
        self._clear_payment_method_caches(payment_method)
        
        return success_response("Payment method deleted successfully")
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active payment methods."""
        cache_key = cache_key_generator('active_payment_methods', 'list')
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return success_response("Active payment methods retrieved successfully", cached_data)
        
        payment_methods = self.get_queryset().filter(is_active=True)
        serializer = PaymentMethodListSerializer(payment_methods, many=True, context={'request': request})
        data = serializer.data
        
        # Cache the response
        set_cache_data(cache_key, data, timeout=300)  # Cache for 5 minutes
        
        return success_response("Active payment methods retrieved successfully", data)
    
    @action(detail=False, methods=['get'])
    def by_provider(self, request):
        """Get payment methods grouped by provider."""
        provider = request.query_params.get('provider')
        if not provider:
            return error_response("Provider parameter is required")
        
        payment_methods = self.get_queryset().filter(provider=provider, is_active=True)
        serializer = PaymentMethodListSerializer(payment_methods, many=True, context={'request': request})
        
        return success_response(f"Payment methods for {provider} retrieved successfully", serializer.data)
    
    def _clear_payment_method_caches(self, payment_method):
        """Clear all caches related to a payment method."""
        # Clear payment method detail cache
        cache_key = cache_key_generator('payment_method_detail', str(payment_method.id))
        delete_cache_data(cache_key)
        
        # Clear active payment methods cache
        cache_key = cache_key_generator('active_payment_methods', 'list')
        delete_cache_data(cache_key)


class CheckoutSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for checkout session management with role-based access control.
    
    Provides CRUD operations for checkout sessions with different permission levels:
    - Customers: Can create and view their own checkout sessions
    - Staff/Managers: Can manage all checkout sessions
    - Admins: Full access to all operations
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'currency']
    search_fields = ['session_id', 'description']
    ordering_fields = ['created_at', 'expires_at', 'amount', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return CheckoutSession.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset
        queryset = CheckoutSession.objects.select_related('user', 'payment_method').filter(is_deleted=False)
        
        # Admins and staff can see all checkout sessions
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Users can only see their own checkout sessions
        return queryset.filter(user=user)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return CheckoutSessionCreateSerializer
        elif self.action == 'list':
            return CheckoutSessionListSerializer
        elif self.action == 'retrieve':
            return CheckoutSessionDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return CheckoutSessionCreateSerializer
        return CheckoutSessionListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'list':
            permission_classes = [CheckoutSessionPermission]
        elif self.action == 'retrieve':
            permission_classes = [CheckoutSessionPermission]
        elif self.action == 'create':
            permission_classes = [CheckoutSessionCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CheckoutSessionUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [CheckoutSessionUpdatePermission]
        else:
            permission_classes = [CheckoutSessionPermission]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create a new checkout session."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        checkout_session = serializer.save()
        
        # Clear related caches
        self._clear_checkout_session_caches(checkout_session)
        
        return success_response(
            "Checkout session created successfully",
            CheckoutSessionDetailSerializer(checkout_session, context={'request': request}).data
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve checkout session details."""
        checkout_session = self.get_object()
        
        # Check if session is expired
        if checkout_session.is_expired() and checkout_session.status == 'PENDING':
            checkout_session.status = 'EXPIRED'
            checkout_session.save(update_fields=['status', 'updated_at'])
        
        serializer = CheckoutSessionDetailSerializer(checkout_session, context={'request': request})
        return success_response("Checkout session retrieved successfully", serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a checkout session."""
        checkout_session = self.get_object()
        
        if checkout_session.status not in ['PENDING', 'PROCESSING']:
            return error_response("Checkout session cannot be cancelled")
        
        checkout_session.mark_as_cancelled()
        
        # Clear related caches
        self._clear_checkout_session_caches(checkout_session)
        
        return success_response("Checkout session cancelled successfully")
    
    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """Extend checkout session expiration."""
        checkout_session = self.get_object()
        
        if checkout_session.status != 'PENDING':
            return error_response("Only pending sessions can be extended")
        
        # Extend by 30 minutes
        checkout_session.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        checkout_session.save(update_fields=['expires_at', 'updated_at'])
        
        # Clear related caches
        self._clear_checkout_session_caches(checkout_session)
        
        return success_response("Checkout session extended successfully")
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Get current user's checkout sessions."""
        sessions = self.get_queryset().filter(user=request.user)
        serializer = CheckoutSessionListSerializer(sessions, many=True, context={'request': request})
        return success_response("Your checkout sessions retrieved successfully", serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending checkout sessions."""
        sessions = self.get_queryset().filter(status='PENDING')
        serializer = CheckoutSessionListSerializer(sessions, many=True, context={'request': request})
        return success_response("Pending checkout sessions retrieved successfully", serializer.data)
    
    def _clear_checkout_session_caches(self, checkout_session):
        """Clear all caches related to a checkout session."""
        # Clear user sessions cache
        cache_key = cache_key_generator('user_checkout_sessions', str(checkout_session.user.id))
        delete_cache_data(cache_key)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment management with role-based access control.
    
    Provides CRUD operations for payments with different permission levels:
    - Customers: Can create and view their own payments
    - Staff/Managers: Can manage all payments
    - Admins: Full access to all operations
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction_type', 'payment_method', 'currency']
    search_fields = ['payment_id', 'description']
    ordering_fields = ['created_at', 'completed_at', 'amount', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Payment.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset
        queryset = Payment.objects.select_related('user', 'payment_method', 'checkout_session').filter(is_deleted=False)
        
        # Admins and staff can see all payments
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Users can only see their own payments
        return queryset.filter(user=user)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentCreateSerializer
        return PaymentListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'list':
            permission_classes = [PaymentPermission]
        elif self.action == 'retrieve':
            permission_classes = [PaymentPermission]
        elif self.action == 'create':
            permission_classes = [PaymentCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [PaymentUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [PaymentUpdatePermission]
        else:
            permission_classes = [PaymentPermission]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create a new payment."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        payment = serializer.save()
        
        # Clear related caches
        self._clear_payment_caches(payment)
        
        return success_response(
            "Payment created successfully",
            PaymentDetailSerializer(payment, context={'request': request}).data
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve payment details."""
        payment = self.get_object()
        serializer = PaymentDetailSerializer(payment, context={'request': request})
        return success_response("Payment retrieved successfully", serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process a payment (simulate payment processing)."""
        payment = self.get_object()
        
        if payment.status != 'PROCESSING':
            return error_response("Payment is not in processing status")
        
        # Simulate payment processing
        try:
            # Simulate successful payment
            payment.mark_as_completed(
                provider_payment_id=f"prov_{payment.payment_id}",
                provider_transaction_id=f"txn_{payment.payment_id}"
            )
            
            # Update checkout session
            payment.checkout_session.mark_as_paid()
            
            # Clear related caches
            self._clear_payment_caches(payment)
            
            return success_response("Payment processed successfully")
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            payment.mark_as_failed(error_code="PROCESSING_ERROR", error_message=str(e))
            return error_response("Payment processing failed")
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get current user's payments."""
        payments = self.get_queryset().filter(user=request.user)
        serializer = PaymentListSerializer(payments, many=True, context={'request': request})
        return success_response("Your payments retrieved successfully", serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get user payment summary."""
        user = request.user
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Determine if user can see all payments or just their own
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            payments_queryset = Payment.objects.filter(is_deleted=False)
        else:
            payments_queryset = Payment.objects.filter(user=user, is_deleted=False)
        
        # Calculate summary
        total_payments = payments_queryset.count()
        total_amount = payments_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        successful_payments = payments_queryset.filter(status='COMPLETED').count()
        failed_payments = payments_queryset.filter(status='FAILED').count()
        pending_payments = payments_queryset.filter(status__in=['PENDING', 'PROCESSING']).count()
        
        # Refunds
        refunds_queryset = PaymentRefund.objects.filter(payment__in=payments_queryset, is_deleted=False)
        total_refunds = refunds_queryset.count()
        refunded_amount = refunds_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        summary_data = {
            'total_payments': total_payments,
            'total_amount': total_amount,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'pending_payments': pending_payments,
            'total_refunds': total_refunds,
            'refunded_amount': refunded_amount,
            'currency': 'INR'
        }
        
        serializer = UserPaymentSummarySerializer(summary_data)
        return success_response("Payment summary retrieved successfully", serializer.data)
    
    def _clear_payment_caches(self, payment):
        """Clear all caches related to a payment."""
        # Clear user payments cache
        cache_key = cache_key_generator('user_payments', str(payment.user.id))
        delete_cache_data(cache_key)
        
        # Clear payment summary cache
        cache_key = cache_key_generator('payment_summary', str(payment.user.id))
        delete_cache_data(cache_key)


class PaymentRefundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment refund management with role-based access control.
    
    Provides CRUD operations for payment refunds with different permission levels:
    - Customers: Can request refunds for their own payments
    - Staff/Managers: Can manage all refunds
    - Admins: Full access to all operations
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'reason', 'payment__transaction_type']
    search_fields = ['refund_id', 'description']
    ordering_fields = ['created_at', 'completed_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return PaymentRefund.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset
        queryset = PaymentRefund.objects.select_related('payment', 'user').filter(is_deleted=False)
        
        # Admins and staff can see all refunds
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Users can only see their own refunds
        return queryset.filter(user=user)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return PaymentRefundCreateSerializer
        elif self.action == 'list':
            return PaymentRefundListSerializer
        elif self.action == 'retrieve':
            return PaymentRefundDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentRefundCreateSerializer
        return PaymentRefundListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'list':
            permission_classes = [PaymentRefundPermission]
        elif self.action == 'retrieve':
            permission_classes = [PaymentRefundPermission]
        elif self.action == 'create':
            permission_classes = [PaymentRefundCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [PaymentRefundUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [PaymentRefundUpdatePermission]
        else:
            permission_classes = [PaymentRefundPermission]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create a new payment refund."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        refund = serializer.save()
        
        # Clear related caches
        self._clear_refund_caches(refund)
        
        return success_response(
            "Refund request created successfully",
            PaymentRefundDetailSerializer(refund, context={'request': request}).data
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve refund details."""
        refund = self.get_object()
        serializer = PaymentRefundDetailSerializer(refund, context={'request': request})
        return success_response("Refund retrieved successfully", serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_refund(self, request, pk=None):
        """Process a refund (simulate refund processing)."""
        refund = self.get_object()
        
        if refund.status != 'PENDING':
            return error_response("Refund is not in pending status")
        
        # Simulate refund processing
        try:
            refund.mark_as_processing()
            
            # Simulate successful refund
            refund.mark_as_completed(provider_refund_id=f"ref_{refund.refund_id}")
            
            # Clear related caches
            self._clear_refund_caches(refund)
            
            return success_response("Refund processed successfully")
            
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            refund.mark_as_failed(error_code="PROCESSING_ERROR", error_message=str(e))
            return error_response("Refund processing failed")
    
    @action(detail=False, methods=['get'])
    def my_refunds(self, request):
        """Get current user's refunds."""
        refunds = self.get_queryset().filter(user=request.user)
        serializer = PaymentRefundListSerializer(refunds, many=True, context={'request': request})
        return success_response("Your refunds retrieved successfully", serializer.data)
    
    def _clear_refund_caches(self, refund):
        """Clear all caches related to a refund."""
        # Clear user refunds cache
        cache_key = cache_key_generator('user_refunds', str(refund.user.id))
        delete_cache_data(cache_key)
        
        # Clear payment summary cache
        cache_key = cache_key_generator('payment_summary', str(refund.user.id))
        delete_cache_data(cache_key)


class PaymentWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for payment webhook management with role-based access control.
    
    Provides read operations for webhooks with admin/staff access only.
    """
    
    queryset = PaymentWebhook.objects.select_related().filter(is_deleted=False)
    serializer_class = PaymentWebhookSerializer
    permission_classes = [PaymentWebhookPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider', 'event_type', 'status']
    search_fields = ['webhook_id', 'event_id']
    ordering_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'], permission_classes=[PaymentWebhookCreatePermission])
    def stripe_webhook(self, request):
        """Handle Stripe webhook events."""
        try:
            # Get webhook payload
            payload = request.body.decode('utf-8')
            signature = request.headers.get('Stripe-Signature', '')
            
            # Create webhook record
            webhook = PaymentWebhook.objects.create(
                provider='STRIPE',
                event_type='PAYMENT_INTENT_SUCCEEDED',  # This would be determined from payload
                event_id='evt_test',  # This would be extracted from payload
                raw_payload=payload,
                headers=dict(request.headers),
                signature=signature
            )
            
            # Process webhook (simplified)
            webhook.mark_as_processed()
            
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Stripe webhook processing failed: {str(e)}")
            return HttpResponse(status=400)
    
    @action(detail=False, methods=['post'], permission_classes=[PaymentWebhookCreatePermission])
    def razorpay_webhook(self, request):
        """Handle Razorpay webhook events."""
        try:
            # Get webhook payload
            payload = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature', '')
            
            # Create webhook record
            webhook = PaymentWebhook.objects.create(
                provider='RAZORPAY',
                event_type='PAYMENT_INTENT_SUCCEEDED',  # This would be determined from payload
                event_id='evt_test',  # This would be extracted from payload
                raw_payload=payload,
                headers=dict(request.headers),
                signature=signature
            )
            
            # Process webhook (simplified)
            webhook.mark_as_processed()
            
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Razorpay webhook processing failed: {str(e)}")
            return HttpResponse(status=400)


class PaymentAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for payment analytics with role-based access control.
    
    Provides analytics endpoints for payment data with admin/staff access only.
    """
    
    permission_classes = [PaymentAnalyticsPermission]
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """Get revenue summary analytics."""
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Base queryset
        payments_queryset = Payment.objects.filter(status='COMPLETED', is_deleted=False)
        
        # Apply date filters if provided
        if start_date:
            payments_queryset = payments_queryset.filter(completed_at__gte=start_date)
        if end_date:
            payments_queryset = payments_queryset.filter(completed_at__lte=end_date)
        
        # Calculate analytics
        total_revenue = payments_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        total_transactions = payments_queryset.count()
        
        # Calculate success rate
        total_attempts = Payment.objects.filter(is_deleted=False).count()
        success_rate = (total_transactions / total_attempts * 100) if total_attempts > 0 else 0
        
        # Calculate average transaction value
        avg_transaction_value = payments_queryset.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        analytics_data = {
            'total_revenue': total_revenue,
            'total_transactions': total_transactions,
            'success_rate': round(success_rate, 2),
            'average_transaction_value': avg_transaction_value,
            'currency': 'INR',
            'period': f"{start_date or 'all'} to {end_date or 'now'}",
            'data_points': []  # This would contain time-series data
        }
        
        serializer = PaymentAnalyticsSerializer(analytics_data)
        return success_response("Revenue summary retrieved successfully", serializer.data)
    
    @action(detail=False, methods=['get'])
    def payment_methods_analytics(self, request):
        """Get payment methods analytics."""
        # Get payment methods usage statistics
        payment_methods_stats = Payment.objects.filter(
            status='COMPLETED', 
            is_deleted=False
        ).values('payment_method__name').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            avg_amount=Avg('total_amount')
        ).order_by('-total_amount')
        
        return success_response("Payment methods analytics retrieved successfully", payment_methods_stats)
    
    @action(detail=False, methods=['get'])
    def transaction_types_analytics(self, request):
        """Get transaction types analytics."""
        # Get transaction types statistics
        transaction_types_stats = Payment.objects.filter(
            status='COMPLETED', 
            is_deleted=False
        ).values('transaction_type').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            avg_amount=Avg('total_amount')
        ).order_by('-total_amount')
        
        return success_response("Transaction types analytics retrieved successfully", transaction_types_stats)
