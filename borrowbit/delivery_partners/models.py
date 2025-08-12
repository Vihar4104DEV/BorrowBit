from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import BaseModel
from user.models import UserRole
import uuid

User = get_user_model()


class DeliveryPartner(BaseModel):
    """
    Model representing delivery partners who handle pickup and delivery jobs.
    """
    PARTNER_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending_verification', 'Pending Verification'),
    ]
    
    PARTNER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('franchise', 'Franchise'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_partner')
    partner_code = models.CharField(max_length=20, unique=True, help_text="Unique partner identifier")
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPE_CHOICES, default='individual')
    status = models.CharField(max_length=20, choices=PARTNER_STATUS_CHOICES, default='pending_verification')
    
    # Contact Information
    phone_number = models.CharField(max_length=15, unique=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_model = models.CharField(max_length=100, blank=True, null=True)
    vehicle_color = models.CharField(max_length=50, blank=True, null=True)
    
    # Service Area
    service_areas = models.JSONField(default=list, help_text="List of area codes/pincodes served")
    max_delivery_distance = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0.1), MaxValueValidator(100.0)],
        help_text="Maximum delivery distance in kilometers"
    )
    
    # Performance Metrics
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, 
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    failed_deliveries = models.PositiveIntegerField(default=0)
    
    # Availability
    is_available = models.BooleanField(default=True)
    available_from = models.TimeField(blank=True, null=True)
    available_to = models.TimeField(blank=True, null=True)
    working_days = models.JSONField(default=list, help_text="List of working days (0=Monday, 6=Sunday)")
    
    # Financial Information
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=10.0,
        help_text="Commission rate as percentage"
    )
    minimum_payout = models.DecimalField(
        max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(0.0)],
        default=100.0
    )
    
    # Documents
    documents = models.JSONField(default=dict, help_text="Document URLs and verification status")
    
    # Location Tracking
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    last_location_update = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Delivery Partner"
        verbose_name_plural = "Delivery Partners"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_available']),
            models.Index(fields=['partner_code']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['vehicle_number']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['rating']),
            models.Index(fields=['current_latitude', 'current_longitude']),
        ]
    
    def __str__(self):
        return f"{self.partner_code} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.partner_code:
            self.partner_code = f"DP{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_success_rate(self):
        """Calculate delivery success rate."""
        if self.total_deliveries == 0:
            return 0.0
        return (self.successful_deliveries / self.total_deliveries) * 100
    
    def is_working_now(self):
        """Check if partner is currently working based on time and day."""
        if not self.is_available:
            return False
        
        now = timezone.now()
        current_time = now.time()
        current_day = now.weekday()
        
        # Check if today is a working day
        if current_day not in self.working_days:
            return False
        
        # Check if current time is within working hours
        if self.available_from and self.available_to:
            return self.available_from <= current_time <= self.available_to
        
        return True
    
    def update_location(self, latitude, longitude):
        """Update partner's current location."""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save(update_fields=['current_latitude', 'current_longitude', 'last_location_update'])
    
    def can_accept_job(self, job):
        """Check if partner can accept a specific job."""
        if not self.is_working_now():
            return False
        
        # Check if job is within service area
        if job.pickup_pincode not in self.service_areas and job.delivery_pincode not in self.service_areas:
            return False
        
        # Check if partner has capacity (not too many active jobs)
        active_jobs = self.delivery_jobs.filter(status__in=['assigned', 'picked_up', 'in_transit']).count()
        if active_jobs >= 5:  # Maximum 5 active jobs per partner
            return False
        
        return True


