from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Notification, EmailTemplate
from .serializers import (
    NotificationSerializer, NotificationListSerializer, EmailTemplateSerializer,
    SendEmailRequestSerializer, SendTemplateEmailRequestSerializer, NotificationStatsSerializer
)
from .notification_service import NotificationService
from .unified_email_service import unified_email_service
from user.permissions import IsAdminOrReadOnly

logger = logging.getLogger(__name__)

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'category', 'status', 'user']
    search_fields = ['subject', 'message', 'recipient']
    ordering_fields = ['created_at', 'sent_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.request.user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics"""
        queryset = self.get_queryset()
        
        # Basic stats
        total = queryset.count()
        sent = queryset.filter(status='SENT').count()
        failed = queryset.filter(status='FAILED').count()
        pending = queryset.filter(status='PENDING').count()
        retrying = queryset.filter(status='RETRYING').count()
        
        # Stats by category
        by_category = queryset.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Stats by type
        by_type = queryset.values('notification_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Convert to dict format
        category_stats = {item['category']: item['count'] for item in by_category}
        type_stats = {item['notification_type']: item['count'] for item in by_type}
        
        stats_data = {
            'total_notifications': total,
            'sent_notifications': sent,
            'failed_notifications': failed,
            'pending_notifications': pending,
            'retrying_notifications': retrying,
            'notifications_by_category': category_stats,
            'notifications_by_type': type_stats,
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def retry_failed(self, request):
        """Retry sending failed notifications"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can retry failed notifications'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            stats = unified_email_service.retry_failed_notifications()
            return Response({
                'message': 'Retry completed successfully',
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Failed to retry notifications: {e}")
            return Response(
                {'error': 'Failed to retry notifications'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def retry_single(self, request, pk=None):
        """Retry sending a single failed notification"""
        notification = self.get_object()
        
        if notification.status not in ['FAILED', 'RETRYING']:
            return Response(
                {'error': 'Notification is not in failed or retrying status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not notification.can_retry:
            return Response(
                {'error': 'Maximum retries exceeded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            success = unified_email_service.send_notification_email(notification)
            if success:
                return Response({'message': 'Notification sent successfully'})
            else:
                return Response(
                    {'error': 'Failed to send notification'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Failed to retry notification {notification.id}: {e}")
            return Response(
                {'error': 'Failed to retry notification'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email templates"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'subject']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available template types"""
        types = EmailTemplate.TEMPLATE_TYPE_CHOICES
        return Response([{'value': choice[0], 'label': choice[1]} for choice in types])

class EmailServiceViewSet(viewsets.ViewSet):
    """ViewSet for email service operations"""
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def send_email(self, request):
        """Send a custom email"""
        serializer = SendEmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = unified_email_service.send_email(
                    to_email=serializer.validated_data['to_email'],
                    subject=serializer.validated_data['subject'],
                    html_content=serializer.validated_data['html_content'],
                    text_content=serializer.validated_data.get('text_content', ''),
                    from_email=serializer.validated_data.get('from_email'),
                    from_name=serializer.validated_data.get('from_name')
                )
                
                if result['success']:
                    return Response({
                        'message': 'Email sent successfully',
                        'message_id': result.get('message_id')
                    })
                else:
                    return Response(
                        {'error': result['error']}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                return Response(
                    {'error': 'Failed to send email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_template_email(self, request):
        """Send an email using a template"""
        serializer = SendTemplateEmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = unified_email_service.send_template_email(
                    template_type=serializer.validated_data['template_type'],
                    to_email=serializer.validated_data['to_email'],
                    context=serializer.validated_data.get('context', {}),
                    from_email=serializer.validated_data.get('from_email'),
                    from_name=serializer.validated_data.get('from_name')
                )
                
                if result['success']:
                    return Response({
                        'message': 'Template email sent successfully',
                        'message_id': result.get('message_id')
                    })
                else:
                    return Response(
                        {'error': result['error']}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                logger.error(f"Failed to send template email: {e}")
                return Response(
                    {'error': 'Failed to send template email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """Test email service connection"""
        try:
            # Try to send a test email to a test address
            test_email = "test@example.com"
            result = unified_email_service.send_email(
                to_email=test_email,
                subject="Test Email",
                html_content="<p>This is a test email to verify the email service is working.</p>",
                text_content="This is a test email to verify the email service is working."
            )
            
            if result['success']:
                return Response({
                    'message': 'Email service is working correctly',
                    'details': 'Test email sent successfully (may be blocked by email provider)'
                })
            else:
                return Response({
                    'error': 'Email service test failed',
                    'details': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Email service test failed: {e}")
            return Response(
                {'error': 'Email service test failed', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Convenience views for common notification types
class NotificationActionsViewSet(viewsets.ViewSet):
    """ViewSet for common notification actions"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send_welcome_email(self, request):
        """Send welcome email to current user"""
        try:
            success = NotificationService.send_user_registration_email(request.user)
            if success:
                return Response({'message': 'Welcome email sent successfully'})
            else:
                return Response(
                    {'error': 'Failed to send welcome email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return Response(
                {'error': 'Failed to send welcome email'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_otp_email(self, request):
        """Send OTP email to current user"""
        otp_code = request.data.get('otp_code')
        if not otp_code:
            return Response(
                {'error': 'OTP code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            success = NotificationService.send_otp_email(request.user, otp_code)
            if success:
                return Response({'message': 'OTP email sent successfully'})
            else:
                return Response(
                    {'error': 'Failed to send OTP email'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return Response(
                {'error': 'Failed to send OTP email'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
