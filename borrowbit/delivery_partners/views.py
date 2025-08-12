from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction

from .models import (
    DeliveryPartner, DeliveryJob, JobAssignment, 
    DeliveryTracking, PartnerEarnings
)
from .serializers import (
    DeliveryPartnerSerializer, DeliveryPartnerListSerializer, DeliveryPartnerCreateSerializer,
    DeliveryJobSerializer, DeliveryJobListSerializer, DeliveryJobCreateSerializer,
    JobAssignmentSerializer, JobAssignmentCreateSerializer,
    DeliveryTrackingSerializer, PartnerEarningsSerializer, PartnerEarningsListSerializer,
    DeliveryPartnerDashboardSerializer, DeliveryJobStatusUpdateSerializer,
    JobAssignmentResponseSerializer, DeliveryPartnerLocationUpdateSerializer,
    DeliveryPartnerAvailabilitySerializer
)
from .permissions import (
    DeliveryPartnerPermission, DeliveryPartnerCreatePermission, DeliveryPartnerUpdatePermission,
    DeliveryPartnerDeletePermission, DeliveryJobPermission, DeliveryJobCreatePermission,
    DeliveryJobUpdatePermission, DeliveryJobDeletePermission, JobAssignmentPermission,
    JobAssignmentCreatePermission, JobAssignmentUpdatePermission, DeliveryTrackingPermission,
    DeliveryTrackingCreatePermission, PartnerEarningsPermission, PartnerEarningsCreatePermission,
    PartnerEarningsUpdatePermission, DeliveryPartnerDashboardPermission,
    DeliveryPartnerLocationUpdatePermission, DeliveryPartnerAvailabilityUpdatePermission,
    DeliveryJobStatusUpdatePermission, JobAssignmentResponsePermission
)
from core.utils import success_response, error_response, cache_key_generator, set_cache_data, get_cache_data, delete_cache_data


class DeliveryPartnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryPartner model.
    """
    queryset = DeliveryPartner.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'partner_type', 'vehicle_type', 'city', 'state', 'is_available']
    search_fields = ['partner_code', 'user__first_name', 'user__last_name', 'user__email', 'phone_number']
    ordering_fields = ['rating', 'total_deliveries', 'successful_deliveries', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.role == 'ADMIN':
            return queryset
        
        if self.request.user.role == 'DELIVERY_PARTNER':
            return queryset.filter(user=self.request.user)
        
        # For customers, show only active and available partners
        if self.request.user.role == 'CUSTOMER':
            return queryset.filter(status='active', is_available=True)
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return DeliveryPartnerListSerializer
        elif self.action == 'create':
            return DeliveryPartnerCreateSerializer
        return DeliveryPartnerSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action == 'create':
            permission_classes = [DeliveryPartnerCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [DeliveryPartnerUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [DeliveryPartnerDeletePermission]
        else:
            permission_classes = [DeliveryPartnerPermission]
        
        return [permission() for permission in permission_classes]
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List delivery partners with caching."""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def retrieve(self, request, *args, **kwargs):
        """Retrieve delivery partner with caching."""
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create delivery partner and clear caches."""
        response = super().create(request, *args, **kwargs)
        self._clear_partner_caches()
        return response
    
    def update(self, request, *args, **kwargs):
        """Update delivery partner and clear caches."""
        response = super().update(request, *args, **kwargs)
        self._clear_partner_caches()
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Delete delivery partner and clear caches."""
        response = super().destroy(request, *args, **kwargs)
        self._clear_partner_caches()
        return response
    
    def _clear_partner_caches(self):
        """Clear delivery partner related caches."""
        cache_keys = [
            'delivery_partners_list',
            'delivery_partners_active',
            'delivery_partners_available',
        ]
        for key in cache_keys:
            delete_cache_data(key)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active delivery partners."""
        cache_key = cache_key_generator('delivery_partners_active', request.query_params)
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset().filter(status='active', is_available=True)
        serializer = DeliveryPartnerListSerializer(queryset, many=True)
        
        response_data = success_response(
            message="Active delivery partners retrieved successfully",
            data=serializer.data
        )
        set_cache_data(cache_key, response_data, timeout=300)  # 5 minutes
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available delivery partners."""
        cache_key = cache_key_generator('delivery_partners_available', request.query_params)
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset().filter(
            status='active', 
            is_available=True
        ).filter(
            Q(available_from__isnull=True) | 
            Q(available_to__isnull=True) |
            Q(available_from__lte=timezone.now().time()) & Q(available_to__gte=timezone.now().time())
        )
        
        serializer = DeliveryPartnerListSerializer(queryset, many=True)
        
        response_data = success_response(
            message="Available delivery partners retrieved successfully",
            data=serializer.data
        )
        set_cache_data(cache_key, response_data, timeout=300)  # 5 minutes
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update delivery partner location."""
        partner = self.get_object()
        serializer = DeliveryPartnerLocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            
            partner.update_location(latitude, longitude)
            
            return Response(success_response(
                message="Location updated successfully",
                data={'latitude': latitude, 'longitude': longitude}
            ))
        
        return Response(error_response(
            message="Invalid location data",
            errors=serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_availability(self, request, pk=None):
        """Update delivery partner availability."""
        partner = self.get_object()
        serializer = DeliveryPartnerAvailabilitySerializer(data=request.data)
        
        if serializer.is_valid():
            for field, value in serializer.validated_data.items():
                setattr(partner, field, value)
            partner.save()
            
            return Response(success_response(
                message="Availability updated successfully",
                data=serializer.data
            ))
        
        return Response(error_response(
            message="Invalid availability data",
            errors=serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get delivery partner dashboard data."""
        partner = self.get_object()
        
        # Get active jobs
        active_jobs = partner.assigned_jobs.filter(
            status__in=['assigned', 'picked_up', 'in_transit']
        )
        
        # Get pending assignments
        pending_assignments = partner.job_assignments.filter(status='pending')
        
        # Get recent earnings
        recent_earnings = partner.earnings.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        # Calculate today's earnings
        today = timezone.now().date()
        today_earnings = partner.earnings.filter(
            earned_date=today,
            status='paid'
        ).aggregate(total=Sum('net_amount'))['total'] or 0
        
        # Calculate total earnings
        total_earnings = partner.earnings.filter(
            status='paid'
        ).aggregate(total=Sum('net_amount'))['total'] or 0
        
        dashboard_data = {
            'partner': DeliveryPartnerSerializer(partner).data,
            'active_jobs': DeliveryJobListSerializer(active_jobs, many=True).data,
            'pending_assignments': JobAssignmentSerializer(pending_assignments, many=True).data,
            'recent_earnings': PartnerEarningsListSerializer(recent_earnings, many=True).data,
            'today_earnings': today_earnings,
            'total_earnings': total_earnings,
            'success_rate': partner.get_success_rate(),
            'total_deliveries': partner.total_deliveries,
            'is_working_now': partner.is_working_now(),
        }
        
        return Response(success_response(
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        ))


class DeliveryJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryJob model.
    """
    queryset = DeliveryJob.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job_type', 'priority', 'is_urgent', 'pickup_city', 'delivery_city']
    search_fields = ['job_id', 'customer_name', 'pickup_address', 'delivery_address', 'tracking_number']
    ordering_fields = ['pickup_date', 'delivery_date', 'total_fare', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.role == 'ADMIN':
            return queryset
        
        if self.request.user.role == 'DELIVERY_PARTNER':
            return queryset.filter(assigned_partner__user=self.request.user)
        
        if self.request.user.role == 'CUSTOMER':
            return queryset.filter(customer=self.request.user)
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return DeliveryJobListSerializer
        elif self.action == 'create':
            return DeliveryJobCreateSerializer
        return DeliveryJobSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action == 'create':
            permission_classes = [DeliveryJobCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [DeliveryJobUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [DeliveryJobDeletePermission]
        else:
            permission_classes = [DeliveryJobPermission]
        
        return [permission() for permission in permission_classes]
    
    @method_decorator(cache_page(60 * 3))  # Cache for 3 minutes
    def list(self, request, *args, **kwargs):
        """List delivery jobs with caching."""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def retrieve(self, request, *args, **kwargs):
        """Retrieve delivery job with caching."""
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create delivery job and clear caches."""
        response = super().create(request, *args, **kwargs)
        self._clear_job_caches()
        return response
    
    def update(self, request, *args, **kwargs):
        """Update delivery job and clear caches."""
        response = super().update(request, *args, **kwargs)
        self._clear_job_caches()
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Delete delivery job and clear caches."""
        response = super().destroy(request, *args, **kwargs)
        self._clear_job_caches()
        return response
    
    def _clear_job_caches(self):
        """Clear delivery job related caches."""
        cache_keys = [
            'delivery_jobs_list',
            'delivery_jobs_pending',
            'delivery_jobs_active',
        ]
        for key in cache_keys:
            delete_cache_data(key)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending delivery jobs."""
        cache_key = cache_key_generator('delivery_jobs_pending', request.query_params)
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset().filter(status='pending')
        serializer = DeliveryJobListSerializer(queryset, many=True)
        
        response_data = success_response(
            message="Pending delivery jobs retrieved successfully",
            data=serializer.data
        )
        set_cache_data(cache_key, response_data, timeout=180)  # 3 minutes
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active delivery jobs."""
        cache_key = cache_key_generator('delivery_jobs_active', request.query_params)
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset().filter(
            status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
        )
        serializer = DeliveryJobListSerializer(queryset, many=True)
        
        response_data = success_response(
            message="Active delivery jobs retrieved successfully",
            data=serializer.data
        )
        set_cache_data(cache_key, response_data, timeout=180)  # 3 minutes
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update delivery job status."""
        job = self.get_object()
        serializer = DeliveryJobStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            reason = serializer.validated_data.get('reason', '')
            latitude = serializer.validated_data.get('latitude')
            longitude = serializer.validated_data.get('longitude')
            location_address = serializer.validated_data.get('location_address', '')
            notes = serializer.validated_data.get('notes', '')
            
            with transaction.atomic():
                # Update job status
                if new_status == 'picked_up':
                    job.mark_as_picked_up()
                elif new_status == 'in_transit':
                    job.mark_as_in_transit()
                elif new_status == 'delivered':
                    job.mark_as_delivered()
                elif new_status == 'failed':
                    job.mark_as_failed(reason)
                else:
                    job.status = new_status
                    job.save(update_fields=['status'])
                
                # Create tracking entry
                if hasattr(request.user, 'delivery_partner'):
                    partner = request.user.delivery_partner
                    tracking_data = {
                        'job': job,
                        'partner': partner,
                        'event_type': f'status_update_{new_status}',
                        'description': f'Job status updated to {new_status}',
                        'latitude': latitude,
                        'longitude': longitude,
                        'location_address': location_address,
                        'additional_data': {
                            'reason': reason,
                            'notes': notes,
                            'updated_by': request.user.id
                        }
                    }
                    DeliveryTracking.objects.create(**tracking_data)
                
                # Update partner location if provided
                if latitude and longitude and hasattr(request.user, 'delivery_partner'):
                    request.user.delivery_partner.update_location(latitude, longitude)
            
            self._clear_job_caches()
            
            return Response(success_response(
                message=f"Job status updated to {new_status} successfully",
                data={'status': new_status, 'job_id': job.job_id}
            ))
        
        return Response(error_response(
            message="Invalid status update data",
            errors=serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_partner(self, request, pk=None):
        """Assign delivery partner to job."""
        job = self.get_object()
        partner_id = request.data.get('partner_id')
        
        if not partner_id:
            return Response(error_response(
                message="Partner ID is required"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
        except DeliveryPartner.DoesNotExist:
            return Response(error_response(
                message="Delivery partner not found"
            ), status=status.HTTP_404_NOT_FOUND)
        
        if not partner.can_accept_job(job):
            return Response(error_response(
                message="Partner cannot accept this job"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            job.assign_to_partner(partner)
            
            # Create job assignment
            JobAssignment.objects.create(
                job=job,
                partner=partner,
                expires_at=timezone.now() + timedelta(minutes=30)
            )
            
            # Create tracking entry
            tracking_data = {
                'job': job,
                'partner': partner,
                'event_type': 'job_assigned',
                'description': f'Job assigned to partner {partner.partner_code}',
                'additional_data': {
                    'assigned_by': request.user.id,
                    'expires_at': timezone.now() + timedelta(minutes=30)
                }
            }
            DeliveryTracking.objects.create(**tracking_data)
        
        self._clear_job_caches()
        
        return Response(success_response(
            message="Partner assigned to job successfully",
            data={'job_id': job.job_id, 'partner_code': partner.partner_code}
        ))


class JobAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobAssignment model.
    """
    queryset = JobAssignment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job__status', 'partner__status']
    search_fields = ['job__job_id', 'partner__partner_code']
    ordering_fields = ['assigned_at', 'expires_at', 'responded_at']
    ordering = ['-assigned_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.role == 'ADMIN':
            return queryset
        
        if self.request.user.role == 'DELIVERY_PARTNER':
            return queryset.filter(partner__user=self.request.user)
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return JobAssignmentCreateSerializer
        return JobAssignmentSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action == 'create':
            permission_classes = [JobAssignmentCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [JobAssignmentUpdatePermission]
        else:
            permission_classes = [JobAssignmentPermission]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to job assignment (accept/reject)."""
        assignment = self.get_object()
        serializer = JobAssignmentResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            
            if action == 'accept':
                estimated_pickup_time = serializer.validated_data.get('estimated_pickup_time')
                estimated_delivery_time = serializer.validated_data.get('estimated_delivery_time')
                partner_notes = serializer.validated_data.get('partner_notes', '')
                
                success = assignment.accept_assignment(
                    estimated_pickup_time=estimated_pickup_time,
                    estimated_delivery_time=estimated_delivery_time,
                    partner_notes=partner_notes
                )
                
                if success:
                    # Create tracking entry
                    tracking_data = {
                        'job': assignment.job,
                        'partner': assignment.partner,
                        'event_type': 'job_accepted',
                        'description': f'Job accepted by partner {assignment.partner.partner_code}',
                        'additional_data': {
                            'estimated_pickup_time': estimated_pickup_time,
                            'estimated_delivery_time': estimated_delivery_time,
                            'partner_notes': partner_notes
                        }
                    }
                    DeliveryTracking.objects.create(**tracking_data)
                    
                    return Response(success_response(
                        message="Job assignment accepted successfully",
                        data={'assignment_id': assignment.id, 'job_id': assignment.job.job_id}
                    ))
                else:
                    return Response(error_response(
                        message="Assignment has expired"
                    ), status=status.HTTP_400_BAD_REQUEST)
            
            elif action == 'reject':
                rejection_reason = serializer.validated_data.get('rejection_reason', '')
                
                success = assignment.reject_assignment(rejection_reason)
                
                if success:
                    # Create tracking entry
                    tracking_data = {
                        'job': assignment.job,
                        'partner': assignment.partner,
                        'event_type': 'job_rejected',
                        'description': f'Job rejected by partner {assignment.partner.partner_code}',
                        'additional_data': {
                            'rejection_reason': rejection_reason
                        }
                    }
                    DeliveryTracking.objects.create(**tracking_data)
                    
                    return Response(success_response(
                        message="Job assignment rejected successfully",
                        data={'assignment_id': assignment.id, 'job_id': assignment.job.job_id}
                    ))
                else:
                    return Response(error_response(
                        message="Assignment has expired"
                    ), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(error_response(
            message="Invalid response data",
            errors=serializer.errors
        ), status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending assignments."""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(success_response(
            message="Pending assignments retrieved successfully",
            data=serializer.data
        ))


class DeliveryTrackingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryTracking model.
    """
    queryset = DeliveryTracking.objects.all()
    serializer_class = DeliveryTrackingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'job__status', 'partner__status']
    search_fields = ['job__job_id', 'partner__partner_code', 'description']
    ordering_fields = ['event_time', 'created_at']
    ordering = ['-event_time']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.role == 'ADMIN':
            return queryset
        
        if self.request.user.role == 'DELIVERY_PARTNER':
            return queryset.filter(partner__user=self.request.user)
        
        if self.request.user.role == 'CUSTOMER':
            return queryset.filter(job__customer=self.request.user)
        
        return queryset.none()
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action == 'create':
            permission_classes = [DeliveryTrackingCreatePermission]
        else:
            permission_classes = [DeliveryTrackingPermission]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def job_tracking(self, request):
        """Get tracking events for a specific job."""
        job_id = request.query_params.get('job_id')
        
        if not job_id:
            return Response(error_response(
                message="Job ID is required"
            ), status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(job__job_id=job_id)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(success_response(
            message="Job tracking events retrieved successfully",
            data=serializer.data
        ))


class PartnerEarningsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PartnerEarnings model.
    """
    queryset = PartnerEarnings.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'earning_type', 'partner__status']
    search_fields = ['partner__partner_code', 'job__job_id']
    ordering_fields = ['earned_date', 'amount', 'created_at']
    ordering = ['-earned_date']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        
        if self.request.user.is_staff or self.request.user.role == 'ADMIN':
            return queryset
        
        if self.request.user.role == 'DELIVERY_PARTNER':
            return queryset.filter(partner__user=self.request.user)
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return PartnerEarningsListSerializer
        return PartnerEarningsSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action == 'create':
            permission_classes = [PartnerEarningsCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [PartnerEarningsUpdatePermission]
        else:
            permission_classes = [PartnerEarningsPermission]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve earnings."""
        earning = self.get_object()
        earning.approve_earning()
        
        return Response(success_response(
            message="Earnings approved successfully",
            data={'earning_id': earning.id, 'status': earning.status}
        ))
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark earnings as paid."""
        earning = self.get_object()
        payment_reference = request.data.get('payment_reference')
        
        earning.mark_as_paid(payment_reference)
        
        return Response(success_response(
            message="Earnings marked as paid successfully",
            data={'earning_id': earning.id, 'status': earning.status}
        ))
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get earnings summary."""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(earned_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(earned_date__lte=end_date)
        
        summary = queryset.aggregate(
            total_earnings=Sum('amount'),
            total_commission=Sum('commission_amount'),
            total_net=Sum('net_amount'),
            total_count=Count('id'),
            avg_earning=Avg('amount')
        )
        
        # Get earnings by type
        earnings_by_type = queryset.values('earning_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Get earnings by status
        earnings_by_status = queryset.values('status').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        summary_data = {
            'summary': summary,
            'earnings_by_type': list(earnings_by_type),
            'earnings_by_status': list(earnings_by_status)
        }
        
        return Response(success_response(
            message="Earnings summary retrieved successfully",
            data=summary_data
        ))
