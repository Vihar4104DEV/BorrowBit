"""
Product models for the rental backend application.
This module contains models for product catalog, categories, pricing, and inventory management.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import BaseModel

User = get_user_model()


class ProductCategory(BaseModel):
    """Product categories for organizing rental products with hierarchical structure."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Category Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name=_("Parent Category")
    )
    image = models.ImageField(
        upload_to='category_images/', 
        blank=True, 
        null=True,
        verbose_name=_("Category Image")
    )
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"))
    
    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the category."""
        return f"/products/category/{self.slug}/"
    
    def get_products_count(self):
        """Get the total number of active products in this category."""
        return self.products.filter(is_active=True).count()
    
    def get_all_children(self):
        """Get all child categories recursively."""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children


class Product(BaseModel):
    """Main product model for rental items with comprehensive features."""
    
    CONDITION_CHOICES = [
        ('NEW', _('New')),
        ('EXCELLENT', _('Excellent')),
        ('GOOD', _('Good')),
        ('FAIR', _('Fair')),
        ('POOR', _('Poor')),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', _('Available')),
        ('RENTED', _('Rented')),
        ('MAINTENANCE', _('Under Maintenance')),
        ('RETIRED', _('Retired')),
        ('RESERVED', _('Reserved')),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name=_("Product Name"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Product Slug"))
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='owned_products',
        verbose_name=_("Owner")
    )
    
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.PROTECT, 
        related_name='products',
        verbose_name=_("Category")
    )
    
    # Description and details
    short_description = models.TextField(max_length=500, verbose_name=_("Short Description"))
    description = models.TextField(verbose_name=_("Long Description"))
    specifications = models.JSONField(default=dict, blank=True, verbose_name=_("Specifications"))
    features = models.JSONField(default=list, blank=True, verbose_name=_("Features"))
    
    # Physical attributes
    dimensions = models.JSONField(default=dict, blank=True, verbose_name=_("Dimensions"))
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Weight (kg)")
    )
    color = models.CharField(max_length=50, blank=True, verbose_name=_("Color"))
    material = models.CharField(max_length=100, blank=True, verbose_name=_("Material"))
    brand = models.CharField(max_length=100, blank=True, verbose_name=_("Brand"))
    model = models.CharField(max_length=100, blank=True, verbose_name=_("Model"))
    
    # Condition and status
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        default='GOOD',
        verbose_name=_("Condition")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='AVAILABLE',
        verbose_name=_("Status")
    )
    
    # Inventory and availability
    total_quantity = models.PositiveIntegerField(default=1, verbose_name=_("Total Quantity"))
    available_quantity = models.PositiveIntegerField(default=1, verbose_name=_("Available Quantity"))
    reserved_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Reserved Quantity"))
    minimum_quantity = models.PositiveIntegerField(default=1, verbose_name=_("Minimum Quantity"))
    
    # Financial information
    deposit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Security Deposit Amount")
    )
    
    # Location and storage
    warehouse_location = models.CharField(max_length=100, blank=True, verbose_name=_("Warehouse Location"))
    storage_requirements = models.TextField(blank=True, verbose_name=_("Storage Requirements"))
    
    # Rental information
    is_rentable = models.BooleanField(default=True, verbose_name=_("Is Rentable"))
    minimum_rental_duration = models.PositiveIntegerField(
        default=1, 
        verbose_name=_("Minimum Rental Duration (hours)")
    )
    maximum_rental_duration = models.PositiveIntegerField(
        default=8760, 
        verbose_name=_("Maximum Rental Duration (hours)")
    )
    
    # Images and media
    main_image = models.FileField(
        upload_to='product_images/', 
        blank=True,
        null=True,
        verbose_name=_("Main Image")
    )
    images = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name=_("Additional Images")
    )
    
    # SEO and marketing
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, verbose_name=_("Meta Description"))
    keywords = models.TextField(blank=True, verbose_name=_("Keywords"))
    
    # Business logic
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured"))
    is_popular = models.BooleanField(default=False, verbose_name=_("Is Popular"))
    admin_approved = models.BooleanField(default=False, verbose_name=_("Admin Approved"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    
    # Maintenance and lifecycle
    purchase_date = models.DateField(null=True, blank=True, verbose_name=_("Purchase Date"))
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name=_("Warranty Expiry"))
    last_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Last Maintenance"))
    next_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Next Maintenance"))
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_rentable', 'status']),
            models.Index(fields=['is_featured', 'is_popular']),
            models.Index(fields=['admin_approved']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the product."""
        return f"/products/{self.slug}/"
    
    def get_rental_price(self, duration_hours, customer_type='REGULAR'):
        """Get rental price for a specific duration and customer type."""
        try:
            pricing_rule = self.pricing_rules.filter(
                customer_type=customer_type,
                is_active=True
            ).order_by('priority').first()
            
            if pricing_rule:
                # Convert hours to the appropriate duration type
                if pricing_rule.duration_type == 'HOURLY':
                    duration_units = duration_hours
                elif pricing_rule.duration_type == 'DAILY':
                    duration_units = max(1, duration_hours // 24)
                elif pricing_rule.duration_type == 'WEEKLY':
                    duration_units = max(1, duration_hours // (24 * 7))
                elif pricing_rule.duration_type == 'MONTHLY':
                    duration_units = max(1, duration_hours // (24 * 30))
                else:
                    duration_units = duration_hours
                
                return pricing_rule.calculate_price(duration_units)
            
            return 0
            
        except Exception:
            return 0
    
    def is_available_for_rental(self, start_date, end_date, quantity=1):
        """Check if product is available for rental during specified period."""
        if not self.is_rentable or self.status != 'AVAILABLE' or not self.admin_approved:
            return False
        
        if self.available_quantity < quantity:
            return False
        
        # Check for conflicts with existing rentals (this would need rental model)
        # For now, just check basic availability
        return True
    
    def reserve_quantity(self, quantity):
        """Reserve a quantity of the product."""
        if self.available_quantity >= quantity:
            self.available_quantity -= quantity
            self.reserved_quantity += quantity
            self.save(update_fields=['available_quantity', 'reserved_quantity'])
            self.update_status()
            return True
        return False
    
    def release_reservation(self, quantity):
        """Release a reserved quantity of the product."""
        if self.reserved_quantity >= quantity:
            self.reserved_quantity -= quantity
            self.available_quantity += quantity
            self.save(update_fields=['available_quantity', 'reserved_quantity'])
            self.update_status()
            return True
        return False
    
    def is_available_quantity(self, quantity):
        """Check if the specified quantity is available for rental."""
        return self.available_quantity >= quantity
    
    def update_status(self):
        """Update product status based on availability."""
        if self.available_quantity == 0 and self.reserved_quantity > 0:
            self.status = 'RESERVED'
        elif self.available_quantity == 0:
            self.status = 'RENTED'
        else:
            self.status = 'AVAILABLE'
        self.save(update_fields=['status'])


class ProductPricing(BaseModel):
    """Flexible pricing rules for products based on duration and customer type."""
    
    CUSTOMER_TYPE_CHOICES = [
        ('REGULAR', _('Regular Customer')),
        ('CORPORATE', _('Corporate Customer')),
        ('VIP', _('VIP Customer')),
        ('STAFF', _('Staff Member')),
    ]
    
    DURATION_TYPE_CHOICES = [
        ('HOURLY', _('Hourly')),
        ('DAILY', _('Daily')),
        ('WEEKLY', _('Weekly')),
        ('MONTHLY', _('Monthly')),
        ('YEARLY', _('Yearly')),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='pricing_rules',
        verbose_name=_("Product")
    )
    customer_type = models.CharField(
        max_length=20, 
        choices=CUSTOMER_TYPE_CHOICES, 
        default='REGULAR',
        verbose_name=_("Customer Type")
    )
    duration_type = models.CharField(
        max_length=20, 
        choices=DURATION_TYPE_CHOICES, 
        verbose_name=_("Duration Type")
    )
    
    # Consolidated pricing fields
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name=_("Base Price")
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name=_("Price Per Unit")
    )
    
    # For backward compatibility with existing rate fields
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Hourly Rate")
    )
    daily_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Daily Rate")
    )
    weekly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Weekly Rate")
    )
    monthly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Monthly Rate")
    )
    
    # Discounts and special pricing
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Discount Percentage")
    )
    bulk_discount_threshold = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("Bulk Discount Threshold")
    )
    bulk_discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Bulk Discount Percentage")
    )
    
    # Seasonal pricing and validity
    seasonal_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=1.0,
        verbose_name=_("Seasonal Multiplier")
    )
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid From"))
    valid_to = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid Until"))
    
    # Additional charges
    setup_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Setup Fee")
    )
    delivery_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Delivery Fee")
    )
    late_return_fee_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Late Return Fee Per Day")
    )
    
    # Priority and overrides
    priority = models.PositiveIntegerField(default=0, verbose_name=_("Priority"))
    overrides_lower_priority = models.BooleanField(default=False, verbose_name=_("Overrides Lower Priority"))
    
    class Meta:
        verbose_name = _("Product Pricing")
        verbose_name_plural = _("Product Pricing Rules")
        ordering = ['product', 'customer_type', 'priority', 'duration_type']
        unique_together = ['product', 'customer_type', 'duration_type', 'priority']
        indexes = [
            models.Index(fields=['product', 'customer_type']),
            models.Index(fields=['valid_from', 'valid_to']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_customer_type_display()} - {self.get_duration_type_display()}"
    
    def clean(self):
        """Validate pricing data."""
        if self.valid_from and self.valid_to and self.valid_from >= self.valid_to:
            raise ValidationError(_("Valid from date must be before valid to date."))
    
    def is_valid_for_date(self, date):
        """Check if pricing rule is valid for a specific date."""
        if self.valid_from and date < self.valid_from:
            return False
        if self.valid_to and date > self.valid_to:
            return False
        return True
    
    def calculate_price(self, duration_units, quantity=1):
        """Calculate rental price for given duration and quantity."""
        # Use specific rate fields if available, otherwise use base + per unit
        if self.duration_type == 'HOURLY' and self.hourly_rate:
            unit_price = self.hourly_rate
        elif self.duration_type == 'DAILY' and self.daily_rate:
            unit_price = self.daily_rate
        elif self.duration_type == 'WEEKLY' and self.weekly_rate:
            unit_price = self.weekly_rate
        elif self.duration_type == 'MONTHLY' and self.monthly_rate:
            unit_price = self.monthly_rate
        else:
            unit_price = self.base_price + (self.price_per_unit * duration_units)
        
        if self.duration_type in ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY'] and unit_price != (self.base_price + (self.price_per_unit * duration_units)):
            total_price = unit_price * duration_units
        else:
            total_price = unit_price
        
        # Apply quantity discount
        if quantity >= self.bulk_discount_threshold and self.bulk_discount_percentage > 0:
            discount_amount = total_price * (self.bulk_discount_percentage / 100)
            total_price -= discount_amount
        
        # Apply customer discount
        if self.discount_percentage > 0:
            discount_amount = total_price * (self.discount_percentage / 100)
            total_price -= discount_amount
        
        # Apply seasonal multiplier
        total_price *= self.seasonal_multiplier
        
        # Add setup and delivery fees
        total_price += self.setup_fee + self.delivery_fee
        
        # Multiply by quantity
        total_price *= quantity
        
        return max(0, total_price)


class ProductImage(BaseModel):
    """Additional images for products."""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='product_images',
        verbose_name=_("Product")
    )
    image = models.ImageField(
        upload_to='product_images/', 
        verbose_name=_("Image")
    )
    alt_text = models.CharField(max_length=200, blank=True, verbose_name=_("Alt Text"))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_("Caption"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Is Primary"))
    
    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['product', 'sort_order', '-is_primary']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductReview(BaseModel):
    """Customer reviews and ratings for products."""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name=_("Product")
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='product_reviews',
        verbose_name=_("User")
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating")
    )
    title = models.CharField(max_length=200, verbose_name=_("Review Title"))
    comment = models.TextField(verbose_name=_("Review Comment"))
    is_verified_purchase = models.BooleanField(default=False, verbose_name=_("Verified Purchase"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    
    class Meta:
        verbose_name = _("Product Review")
        verbose_name_plural = _("Product Reviews")
        ordering = ['-created_at']
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.get_full_name() or self.user.username} for {self.product.name}"
    
    def get_rating_display(self):
        """Get human-readable rating display."""
        rating_map = {
            1: _('Poor'),
            2: _('Fair'),
            3: _('Good'),
            4: _('Very Good'),
            5: _('Excellent')
        }
        return rating_map.get(self.rating, _('Unknown'))


class ProductMaintenance(BaseModel):
    """Maintenance records for products."""
    
    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', _('Preventive Maintenance')),
        ('CORRECTIVE', _('Corrective Maintenance')),
        ('INSPECTION', _('Inspection')),
        ('REPAIR', _('Repair')),
        ('CLEANING', _('Cleaning')),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', _('Scheduled')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='maintenance_records',
        verbose_name=_("Product")
    )
    maintenance_type = models.CharField(
        max_length=20, 
        choices=MAINTENANCE_TYPE_CHOICES, 
        verbose_name=_("Maintenance Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='SCHEDULED',
        verbose_name=_("Status")
    )
    
    # Scheduling
    scheduled_date = models.DateTimeField(verbose_name=_("Scheduled Date"))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Start Date"))
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed Date"))
    
    # Details
    description = models.TextField(verbose_name=_("Description"))
    technician_notes = models.TextField(blank=True, verbose_name=_("Technician Notes"))
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Cost")
    )
    
    # Personnel
    assigned_technician = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_maintenance',
        verbose_name=_("Assigned Technician")
    )
    
    class Meta:
        verbose_name = _("Product Maintenance")
        verbose_name_plural = _("Product Maintenance Records")
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['assigned_technician']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_maintenance_type_display()} for {self.product.name} on {self.scheduled_date.date()}"
    
    def clean(self):
        """Validate maintenance data."""
        if self.start_date and self.start_date < self.scheduled_date:
            raise ValidationError(_("Start date cannot be before scheduled date."))
        if self.completed_date and self.start_date and self.completed_date < self.start_date:
            raise ValidationError(_("Completed date cannot be before start date."))
    
    def is_overdue(self):
        """Check if maintenance is overdue."""
        return self.status == 'SCHEDULED' and timezone.now() > self.scheduled_date
    
    def start_maintenance(self):
        """Start the maintenance process."""
        self.status = 'IN_PROGRESS'
        self.start_date = timezone.now()
        self.save(update_fields=['status', 'start_date'])
        
        # Update product status to maintenance
        self.product.status = 'MAINTENANCE'
        self.product.save(update_fields=['status'])
    
    def complete_maintenance(self):
        """Complete the maintenance process."""
        self.status = 'COMPLETED'
        self.completed_date = timezone.now()
        self.save(update_fields=['status', 'completed_date'])
        
        # Update product's last maintenance date and status
        self.product.last_maintenance = timezone.now().date()
        self.product.status = 'AVAILABLE'
        self.product.save(update_fields=['last_maintenance', 'status'])