class DeliveryJob(BaseModel):
    """
    Model representing delivery jobs (pickup and delivery requests).
    """
    JOB_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
        ('pickup_and_delivery', 'Pickup and Delivery'),
        ('return', 'Return'),
    ]
    
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Job Information
    job_id = models.CharField(max_length=20, unique=True, help_text="Unique job identifier")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Customer Information
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_jobs')
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField()
    
    # Pickup Information
    pickup_address = models.TextField()
    pickup_pincode = models.CharField(max_length=10)
    pickup_city = models.CharField(max_length=100)
    pickup_state = models.CharField(max_length=100)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    pickup_instructions = models.TextField(blank=True, null=True)
    pickup_contact_name = models.CharField(max_length=255, blank=True, null=True)
    pickup_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Delivery Information
    delivery_address = models.TextField()
    delivery_pincode = models.CharField(max_length=10)
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    delivery_contact_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Package Information
    package_description = models.TextField()
    package_weight = models.DecimalField(
        max_digits=8, decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Weight in kilograms"
    )
    package_dimensions = models.JSONField(default=dict, help_text="Length, width, height in cm")
    package_value = models.DecimalField(
        max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(0.0)],
        help_text="Declared value of package"
    )
    is_fragile = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    # Timing Information
    pickup_date = models.DateField()
    pickup_time_slot = models.CharField(max_length=50, blank=True, null=True)
    delivery_date = models.DateField()
    delivery_time_slot = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    actual_pickup_time = models.DateTimeField(blank=True, null=True)
    actual_delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Financial Information
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    distance_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    priority_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    partner_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Assignment Information
    assigned_partner = models.ForeignKey(
        DeliveryPartner, on_delete=models.SET_NULL, 
        blank=True, null=True, related_name='assigned_jobs'
    )
    assigned_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Tracking Information
    tracking_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    current_location = models.JSONField(default=dict, help_text="Current location coordinates")
    route_optimization = models.JSONField(default=dict, help_text="Optimized route information")
    
    # Additional Information
    special_requirements = models.JSONField(default=dict, help_text="Special handling requirements")
    insurance_required = models.BooleanField(default=False)
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    class Meta:
        verbose_name = "Delivery Job"
        verbose_name_plural = "Delivery Jobs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['customer']),
            models.Index(fields=['assigned_partner']),
            models.Index(fields=['pickup_date', 'delivery_date']),
            models.Index(fields=['pickup_pincode', 'delivery_pincode']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['is_urgent', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.job_id} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.job_id:
            self.job_id = f"DJ{str(uuid.uuid4())[:8].upper()}"
        if not self.tracking_number:
            self.tracking_number = f"TRK{str(uuid.uuid4())[:12].upper()}"
        
        # Calculate total fare
        self.total_fare = self.base_fare + self.distance_fare + self.priority_fare
        
        super().save(*args, **kwargs)
    
    def assign_to_partner(self, partner):
        """Assign job to a delivery partner."""
        self.assigned_partner = partner
        self.assigned_at = timezone.now()
        self.status = 'assigned'
        self.save(update_fields=['assigned_partner', 'assigned_at', 'status'])
    
    def accept_by_partner(self):
        """Mark job as accepted by partner."""
        if self.assigned_partner:
            self.status = 'accepted'
            self.accepted_at = timezone.now()
            self.save(update_fields=['status', 'accepted_at'])
    
    def reject_by_partner(self, reason):
        """Mark job as rejected by partner."""
        if self.assigned_partner:
            self.status = 'rejected'
            self.rejected_at = timezone.now()
            self.rejection_reason = reason
            self.assigned_partner = None
            self.assigned_at = None
            self.save(update_fields=['status', 'rejected_at', 'rejection_reason', 'assigned_partner', 'assigned_at'])
    
    def mark_as_picked_up(self):
        """Mark job as picked up."""
        self.status = 'picked_up'
        self.actual_pickup_time = timezone.now()
        self.save(update_fields=['status', 'actual_pickup_time'])
    
    def mark_as_in_transit(self):
        """Mark job as in transit."""
        self.status = 'in_transit'
        self.save(update_fields=['status'])
    
    def mark_as_delivered(self):
        """Mark job as delivered."""
        self.status = 'delivered'
        self.actual_delivery_time = timezone.now()
        self.save(update_fields=['status', 'actual_delivery_time'])
        
        # Update partner statistics
        if self.assigned_partner:
            self.assigned_partner.successful_deliveries += 1
            self.assigned_partner.total_deliveries += 1
            self.assigned_partner.save(update_fields=['successful_deliveries', 'total_deliveries'])
    
    def mark_as_failed(self, reason):
        """Mark job as failed."""
        self.status = 'failed'
        self.save(update_fields=['status'])
        
        # Update partner statistics
        if self.assigned_partner:
            self.assigned_partner.failed_deliveries += 1
            self.assigned_partner.total_deliveries += 1
            self.assigned_partner.save(update_fields=['failed_deliveries', 'total_deliveries'])
    
    def cancel_job(self, reason):
        """Cancel the job."""
        self.status = 'cancelled'
        self.save(update_fields=['status'])
    
    def get_distance(self):
        """Calculate distance between pickup and delivery locations."""
        if self.pickup_latitude and self.pickup_longitude and self.delivery_latitude and self.delivery_longitude:
            # Simple distance calculation (can be replaced with more accurate formula)
            import math
            lat1, lon1 = float(self.pickup_latitude), float(self.pickup_longitude)
            lat2, lon2 = float(self.delivery_latitude), float(self.delivery_longitude)
            
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
                math.cos(lat1_rad) * math.cos(lat2_rad) * \
                math.sin(delta_lon/2) * math.sin(delta_lon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c
        return 0.0


class JobAssignment(BaseModel):
    """
    Model representing job assignments and partner responses.
    """
    RESPONSE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    job = models.ForeignKey(DeliveryJob, on_delete=models.CASCADE, related_name='assignments')
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='job_assignments')
    status = models.CharField(max_length=20, choices=RESPONSE_STATUS_CHOICES, default='pending')
    
    # Assignment Details
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Response Details
    response_time = models.DurationField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    estimated_pickup_time = models.DateTimeField(blank=True, null=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    
    # Partner Notes
    partner_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Job Assignment"
        verbose_name_plural = "Job Assignments"
        ordering = ['-assigned_at']
        unique_together = ['job', 'partner']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['job', 'partner']),
            models.Index(fields=['assigned_at']),
        ]
    
    def __str__(self):
        return f"{self.job.job_id} - {self.partner.partner_code}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)  # 30 minutes expiry
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if assignment has expired."""
        return timezone.now() > self.expires_at
    
    def accept_assignment(self, estimated_pickup_time=None, estimated_delivery_time=None, partner_notes=None):
        """Accept the job assignment."""
        if self.is_expired():
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.response_time = self.responded_at - self.assigned_at
        self.estimated_pickup_time = estimated_pickup_time
        self.estimated_delivery_time = estimated_delivery_time
        self.partner_notes = partner_notes
        self.save(update_fields=['status', 'responded_at', 'response_time', 'estimated_pickup_time', 'estimated_delivery_time', 'partner_notes'])
        
        # Update job status
        self.job.accept_by_partner()
        return True
    
    def reject_assignment(self, rejection_reason=None):
        """Reject the job assignment."""
        if self.is_expired():
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.response_time = self.responded_at - self.assigned_at
        self.rejection_reason = rejection_reason
        self.save(update_fields=['status', 'responded_at', 'response_time', 'rejection_reason'])
        
        # Update job status
        self.job.reject_by_partner(rejection_reason or "Partner rejected the assignment")
        return True


class DeliveryTracking(BaseModel):
    """
    Model for tracking delivery progress and location updates.
    """
    TRACKING_EVENT_CHOICES = [
        ('job_assigned', 'Job Assigned'),
        ('job_accepted', 'Job Accepted'),
        ('job_rejected', 'Job Rejected'),
        ('pickup_started', 'Pickup Started'),
        ('pickup_completed', 'Pickup Completed'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivery_attempted', 'Delivery Attempted'),
        ('delivery_completed', 'Delivery Completed'),
        ('delivery_failed', 'Delivery Failed'),
        ('location_update', 'Location Update'),
        ('status_update', 'Status Update'),
    ]
    
    job = models.ForeignKey(DeliveryJob, on_delete=models.CASCADE, related_name='tracking_events')
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='tracking_events')
    event_type = models.CharField(max_length=20, choices=TRACKING_EVENT_CHOICES)
    
    # Location Information
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_address = models.TextField(blank=True, null=True)
    
    # Event Details
    description = models.TextField()
    additional_data = models.JSONField(default=dict, help_text="Additional event data")
    
    # Timing
    event_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Delivery Tracking"
        verbose_name_plural = "Delivery Tracking"
        ordering = ['-event_time']
        indexes = [
            models.Index(fields=['job', 'event_time']),
            models.Index(fields=['partner', 'event_time']),
            models.Index(fields=['event_type', 'event_time']),
        ]
    
    def __str__(self):
        return f"{self.job.job_id} - {self.event_type} - {self.event_time}"


class PartnerEarnings(BaseModel):
    """
    Model for tracking partner earnings and payments.
    """
    EARNING_TYPE_CHOICES = [
        ('delivery_fee', 'Delivery Fee'),
        ('commission', 'Commission'),
        ('bonus', 'Bonus'),
        ('tip', 'Tip'),
        ('penalty', 'Penalty'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='earnings')
    job = models.ForeignKey(DeliveryJob, on_delete=models.CASCADE, related_name='partner_earnings')
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial Details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    
    # Timing
    earned_date = models.DateField()
    approved_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Partner Earning"
        verbose_name_plural = "Partner Earnings"
        ordering = ['-earned_date']
        indexes = [
            models.Index(fields=['partner', 'status']),
            models.Index(fields=['job']),
            models.Index(fields=['earning_type', 'earned_date']),
            models.Index(fields=['status', 'earned_date']),
        ]
    
    def __str__(self):
        return f"{self.partner.partner_code} - {self.amount} - {self.earning_type}"
    
    def save(self, *args, **kwargs):
        # Calculate commission and net amount
        if self.commission_rate > 0:
            self.commission_amount = (self.amount * self.commission_rate) / 100
        self.net_amount = self.amount - self.commission_amount
        super().save(*args, **kwargs)
    
    def approve_earning(self):
        """Approve the earning."""
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_at'])
    
    def mark_as_paid(self, payment_reference=None):
        """Mark earning as paid."""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.payment_reference = payment_reference
        self.save(update_fields=['status', 'paid_at', 'payment_reference'])
