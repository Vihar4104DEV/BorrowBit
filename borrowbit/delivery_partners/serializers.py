from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import transaction
from .models import (
    DeliveryPartner, DeliveryJob, JobAssignment, 
    DeliveryTracking, PartnerEarnings
)
from user.models import User


class DeliveryPartnerSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryPartner model."""
    user = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    is_working_now = serializers.SerializerMethodField()
    active_jobs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryPartner
        fields = '__all__'
        read_only_fields = ['id', 'partner_code', 'rating', 'total_deliveries', 
                           'successful_deliveries', 'failed_deliveries', 'created_at', 
                           'updated_at', 'last_location_update']
    
    def get_user(self, obj):
        """Get user details."""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'phone': obj.user.phone,
            }
        return None
    
    def get_success_rate(self, obj):
        """Get delivery success rate."""
        return obj.get_success_rate()
    
    def get_is_working_now(self, obj):
        """Check if partner is currently working."""
        return obj.is_working_now()
    
    def get_active_jobs_count(self, obj):
        """Get count of active jobs."""
        return obj.assigned_jobs.filter(status__in=['assigned', 'picked_up', 'in_transit']).count()
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value
    
    def validate_vehicle_number(self, value):
        """Validate vehicle number format."""
        if len(value) < 5:
            raise serializers.ValidationError("Vehicle number must be at least 5 characters.")
        return value.upper()
    
    def validate_service_areas(self, value):
        """Validate service areas."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Service areas must be a list.")
        if len(value) == 0:
            raise serializers.ValidationError("At least one service area must be specified.")
        return value
    
    def validate_working_days(self, value):
        """Validate working days."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Working days must be a list.")
        valid_days = list(range(7))  # 0-6 for Monday to Sunday
        if not all(day in valid_days for day in value):
            raise serializers.ValidationError("Working days must be numbers from 0-6 (Monday=0, Sunday=6).")
        return value


class DeliveryPartnerListSerializer(serializers.ModelSerializer):
    """List serializer for DeliveryPartner with minimal fields."""
    user_name = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    is_working_now = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryPartner
        fields = [
            'id', 'partner_code', 'user_name', 'status', 'is_available',
            'vehicle_type', 'city', 'state', 'rating', 'success_rate',
            'total_deliveries', 'is_working_now', 'created_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.get_full_name() if obj.user else ""
    
    def get_success_rate(self, obj):
        """Get delivery success rate."""
        return obj.get_success_rate()
    
    def get_is_working_now(self, obj):
        """Check if partner is currently working."""
        return obj.is_working_now()


class DeliveryPartnerCreateSerializer(serializers.ModelSerializer):
    """Create serializer for DeliveryPartner."""
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = DeliveryPartner
        fields = [
            'user_id', 'partner_type', 'phone_number', 'alternate_phone',
            'emergency_contact', 'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country', 'vehicle_type', 'vehicle_number',
            'vehicle_model', 'vehicle_color', 'service_areas', 'max_delivery_distance',
            'available_from', 'available_to', 'working_days', 'commission_rate',
            'minimum_payout', 'documents'
        ]
    
    def validate_user_id(self, value):
        """Validate user exists and doesn't already have a delivery partner profile."""
        try:
            user = User.objects.get(id=value)
            if hasattr(user, 'delivery_partner'):
                raise serializers.ValidationError("User already has a delivery partner profile.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value
    
    def create(self, validated_data):
        """Create delivery partner with user association."""
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        validated_data['user'] = user
        return super().create(validated_data)


class DeliveryJobSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryJob model."""
    customer = serializers.SerializerMethodField()
    assigned_partner = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    can_be_accepted = serializers.SerializerMethodField()
    estimated_delivery_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryJob
        fields = '__all__'
        read_only_fields = ['id', 'job_id', 'tracking_number', 'total_fare', 
                           'assigned_at', 'accepted_at', 'rejected_at', 
                           'actual_pickup_time', 'actual_delivery_time', 
                           'created_at', 'updated_at']
    
    def get_customer(self, obj):
        """Get customer details."""
        if obj.customer:
            return {
                'id': obj.customer.id,
                'email': obj.customer.email,
                'first_name': obj.customer.first_name,
                'last_name': obj.customer.last_name,
                'phone': obj.customer.phone,
            }
        return None
    
    def get_assigned_partner(self, obj):
        """Get assigned partner details."""
        if obj.assigned_partner:
            return {
                'id': obj.assigned_partner.id,
                'partner_code': obj.assigned_partner.partner_code,
                'user_name': obj.assigned_partner.user.get_full_name(),
                'phone': obj.assigned_partner.phone_number,
                'vehicle_type': obj.assigned_partner.vehicle_type,
            }
        return None
    
    def get_distance(self, obj):
        """Get distance between pickup and delivery locations."""
        return obj.get_distance()
    
    def get_can_be_accepted(self, obj):
        """Check if job can be accepted by current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(request.user, 'delivery_partner'):
                return obj.assigned_partner == request.user.delivery_partner and obj.status == 'assigned'
        return False
    
    def get_estimated_delivery_time_formatted(self, obj):
        """Get formatted estimated delivery time."""
        if obj.estimated_delivery_time:
            return obj.estimated_delivery_time.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def validate_pickup_date(self, value):
        """Validate pickup date is not in the past."""
        if value < timezone.now().date():
            raise serializers.ValidationError("Pickup date cannot be in the past.")
        return value
    
    def validate_delivery_date(self, value):
        """Validate delivery date is not before pickup date."""
        pickup_date = self.initial_data.get('pickup_date')
        if pickup_date and value < pickup_date:
            raise serializers.ValidationError("Delivery date cannot be before pickup date.")
        return value
    
    def validate_package_weight(self, value):
        """Validate package weight."""
        if value <= 0:
            raise serializers.ValidationError("Package weight must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate job data."""
        # Check if pickup and delivery addresses are different
        if data.get('pickup_address') == data.get('delivery_address'):
            raise serializers.ValidationError("Pickup and delivery addresses cannot be the same.")
        
        # Validate package dimensions
        package_dimensions = data.get('package_dimensions', {})
        if package_dimensions:
            required_fields = ['length', 'width', 'height']
            for field in required_fields:
                if field not in package_dimensions:
                    raise serializers.ValidationError(f"Package dimensions must include {field}.")
                if package_dimensions[field] <= 0:
                    raise serializers.ValidationError(f"Package {field} must be greater than 0.")
        
        return data


class DeliveryJobListSerializer(serializers.ModelSerializer):
    """List serializer for DeliveryJob with minimal fields."""
    customer_name = serializers.SerializerMethodField()
    assigned_partner_code = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryJob
        fields = [
            'id', 'job_id', 'job_type', 'status', 'priority', 'customer_name',
            'pickup_city', 'delivery_city', 'package_weight', 'total_fare',
            'assigned_partner_code', 'pickup_date', 'delivery_date', 'distance',
            'is_urgent', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name."""
        return obj.customer_name
    
    def get_assigned_partner_code(self, obj):
        """Get assigned partner code."""
        return obj.assigned_partner.partner_code if obj.assigned_partner else None
    
    def get_distance(self, obj):
        """Get distance between pickup and delivery locations."""
        return obj.get_distance()


class DeliveryJobCreateSerializer(serializers.ModelSerializer):
    """Create serializer for DeliveryJob."""
    customer_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = DeliveryJob
        fields = [
            'customer_id', 'job_type', 'priority', 'customer_name', 'customer_phone',
            'customer_email', 'pickup_address', 'pickup_pincode', 'pickup_city',
            'pickup_state', 'pickup_latitude', 'pickup_longitude', 'pickup_instructions',
            'pickup_contact_name', 'pickup_contact_phone', 'delivery_address',
            'delivery_pincode', 'delivery_city', 'delivery_state', 'delivery_latitude',
            'delivery_longitude', 'delivery_instructions', 'delivery_contact_name',
            'delivery_contact_phone', 'package_description', 'package_weight',
            'package_dimensions', 'package_value', 'is_fragile', 'is_urgent',
            'pickup_date', 'pickup_time_slot', 'delivery_date', 'delivery_time_slot',
            'base_fare', 'distance_fare', 'priority_fare', 'special_requirements',
            'insurance_required', 'insurance_amount'
        ]
    
    def validate_customer_id(self, value):
        """Validate customer exists."""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Customer does not exist.")
        return value
    
    def create(self, validated_data):
        """Create delivery job with customer association."""
        customer_id = validated_data.pop('customer_id')
        customer = User.objects.get(id=customer_id)
        validated_data['customer'] = customer
        return super().create(validated_data)


class JobAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for JobAssignment model."""
    job = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    response_time_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = JobAssignment
        fields = '__all__'
        read_only_fields = ['id', 'assigned_at', 'expires_at', 'created_at', 'updated_at']
    
    def get_job(self, obj):
        """Get job details."""
        return {
            'id': obj.job.id,
            'job_id': obj.job.job_id,
            'job_type': obj.job.job_type,
            'pickup_address': obj.job.pickup_address,
            'delivery_address': obj.job.delivery_address,
            'total_fare': obj.job.total_fare,
            'package_weight': obj.job.package_weight,
        }
    
    def get_partner(self, obj):
        """Get partner details."""
        return {
            'id': obj.partner.id,
            'partner_code': obj.partner.partner_code,
            'user_name': obj.partner.user.get_full_name(),
            'phone': obj.partner.phone_number,
            'vehicle_type': obj.partner.vehicle_type,
        }
    
    def get_is_expired(self, obj):
        """Check if assignment has expired."""
        return obj.is_expired()
    
    def get_response_time_seconds(self, obj):
        """Get response time in seconds."""
        if obj.response_time:
            return obj.response_time.total_seconds()
        return None
    
    def validate(self, data):
        """Validate assignment data."""
        # Check if assignment is expired
        if data.get('status') in ['accepted', 'rejected'] and self.instance and self.instance.is_expired():
            raise serializers.ValidationError("Assignment has expired and cannot be modified.")
        
        return data


class JobAssignmentCreateSerializer(serializers.ModelSerializer):
    """Create serializer for JobAssignment."""
    job_id = serializers.UUIDField(write_only=True)
    partner_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = JobAssignment
        fields = ['job_id', 'partner_id', 'expires_at']
    
    def validate(self, data):
        """Validate assignment data."""
        job_id = data.get('job_id')
        partner_id = data.get('partner_id')
        
        # Check if job exists and is available for assignment
        try:
            job = DeliveryJob.objects.get(id=job_id)
            if job.status != 'pending':
                raise serializers.ValidationError("Job is not available for assignment.")
        except DeliveryJob.DoesNotExist:
            raise serializers.ValidationError("Job does not exist.")
        
        # Check if partner exists and is available
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            if not partner.is_available or partner.status != 'active':
                raise serializers.ValidationError("Partner is not available for assignment.")
        except DeliveryPartner.DoesNotExist:
            raise serializers.ValidationError("Partner does not exist.")
        
        # Check if partner can accept this job
        if not partner.can_accept_job(job):
            raise serializers.ValidationError("Partner cannot accept this job.")
        
        # Check if assignment already exists
        if JobAssignment.objects.filter(job=job, partner=partner).exists():
            raise serializers.ValidationError("Assignment already exists.")
        
        return data
    
    def create(self, validated_data):
        """Create job assignment."""
        job_id = validated_data.pop('job_id')
        partner_id = validated_data.pop('partner_id')
        
        job = DeliveryJob.objects.get(id=job_id)
        partner = DeliveryPartner.objects.get(id=partner_id)
        
        validated_data['job'] = job
        validated_data['partner'] = partner
        
        return super().create(validated_data)


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryTracking model."""
    job = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryTracking
        fields = '__all__'
        read_only_fields = ['id', 'event_time', 'created_at', 'updated_at']
    
    def get_job(self, obj):
        """Get job details."""
        return {
            'id': obj.job.id,
            'job_id': obj.job.job_id,
            'status': obj.job.status,
        }
    
    def get_partner(self, obj):
        """Get partner details."""
        return {
            'id': obj.partner.id,
            'partner_code': obj.partner.partner_code,
            'user_name': obj.partner.user.get_full_name(),
        }
    
    def validate(self, data):
        """Validate tracking data."""
        # Validate location data if provided
        if data.get('latitude') is not None or data.get('longitude') is not None:
            if data.get('latitude') is None or data.get('longitude') is None:
                raise serializers.ValidationError("Both latitude and longitude must be provided for location updates.")
            
            # Validate latitude range
            if not -90 <= float(data['latitude']) <= 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90.")
            
            # Validate longitude range
            if not -180 <= float(data['longitude']) <= 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180.")
        
        return data


class PartnerEarningsSerializer(serializers.ModelSerializer):
    """Serializer for PartnerEarnings model."""
    partner = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerEarnings
        fields = '__all__'
        read_only_fields = ['id', 'commission_amount', 'net_amount', 'created_at', 'updated_at']
    
    def get_partner(self, obj):
        """Get partner details."""
        return {
            'id': obj.partner.id,
            'partner_code': obj.partner.partner_code,
            'user_name': obj.partner.user.get_full_name(),
        }
    
    def get_job(self, obj):
        """Get job details."""
        return {
            'id': obj.job.id,
            'job_id': obj.job.job_id,
            'total_fare': obj.job.total_fare,
        }
    
    def validate_amount(self, value):
        """Validate amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value
    
    def validate_commission_rate(self, value):
        """Validate commission rate."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Commission rate must be between 0 and 100.")
        return value


class PartnerEarningsListSerializer(serializers.ModelSerializer):
    """List serializer for PartnerEarnings with minimal fields."""
    partner_code = serializers.SerializerMethodField()
    job_id = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerEarnings
        fields = [
            'id', 'partner_code', 'job_id', 'earning_type', 'status',
            'amount', 'commission_amount', 'net_amount', 'earned_date',
            'approved_at', 'paid_at', 'created_at'
        ]
    
    def get_partner_code(self, obj):
        """Get partner code."""
        return obj.partner.partner_code
    
    def get_job_id(self, obj):
        """Get job ID."""
        return obj.job.job_id


class DeliveryPartnerDashboardSerializer(serializers.Serializer):
    """Serializer for delivery partner dashboard data."""
    partner = DeliveryPartnerSerializer()
    active_jobs = DeliveryJobListSerializer(many=True)
    pending_assignments = JobAssignmentSerializer(many=True)
    recent_earnings = PartnerEarningsListSerializer(many=True)
    today_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_deliveries = serializers.IntegerField()
    is_working_now = serializers.BooleanField()


class DeliveryJobStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating delivery job status."""
    status = serializers.ChoiceField(choices=DeliveryJob.JOB_STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    location_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate status update data."""
        status = data.get('status')
        reason = data.get('reason')
        
        # Require reason for failed status
        if status == 'failed' and not reason:
            raise serializers.ValidationError("Reason is required when marking job as failed.")
        
        # Validate location data if provided
        if data.get('latitude') is not None or data.get('longitude') is not None:
            if data.get('latitude') is None or data.get('longitude') is None:
                raise serializers.ValidationError("Both latitude and longitude must be provided for location updates.")
        
        return data


class JobAssignmentResponseSerializer(serializers.Serializer):
    """Serializer for partner response to job assignment."""
    action = serializers.ChoiceField(choices=['accept', 'reject'])
    estimated_pickup_time = serializers.DateTimeField(required=False)
    estimated_delivery_time = serializers.DateTimeField(required=False)
    partner_notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate assignment response data."""
        action = data.get('action')
        
        if action == 'accept':
            # Require estimated times for acceptance
            if not data.get('estimated_pickup_time'):
                raise serializers.ValidationError("Estimated pickup time is required when accepting assignment.")
            if not data.get('estimated_delivery_time'):
                raise serializers.ValidationError("Estimated delivery time is required when accepting assignment.")
        elif action == 'reject':
            # Require rejection reason
            if not data.get('rejection_reason'):
                raise serializers.ValidationError("Rejection reason is required when rejecting assignment.")
        
        return data


class DeliveryPartnerLocationUpdateSerializer(serializers.Serializer):
    """Serializer for updating delivery partner location."""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    
    def validate_latitude(self, value):
        """Validate latitude."""
        if not -90 <= float(value) <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude."""
        if not -180 <= float(value) <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class DeliveryPartnerAvailabilitySerializer(serializers.Serializer):
    """Serializer for updating delivery partner availability."""
    is_available = serializers.BooleanField()
    available_from = serializers.TimeField(required=False, allow_null=True)
    available_to = serializers.TimeField(required=False, allow_null=True)
    working_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False
    )
    
    def validate_working_days(self, value):
        """Validate working days."""
        if value and not all(day in range(7) for day in value):
            raise serializers.ValidationError("Working days must be numbers from 0-6 (Monday=0, Sunday=6).")
        return value
    
    def validate(self, data):
        """Validate availability data."""
        is_available = data.get('is_available')
        available_from = data.get('available_from')
        available_to = data.get('available_to')
        
        if is_available and available_from and available_to:
            if available_from >= available_to:
                raise serializers.ValidationError("Available from time must be before available to time.")
        
        return data
