"""
Views for payment management with role-based access control and optimization.

This module provides comprehensive payment operations including rental order creation,
Stripe checkout sessions, webhook handling, and order management with proper
permission handling and database query optimization.
"""
import stripe
import logging
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

from .models import (
    RentalOrder, RentalOrderItem, Payment, PaymentGateway, 
    PaymentSchedule, PaymentNotification
)
from .serializers import (
    RentalOrderCreateSerializer, RentalOrderDetailSerializer, RentalOrderListSerializer,
    PaymentSerializer, StripeCheckoutSessionSerializer, StripeWebhookSerializer,
    PaymentGatewaySerializer, PaymentScheduleSerializer, PaymentNotificationSerializer
)
# from .permissions import (
#     PaymentListPermission, PaymentDetailPermission, PaymentCreatePermission,
#     PaymentUpdatePermission, PaymentDeletePermission, PaymentAdminPermission
# )
from products.models import Product, ProductPricing
from user.models import UserRole
from core.utils import (
    success_response, error_response, validation_error_response, cache_key_generator,
    set_cache_data, get_cache_data, delete_cache_data
)

# Configure Stripe - will be set dynamically in methods
logger = logging.getLogger(__name__)

# Static Stripe Product ID for rental service
RENTAL_PRODUCT_ID = 'prod_SqnBA4PTShxxKT'  # You can change this ID as needed


class RentalOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for rental order management with role-based access control.
    
    Provides CRUD operations for rental orders with different permission levels:
    - Customers: Can view their own orders, create orders
    - Staff/Managers: Can view all orders, manage orders
    - Admins: Full access to all operations
    
    Features:
    - Role-based access control
    - Cart to order conversion
    - Stripe checkout integration
    - Order status management
    - Inventory management
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'rental_start_date', 'rental_end_date']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'rental_start_date', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset based on user role and permissions with optimization.
        
        Returns:
            QuerySet: Filtered rental orders based on user role and permissions
        """
        user = self.request.user
        
        if not user.is_authenticated:
            return RentalOrder.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset with optimized select_related and prefetch_related
        queryset = RentalOrder.objects.select_related(
            'customer'
        ).prefetch_related(
            Prefetch('items', queryset=RentalOrderItem.objects.select_related('product')),
            Prefetch('payments', queryset=Payment.objects.select_related('gateway')),
            'items__product__category'
        ).filter(is_deleted=False)
        
        # Admin and Super Admin can see all orders
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return queryset
        
        # Staff and Manager can see all orders
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            return queryset
        
        # Customers can only see their own orders
        if 'CUSTOMER' in role_names:
            return queryset.filter(customer=user)
        
        return RentalOrder.objects.none()
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'create':
            return RentalOrderCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return RentalOrderDetailSerializer
        else:
            return RentalOrderListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated] # This Permission is For Only Admin Currently IsAuthenticated For Dev Purpose.
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated] # This Permission is For Only Admin Currently IsAuthenticated For Dev Purpose.
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated] # This Permission is For Only Admin Currently IsAuthenticated For Dev Purpose.
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """
        Create rental order from cart items with direct order processing.
        
        This method bypasses payment gateway integration and processes the order directly,
        handling all the necessary steps including inventory management and notifications.
        """
        try:
            # Validate the request data
            serializer = RentalOrderCreateSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            
            data = serializer.validated_data
            cart_items = data['cart_items']
            rental_start_date = data['rental_start_date']
            rental_end_date = data['rental_end_date']
            notes = data.get('notes', '')
            
            # Validate dates
            if rental_start_date >= rental_end_date:
                return error_response(
                    "Rental end date must be after start date",
                    status.HTTP_400_BAD_REQUEST
                )
            
            if rental_start_date < timezone.now():
                return error_response(
                    "Rental start date cannot be in the past",
                    status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Create rental order
                order = RentalOrder.objects.create(
                    customer=request.user,
                    rental_start_date=rental_start_date,
                    rental_end_date=rental_end_date,
                    notes=notes,
                    status='DRAFT'
                )
                
                # Calculate rental duration in hours
                duration = (rental_end_date - rental_start_date).total_seconds() / 3600
                
                subtotal = Decimal('0.00')
                deposit_total = Decimal('0.00')
                
                # Validate and create order items
                for item_data in cart_items:
                    try:
                        product = Product.objects.get(id=item_data['product_id'])
                    except Product.DoesNotExist:
                        raise ValidationError(f"Product with ID {item_data['product_id']} does not exist")
                    
                    quantity = item_data['quantity']
                    
                    # Validate quantity
                    if quantity <= 0:
                        raise ValidationError(f"Invalid quantity for product {product.name}")
                    
                    if not product.is_available_quantity(quantity):
                        raise ValidationError(f"Insufficient quantity available for {product.name}")
                    
                    # Get pricing for the product
                    pricing = product.pricing_rules.filter(
                        customer_type='REGULAR',
                        duration_type='HOURLY'
                    ).first()
                    
                    if not pricing:
                        unit_price = product.deposit_amount * Decimal('0.1')  # 10% of deposit as hourly rate
                    else:
                        unit_price = pricing.price_per_unit
                    
                    # Calculate total price for this item
                    item_total = unit_price * Decimal(str(duration)) * quantity
                    subtotal += item_total
                    deposit_total += product.deposit_amount * quantity
                    
                    # Create order item
                    RentalOrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=item_total,
                        deposit_per_unit=product.deposit_amount
                    )
                    
                    # Reserve the quantity
                    product.reserve_quantity(quantity)
                
                # Calculate tax and totals
                tax_rate = Decimal('0.085')  # 8.5% tax rate
                tax_amount = subtotal * tax_rate
                
                # Update order totals
                order.subtotal = subtotal
                order.tax_amount = tax_amount
                order.deposit_amount = deposit_total
                order.total_amount = subtotal + tax_amount + deposit_total
                
                # Update order status directly (bypassing payment process)
                order.status = 'CONFIRMED'
                order.save()
                
                # Create payment record (marked as completed)
                gateway, _ = PaymentGateway.objects.get_or_create(
                    gateway_type='INTERNAL',
                    defaults={
                        'name': 'Internal Payment Processing',
                        'is_active': True,
                        'is_test_mode': settings.DEBUG
                    }
                )
                
                payment = Payment.objects.create(
                    order=order,
                    payment_type='FULL_UPFRONT',
                    amount=order.total_amount,
                    gateway=gateway,
                    status='COMPLETED',
                    payment_date=timezone.now(),
                    gateway_response={
                        'processed_at': timezone.now().isoformat(),
                        'internal_reference': f"INT-{order.order_number}"
                    }
                )
                
                # Create payment notification
                try:
                    PaymentNotification.objects.create(
                        order=order,
                        notification_type='PAYMENT_CONFIRMED',
                        subject=f'Order Confirmed - {order.order_number}',
                        message=f'Your order {order.order_number} has been confirmed. Total amount: ${order.total_amount}',
                        scheduled_for=timezone.now(),
                        is_sent=True,
                        sent_at=timezone.now()
                    )
                except Exception as notification_error:
                    logger.error(f"Error creating notification: {str(notification_error)}")
                    # Continue processing as this is not critical
                
                # Clear any cached data
                cache_key = cache_key_generator('user_orders', str(request.user.id))
                delete_cache_data(cache_key)
                
                return success_response(
                    "Order created and confirmed successfully",
                    {
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'total_amount': str(order.total_amount),
                        'status': order.status,
                        'payment_reference': payment.payment_id
                    }
                )
                
        except ValidationError as validation_error:
            logger.error(f"Validation error: {str(validation_error)}")
            return error_response(
                str(validation_error),
                status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}")
            return error_response(
                "An error occurred while processing your order. Please try again.",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel a rental order and release reserved quantities."""
        try:
            order = self.get_object()
            
            if order.status not in ['DRAFT', 'CONFIRMED']:
                return error_response(
                    "Order cannot be cancelled in its current status",
                    status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Release reserved quantities
                for item in order.items.all():
                    item.product.release_reservation(item.quantity)
                
                # Update order status
                order.status = 'CANCELLED'
                order.save()
                
                # Cancel any pending payments
                pending_payments = order.payments.filter(status='PENDING')
                for payment in pending_payments:
                    payment.status = 'FAILED'
                    payment.notes = 'Order cancelled by customer'
                    payment.save()
                
                # Clear cache
                cache_key = cache_key_generator('user_orders', str(request.user.id))
                delete_cache_data(cache_key)
                
                return success_response("Order cancelled successfully")
                
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return error_response(
                f"Error cancelling order: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get orders for the current user with caching."""
        try:
            cache_key = cache_key_generator('user_orders', str(request.user.id))
            cached_orders = get_cache_data(cache_key)
            
            if cached_orders is not None:
                return success_response("Orders retrieved from cache", cached_orders)
            
            orders = self.get_queryset().filter(customer=request.user)
            serializer = RentalOrderListSerializer(orders, many=True, context={'request': request})
            
            # Cache the results for 5 minutes
            set_cache_data(cache_key, serializer.data, timeout=300)
            
            return success_response("Orders retrieved successfully", serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving user orders: {str(e)}")
            return error_response(
                f"Error retrieving orders: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment management with role-based access control.
    
    Provides CRUD operations for payments with different permission levels:
    - Customers: Can view their own payments
    - Staff/Managers: Can view all payments, manage payments
    - Admins: Full access to all operations
    """
    
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'gateway', 'order']
    search_fields = ['payment_id', 'gateway_transaction_id', 'order__order_number']
    ordering_fields = ['created_at', 'amount', 'payment_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Payment.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset with optimization
        queryset = Payment.objects.select_related(
            'order', 'gateway'
        ).filter(is_deleted=False)
        
        # Admin and Super Admin can see all payments
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return queryset
        
        # Staff and Manager can see all payments
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            return queryset
        
        # Customers can only see their own payments
        if 'CUSTOMER' in role_names:
            return queryset.filter(order__customer=user)
        
        return Payment.objects.none()
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [PaymentListPermission]
        elif self.action == 'create':
            permission_classes = [PaymentCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [PaymentUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [PaymentDeletePermission]
        else:
            permission_classes = [PaymentAdminPermission]
        
        return [permission() for permission in permission_classes]


class StripeWebhookView(View):
    """
    Handle Stripe webhooks for payment status updates.
    
    This view processes Stripe webhook events to update payment statuses,
    manage inventory, and handle order status changes.
    """
    
    @method_decorator(csrf_exempt)
    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Process Stripe webhook events."""
        try:
            # Check if Stripe webhook secret is configured
            if not settings.STRIPE_WEBHOOK_SECRET:
                logger.error("Stripe webhook secret is not configured")
                return HttpResponse(status=500)
            
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            
            if not sig_header:
                logger.error("Missing Stripe signature header")
                return HttpResponse(status=400)
            
            # Verify webhook signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
            except ValueError as e:
                logger.error(f"Invalid payload: {e}")
                return HttpResponse(status=400)
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid signature: {e}")
                return HttpResponse(status=400)
            
            # Handle the event
            if event['type'] == 'checkout.session.completed':
                return self.handle_checkout_session_completed(event)
            elif event['type'] == 'payment_intent.succeeded':
                return self.handle_payment_intent_succeeded(event)
            elif event['type'] == 'payment_intent.payment_failed':
                return self.handle_payment_intent_failed(event)
            elif event['type'] == 'charge.refunded':
                return self.handle_charge_refunded(event)
            else:
                logger.info(f"Unhandled event type: {event['type']}")
            
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return HttpResponse(status=500)
    
    def handle_checkout_session_completed(self, event):
        """Handle successful checkout session completion."""
        try:
            session = event['data']['object']
            order_id = session['metadata']['order_id']
            payment_id = session['metadata']['payment_id']
            
            with transaction.atomic():
                # Get the order and payment
                order = RentalOrder.objects.get(id=order_id)
                payment = Payment.objects.get(payment_id=payment_id)
                
                # Update payment status
                payment.status = 'COMPLETED'
                payment.payment_date = timezone.now()
                payment.gateway_response.update({
                    'webhook_received': True,
                    'webhook_type': 'checkout.session.completed'
                })
                payment.save()
                
                # Update order status
                order.status = 'CONFIRMED'
                order.save()
                
                # Create payment schedule for future payments if needed
                self.create_payment_schedule(order)
                
                # Send confirmation notification
                self.send_payment_confirmation_notification(order)
                
                # Clear cache
                cache_key = cache_key_generator('user_orders', str(order.customer.id))
                delete_cache_data(cache_key)
                
                logger.info(f"Order {order.order_number} confirmed and payment completed")
                
        except Exception as e:
            logger.error(f"Error handling checkout session completed: {str(e)}")
            raise
        
        return HttpResponse(status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """Handle successful payment intent."""
        try:
            payment_intent = event['data']['object']
            session_id = payment_intent.get('metadata', {}).get('session_id')
            
            if session_id:
                # Find payment by session ID
                payment = Payment.objects.get(gateway_transaction_id=session_id)
                payment.status = 'COMPLETED'
                payment.payment_date = timezone.now()
                payment.save()
                
                logger.info(f"Payment {payment.payment_id} completed via payment intent")
            
        except Exception as e:
            logger.error(f"Error handling payment intent succeeded: {str(e)}")
        
        return HttpResponse(status=200)
    
    def handle_payment_intent_failed(self, event):
        """Handle failed payment intent."""
        try:
            payment_intent = event['data']['object']
            session_id = payment_intent.get('metadata', {}).get('session_id')
            
            if session_id:
                # Find payment by session ID
                payment = Payment.objects.get(gateway_transaction_id=session_id)
                payment.status = 'FAILED'
                payment.notes = f"Payment failed: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
                payment.save()
                
                # Release reserved quantities
                order = payment.order
                for item in order.items.all():
                    item.product.release_reservation(item.quantity)
                
                logger.info(f"Payment {payment.payment_id} failed")
            
        except Exception as e:
            logger.error(f"Error handling payment intent failed: {str(e)}")
        
        return HttpResponse(status=200)
    
    def handle_charge_refunded(self, event):
        """Handle charge refunds."""
        try:
            charge = event['data']['object']
            session_id = charge.get('metadata', {}).get('session_id')
            
            if session_id:
                # Find payment by session ID
                payment = Payment.objects.get(gateway_transaction_id=session_id)
                payment.status = 'REFUNDED'
                payment.notes = f"Payment refunded: {charge.get('reason', 'Unknown reason')}"
                payment.save()
                
                # Update order status
                order = payment.order
                order.status = 'CANCELLED'
                order.save()
                
                # Release reserved quantities
                for item in order.items.all():
                    item.product.release_reservation(item.quantity)
                
                logger.info(f"Payment {payment.payment_id} refunded")
            
        except Exception as e:
            logger.error(f"Error handling charge refunded: {str(e)}")
        
        return HttpResponse(status=200)
    
    def create_payment_schedule(self, order):
        """Create payment schedule for the order if needed."""
        try:
            # For now, we only handle one-time payments
            # Future enhancement: Add support for installment payments
            pass
        except Exception as e:
            logger.error(f"Error creating payment schedule: {str(e)}")
    
    def send_payment_confirmation_notification(self, order):
        """Send payment confirmation notification."""
        try:
            # Create notification record
            PaymentNotification.objects.create(
                order=order,
                notification_type='PAYMENT_CONFIRMED',
                subject=f'Payment Confirmed - Order {order.order_number}',
                message=f'Your payment of ${order.total_amount} has been confirmed for order {order.order_number}.',
                scheduled_for=timezone.now(),
                is_sent=True,
                sent_at=timezone.now()
            )
            
            # TODO: Send actual email/SMS notification
            logger.info(f"Payment confirmation notification created for order {order.order_number}")
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation notification: {str(e)}")


class PaymentGatewayViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment gateways (read-only)."""
    
    queryset = PaymentGateway.objects.filter(is_active=True, is_deleted=False)
    serializer_class = PaymentGatewaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gateway_type', 'is_test_mode']


class PaymentScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment schedules (read-only)."""
    
    serializer_class = PaymentScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'payment_type', 'is_paid']
    ordering_fields = ['due_date', 'amount']
    ordering = ['due_date']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return PaymentSchedule.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset with optimization
        queryset = PaymentSchedule.objects.select_related(
            'order', 'payment'
        ).filter(is_deleted=False)
        
        # Admin and Super Admin can see all schedules
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return queryset
        
        # Staff and Manager can see all schedules
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            return queryset
        
        # Customers can only see their own schedules
        if 'CUSTOMER' in role_names:
            return queryset.filter(order__customer=user)
        
        return PaymentSchedule.objects.none()


class PaymentNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment notifications (read-only)."""
    
    serializer_class = PaymentNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'notification_type', 'is_sent']
    ordering_fields = ['scheduled_for', 'sent_at']
    ordering = ['-scheduled_for']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return PaymentNotification.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset with optimization
        queryset = PaymentNotification.objects.select_related(
            'order'
        ).filter(is_deleted=False)
        
        # Admin and Super Admin can see all notifications
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return queryset
        
        # Staff and Manager can see all notifications
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            return queryset
        
        # Customers can only see their own notifications
        if 'CUSTOMER' in role_names:
            return queryset.filter(order__customer=user)
        
        return PaymentNotification.objects.none()


class PaymentSuccessView(View):
    """Handle successful payment redirects."""
    
    def get(self, request, *args, **kwargs):
        """Handle successful payment redirect."""
        # Check if Stripe is properly configured
        if not settings.STRIPE_SECRET_KEY:
            logger.error("Stripe secret key is not configured")
            return JsonResponse({
                'success': False,
                'message': 'Payment gateway is not properly configured'
            }, status=500)
        
        session_id = request.GET.get('session_id')
        
        if session_id:
            try:
                # Verify the session with Stripe
                session = stripe.checkout.Session.retrieve(session_id)
                
                if session.payment_status == 'paid':
                    return JsonResponse({
                        'success': True,
                        'message': 'Payment completed successfully!',
                        'session_id': session_id
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Payment not completed'
                    }, status=400)
                    
            except stripe.error.StripeError as e:
                logger.error(f"Error verifying Stripe session: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error verifying payment'
                }, status=500)
        
        return JsonResponse({
            'success': False,
            'message': 'No session ID provided'
        }, status=400)


class PaymentCancelView(View):
    """Handle cancelled payment redirects."""
    
    def get(self, request, *args, **kwargs):
        """Handle cancelled payment redirect."""
        order_id = request.GET.get('order_id')
        
        if order_id:
            try:
                # Get the order and update status if needed
                order = RentalOrder.objects.get(id=order_id, customer=request.user)
                
                if order.status == 'DRAFT':
                    # Release reserved quantities
                    with transaction.atomic():
                        for item in order.items.all():
                            item.product.release_reservation(item.quantity)
                        
                        order.status = 'CANCELLED'
                        order.save()
                        
                        # Cancel pending payments
                        pending_payments = order.payments.filter(status='PENDING')
                        for payment in pending_payments:
                            payment.status = 'FAILED'
                            payment.notes = 'Payment cancelled by customer'
                            payment.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Order cancelled successfully',
                        'order_id': str(order_id)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Order cannot be cancelled'
                    }, status=400)
                    
            except RentalOrder.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Order not found'
                }, status=404)
            except Exception as e:
                logger.error(f"Error cancelling order: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error cancelling order'
                }, status=500)
        
        return JsonResponse({
            'success': False,
            'message': 'No order ID provided'
        }, status=400)
