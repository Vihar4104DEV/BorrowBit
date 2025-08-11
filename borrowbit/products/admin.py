"""
Admin configuration for product models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Product, ProductCategory, ProductPricing, ProductImage, 
    ProductReview, ProductMaintenance
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for ProductCategory."""
    
    list_display = ['name', 'slug', 'parent', 'is_featured', 'products_count', 'created_at']
    list_filter = ['is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        (_('Display'), {
            'fields': ('image', 'icon', 'sort_order', 'is_featured')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
    )
    
    def products_count(self, obj):
        """Display products count for category."""
        count = obj.get_products_count()
        return format_html('<span style="color: green;">{}</span>', count)
    products_count.short_description = _('Products Count')


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage."""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'sort_order', 'is_primary']


class ProductPricingInline(admin.TabularInline):
    """Inline admin for ProductPricing."""
    model = ProductPricing
    extra = 1
    fields = ['customer_type', 'duration_type', 'base_price', 'price_per_unit', 
              'hourly_rate', 'daily_rate', 'weekly_rate', 'monthly_rate',
              'discount_percentage', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product."""
    
    list_display = [
        'name', 'sku', 'owner', 'category', 'status', 'available_quantity',
        'admin_approved', 'is_featured', 'is_popular', 'created_at'
    ]
    list_filter = [
        'status', 'condition', 'admin_approved', 'is_featured', 'is_popular',
        'is_rentable', 'is_active', 'category', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description', 'brand', 'model']
    list_editable = ['admin_approved', 'is_featured', 'is_popular']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    prepopulated_fields = {'slug': ('name', 'sku')}
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'sku', 'owner', 'category')
        }),
        (_('Description'), {
            'fields': ('short_description', 'description', 'specifications', 'features')
        }),
        (_('Physical Attributes'), {
            'fields': ('dimensions', 'weight', 'color', 'material', 'brand', 'model')
        }),
        (_('Condition & Status'), {
            'fields': ('condition', 'status')
        }),
        (_('Inventory'), {
            'fields': ('total_quantity', 'available_quantity', 'reserved_quantity', 'minimum_quantity')
        }),
        (_('Financial'), {
            'fields': ('deposit_amount',)
        }),
        (_('Location & Storage'), {
            'fields': ('warehouse_location', 'storage_requirements')
        }),
        (_('Rental Settings'), {
            'fields': ('is_rentable', 'minimum_rental_duration', 'maximum_rental_duration')
        }),
        (_('Images & Media'), {
            'fields': ('main_image', 'images')
        }),
        (_('SEO & Marketing'), {
            'fields': ('meta_title', 'meta_description', 'keywords')
        }),
        (_('Business Logic'), {
            'fields': ('is_featured', 'is_popular', 'admin_approved', 'sort_order')
        }),
        (_('Maintenance'), {
            'fields': ('purchase_date', 'warranty_expiry', 'last_maintenance', 'next_maintenance')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductPricingInline]
    
    actions = ['approve_products', 'unapprove_products', 'feature_products', 
               'unfeature_products', 'activate_products', 'deactivate_products']
    
    def approve_products(self, request, queryset):
        """Approve selected products."""
        updated = queryset.update(admin_approved=True)
        self.message_user(request, f'{updated} products were successfully approved.')
    approve_products.short_description = _('Approve selected products')
    
    def unapprove_products(self, request, queryset):
        """Unapprove selected products."""
        updated = queryset.update(admin_approved=False)
        self.message_user(request, f'{updated} products were successfully unapproved.')
    unapprove_products.short_description = _('Unapprove selected products')
    
    def feature_products(self, request, queryset):
        """Feature selected products."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products were successfully featured.')
    feature_products.short_description = _('Feature selected products')
    
    def unfeature_products(self, request, queryset):
        """Unfeature selected products."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products were successfully unfeatured.')
    unfeature_products.short_description = _('Unfeature selected products')
    
    def activate_products(self, request, queryset):
        """Activate selected products."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products were successfully activated.')
    activate_products.short_description = _('Activate selected products')
    
    def deactivate_products(self, request, queryset):
        """Deactivate selected products."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products were successfully deactivated.')
    deactivate_products.short_description = _('Deactivate selected products')


@admin.register(ProductPricing)
class ProductPricingAdmin(admin.ModelAdmin):
    """Admin configuration for ProductPricing."""
    
    list_display = [
        'product', 'customer_type', 'duration_type', 'base_price', 
        'price_per_unit', 'is_active', 'priority'
    ]
    list_filter = ['customer_type', 'duration_type', 'is_active', 'priority', 'created_at']
    search_fields = ['product__name', 'product__sku']
    ordering = ['product', 'customer_type', 'priority', 'duration_type']
    
    fieldsets = (
        (_('Product & Type'), {
            'fields': ('product', 'customer_type', 'duration_type')
        }),
        (_('Pricing'), {
            'fields': ('base_price', 'price_per_unit', 'hourly_rate', 'daily_rate', 
                      'weekly_rate', 'monthly_rate')
        }),
        (_('Discounts'), {
            'fields': ('discount_percentage', 'bulk_discount_threshold', 'bulk_discount_percentage')
        }),
        (_('Additional Charges'), {
            'fields': ('setup_fee', 'delivery_fee', 'late_return_fee_per_day')
        }),
        (_('Seasonal & Validity'), {
            'fields': ('seasonal_multiplier', 'valid_from', 'valid_to')
        }),
        (_('Priority'), {
            'fields': ('priority', 'overrides_lower_priority')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage."""
    
    list_display = ['product', 'image_preview', 'alt_text', 'is_primary', 'sort_order']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text', 'caption']
    ordering = ['product', 'sort_order', '-is_primary']
    
    fieldsets = (
        (_('Image Information'), {
            'fields': ('product', 'image', 'alt_text', 'caption')
        }),
        (_('Display'), {
            'fields': ('sort_order', 'is_primary')
        }),
    )
    
    def image_preview(self, obj):
        """Display image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Preview')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview."""
    
    list_display = [
        'product', 'user', 'rating', 'title', 'is_verified_purchase', 
        'is_approved', 'created_at'
    ]
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        (_('Status'), {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews were successfully approved.')
    approve_reviews.short_description = _('Approve selected reviews')
    
    def reject_reviews(self, request, queryset):
        """Reject selected reviews."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews were successfully rejected.')
    reject_reviews.short_description = _('Reject selected reviews')


@admin.register(ProductMaintenance)
class ProductMaintenanceAdmin(admin.ModelAdmin):
    """Admin configuration for ProductMaintenance."""
    
    list_display = [
        'product', 'maintenance_type', 'status', 'scheduled_date', 
        'assigned_technician', 'cost'
    ]
    list_filter = ['maintenance_type', 'status', 'scheduled_date', 'created_at']
    search_fields = ['product__name', 'description', 'assigned_technician__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-scheduled_date']
    
    fieldsets = (
        (_('Maintenance Information'), {
            'fields': ('product', 'maintenance_type', 'status')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_date', 'start_date', 'completed_date')
        }),
        (_('Details'), {
            'fields': ('description', 'technician_notes', 'cost')
        }),
        (_('Personnel'), {
            'fields': ('assigned_technician',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['start_maintenance', 'complete_maintenance']
    
    def start_maintenance(self, request, queryset):
        """Start selected maintenance tasks."""
        for maintenance in queryset.filter(status='SCHEDULED'):
            maintenance.start_maintenance()
        self.message_user(request, f'{queryset.count()} maintenance tasks were started.')
    start_maintenance.short_description = _('Start selected maintenance tasks')
    
    def complete_maintenance(self, request, queryset):
        """Complete selected maintenance tasks."""
        for maintenance in queryset.filter(status='IN_PROGRESS'):
            maintenance.complete_maintenance()
        self.message_user(request, f'{queryset.count()} maintenance tasks were completed.')
    complete_maintenance.short_description = _('Complete selected maintenance tasks')
