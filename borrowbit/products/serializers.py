"""
Serializers for product management with role-based access control.
"""
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    Product, ProductCategory, ProductPricing, ProductImage, 
    ProductReview, ProductMaintenance
)
from user.models import User, UserRole
from core.utils import cache_key_generator, set_cache_data, get_cache_data, delete_cache_data


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    
    # products_count = serializers.SerializerMethodField()
    # children = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug'
            # , 'description', 'parent', 'image', 
            # 'icon', 'sort_order', 'is_featured', 'products_count', 
            # 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    # def get_products_count(self, obj):
    #     """Get count of active products in category."""
    #     cache_key = cache_key_generator('category_products_count', str(obj.id))
    #     cached_count = get_cache_data(cache_key)
        
    #     if cached_count is not None:
    #         return cached_count
        
    #     count = obj.get_products_count()
    #     set_cache_data(cache_key, count, timeout=300)  # Cache for 5 minutes
    #     return count
    
    # def get_children(self, obj):
    #     """Get child categories."""
    #     children = obj.children.filter(is_active=True, is_deleted=False)
    #     return ProductCategorySerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'caption', 'sort_order', 
            'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductPricingSerializer(serializers.ModelSerializer):
    """Serializer for product pricing rules."""
    
    class Meta:
        model = ProductPricing
        fields = [
            'id', 'customer_type', 'duration_type', 'base_price', 
            'price_per_unit', 'hourly_rate', 'daily_rate', 'weekly_rate', 
            'monthly_rate', 'discount_percentage', 'bulk_discount_threshold',
            'bulk_discount_percentage', 'seasonal_multiplier', 'valid_from',
            'valid_to', 'setup_fee', 'delivery_fee', 'late_return_fee_per_day',
            'priority', 'overrides_lower_priority', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews."""
    
    user_name = serializers.SerializerMethodField()
    rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'user_name', 'rating', 'rating_display',
            'title', 'comment', 'is_verified_purchase', 'is_approved', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'is_approved', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.get_full_name() if obj.user else "Anonymous"
    
    def get_rating_display(self, obj):
        """Get human-readable rating."""
        return obj.get_rating_display()
    
    def validate(self, data):
        """Validate review data."""
        user = self.context['request'].user
        product = data.get('product')
        
        # Check if user has already reviewed this product
        if ProductReview.objects.filter(user=user, product=product).exists():
            raise ValidationError(_("You have already reviewed this product."))
        
        return data


class ProductMaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for product maintenance records."""
    
    assigned_technician_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductMaintenance
        fields = [
            'id', 'product', 'maintenance_type', 'status', 'scheduled_date',
            'start_date', 'completed_date', 'description', 'technician_notes',
            'cost', 'assigned_technician', 'assigned_technician_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_assigned_technician_name(self, obj):
        """Get assigned technician's name."""
        return obj.assigned_technician.get_full_name() if obj.assigned_technician else None


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product listing with basic information for cart and listing."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    basic_pricing = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'owner', 'owner_name', 'short_description', 'condition',
            'status', 'available_quantity', 'deposit_amount',
            'main_image_url', 'average_rating', 'review_count',
            'basic_pricing', 'is_featured', 'is_popular', 'admin_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_main_image_url(self, obj):
        """Get main image URL."""
        if obj.main_image:
            return self.context['request'].build_absolute_uri(obj.main_image.url)
        return None
    
    def get_average_rating(self, obj):
        """Get average rating for the product."""
        cache_key = cache_key_generator('product_avg_rating', str(obj.id))
        cached_rating = get_cache_data(cache_key)
        
        if cached_rating is not None:
            return cached_rating
        
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            set_cache_data(cache_key, round(avg_rating, 1), timeout=600)  # Cache for 10 minutes
            return round(avg_rating, 1)
        return 0.0
    
    def get_review_count(self, obj):
        """Get count of approved reviews."""
        cache_key = cache_key_generator('product_review_count', str(obj.id))
        cached_count = get_cache_data(cache_key)
        
        if cached_count is not None:
            return cached_count
        
        count = obj.reviews.filter(is_approved=True).count()
        set_cache_data(cache_key, count, timeout=600)  # Cache for 10 minutes
        return count
    
    def get_basic_pricing(self, obj):
        """Get basic pricing information for listing and cart."""
        try:
            # Get the most common pricing rule (REGULAR customer, DAILY duration)
            pricing_rule = obj.pricing_rules.filter(
                customer_type='REGULAR',
                duration_type='DAILY'
            ).first()
            
            if not pricing_rule:
                # Fallback to any available pricing rule
                pricing_rule = obj.pricing_rules.filter(is_active=True).first()
            
            if pricing_rule:
                return {
                    'daily_rate': str(pricing_rule.daily_rate) if pricing_rule.daily_rate else str(pricing_rule.base_price),
                    'hourly_rate': str(pricing_rule.hourly_rate) if pricing_rule.hourly_rate else None,
                    'weekly_rate': str(pricing_rule.weekly_rate) if pricing_rule.weekly_rate else None,
                    'monthly_rate': str(pricing_rule.monthly_rate) if pricing_rule.monthly_rate else None,
                    'setup_fee': str(pricing_rule.setup_fee),
                    'delivery_fee': str(pricing_rule.delivery_fee),
                    'currency': 'USD'  # You can make this configurable
                }
            
            return {
                'daily_rate': None,
                'hourly_rate': None,
                'weekly_rate': None,
                'monthly_rate': None,
                'setup_fee': '0.00',
                'delivery_fee': '0.00',
                'currency': 'USD'
            }
        except Exception:
            return {
                'daily_rate': None,
                'hourly_rate': None,
                'weekly_rate': None,
                'monthly_rate': None,
                'setup_fee': '0.00',
                'delivery_fee': '0.00',
                'currency': 'USD'
            }


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product with full information."""
    
    category = ProductCategorySerializer(read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    pricing_rules = ProductPricingSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    maintenance_records = ProductMaintenanceSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'owner', 'owner_name', 'category',
            'short_description', 'description', 'specifications', 'features',
            'dimensions', 'weight', 'color', 'material', 'brand', 'model',
            'condition', 'status', 'total_quantity', 'available_quantity',
            'reserved_quantity', 'minimum_quantity', 'deposit_amount',
            'warehouse_location', 'storage_requirements', 'is_rentable',
            'minimum_rental_duration', 'maximum_rental_duration',
            'main_image', 'images', 'meta_title', 'meta_description',
            'keywords', 'is_featured', 'is_popular', 'admin_approved',
            'sort_order', 'purchase_date', 'warranty_expiry', 'last_maintenance',
            'next_maintenance', 'pricing_rules', 'reviews', 'maintenance_records',
            'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        """Get average rating for the product."""
        cache_key = cache_key_generator('product_avg_rating', str(obj.id))
        cached_rating = get_cache_data(cache_key)
        
        if cached_rating is not None:
            return cached_rating
        
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            set_cache_data(cache_key, round(avg_rating, 1), timeout=600)  # Cache for 10 minutes
            return round(avg_rating, 1)
        return 0.0
    
    def get_review_count(self, obj):
        """Get count of approved reviews."""
        cache_key = cache_key_generator('product_review_count', str(obj.id))
        cached_count = get_cache_data(cache_key)
        
        if cached_count is not None:
            return cached_count
        
        count = obj.reviews.filter(is_approved=True).count()
        set_cache_data(cache_key, count, timeout=600)  # Cache for 10 minutes
        return count


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products with role-based field access."""
    
    main_image = serializers.ImageField(
        required=False, 
        allow_null=True,
        allow_empty_file=True,
        use_url=True
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'short_description', 'description',
            'specifications', 'features', 'dimensions', 'weight', 'color',
            'material', 'brand', 'model', 'condition', 'total_quantity',
            'deposit_amount', 'warehouse_location', 'storage_requirements',
            'is_rentable', 'minimum_rental_duration', 'maximum_rental_duration',
            'main_image', 'images', 'meta_title', 'meta_description',
            'keywords', 'is_featured', 'is_popular', 'admin_approved',
            'sort_order', 'purchase_date', 'warranty_expiry'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get user from context to determine role-based field access
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self._set_role_based_fields(request.user)
    
    def _set_role_based_fields(self, user):
        """Set read-only fields based on user role."""
        if not user.is_authenticated:
            return
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Admin and Super Admin have full access
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return
        
        # Staff and Manager have limited access
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            admin_fields = ['admin_approved', 'is_featured', 'is_popular']
            for field in admin_fields:
                if field in self.fields:
                    self.fields[field].read_only = True
        
        # Customers have very limited access
        if 'CUSTOMER' in role_names:
            restricted_fields = [
                'admin_approved', 'is_featured', 'is_popular', 'sort_order',
                'warehouse_location', 'storage_requirements', 'purchase_date',
                'warranty_expiry', 'total_quantity'
            ]
            for field in restricted_fields:
                if field in self.fields:
                    self.fields[field].read_only = True
    
    def validate_main_image(self, value):
        """Validate the main image field."""
        print("Debug - Received main_image value type:", type(value))
        print("Debug - Received main_image value:", value[:100] if isinstance(value, str) else value)
        
        if not value:
            return None
            
        if isinstance(value, str) and value.startswith('data:image'):
            try:
                import base64
                from django.core.files.base import ContentFile
                import uuid
                
                # Get the image format and base64 data
                format, imgstr = value.split(';base64,') 
                ext = format.split('/')[-1]
                
                # Generate unique filename
                filename = f"{uuid.uuid4()}.{ext}"
                
                # Decode base64 and validate
                try:
                    decoded_data = base64.b64decode(imgstr)
                    if not decoded_data:
                        raise ValidationError("Invalid base64 image data")
                except Exception as e:
                    print("Debug - Base64 decode error:", str(e))
                    raise ValidationError(f"Invalid base64 image data: {str(e)}")
                
                # Convert to ContentFile
                data = ContentFile(decoded_data, name=filename)
                print("Debug - Successfully created ContentFile")
                return data
                
            except Exception as e:
                print("Debug - Error processing image:", str(e))
                raise ValidationError(f"Error processing image: {str(e)}")
            
        print("Debug - Returning original value")
        return value

    def validate(self, data):
        """Validate product data."""
        # Validate rental duration
        min_duration = data.get('minimum_rental_duration', 1)
        max_duration = data.get('maximum_rental_duration', 8760)
        
        if min_duration > max_duration:
            raise ValidationError(_("Minimum rental duration cannot be greater than maximum rental duration."))
        
        # Validate quantities
        total_quantity = data.get('total_quantity', 1)
        if total_quantity < 1:
            raise ValidationError(_("Total quantity must be at least 1."))
        
        # Validate deposit amount
        deposit_amount = data.get('deposit_amount', 0)
        if deposit_amount < 0:
            raise ValidationError(_("Deposit amount cannot be negative."))
        
        return data
    
    def create(self, validated_data):
        """Create a new product."""
        try:
            print("Debug - Create method - validated_data:", {k: str(v)[:100] if k == 'main_image' else v for k, v in validated_data.items()})
            
            # Set owner to current user
            validated_data['owner'] = self.context['request'].user
            
            # Set initial available quantity
            validated_data['available_quantity'] = validated_data.get('total_quantity', 1)
            
            # Handle main_image specially if it's still a base64 string
            main_image = validated_data.get('main_image')
            if main_image and isinstance(main_image, str) and main_image.startswith('data:image'):
                validated_data['main_image'] = self.validate_main_image(main_image)
            
            product = super().create(validated_data)
            
            # Clear cache for category products count
            cache_key = cache_key_generator('category_products_count', str(product.category.id))
            delete_cache_data(cache_key)
            
            return product
            
        except Exception as e:
            print("Debug - Error in create method:", str(e))
            raise
    
    def update(self, instance, validated_data):
        """Update an existing product."""
        # Handle quantity updates
        if 'total_quantity' in validated_data:
            new_total = validated_data['total_quantity']
            current_available = instance.available_quantity
            current_reserved = instance.reserved_quantity
            
            # Calculate new available quantity
            if new_total >= (current_available + current_reserved):
                validated_data['available_quantity'] = new_total - current_reserved
            else:
                raise ValidationError(_("Cannot reduce total quantity below currently available + reserved quantity."))
        
        product = super().update(instance, validated_data)
        
        # Clear related caches
        cache_key = cache_key_generator('category_products_count', str(product.category.id))
        delete_cache_data(cache_key)
        
        return product


class ProductBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk product actions."""
    
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
        help_text=_("List of product IDs to perform action on")
    )
    action = serializers.ChoiceField(
        choices=[
            ('activate', _('Activate')),
            ('deactivate', _('Deactivate')),
            ('approve', _('Approve')),
            ('unapprove', _('Unapprove')),
            ('feature', _('Feature')),
            ('unfeature', _('Unfeature')),
            ('delete', _('Delete')),
        ],
        help_text=_("Action to perform on selected products")
    )
    
    def validate(self, data):
        """Validate bulk action data."""
        user = self.context['request'].user
        action = data['action']
        
        # Check permissions based on action
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Only admins can perform certain actions
        admin_only_actions = ['approve', 'unapprove', 'delete']
        if action in admin_only_actions and 'ADMIN' not in role_names and 'SUPER_ADMIN' not in role_names:
            raise ValidationError(_("You don't have permission to perform this action."))
        
        # Staff and managers can perform most actions except delete
        if action == 'delete' and not any(role in role_names for role in ['ADMIN', 'SUPER_ADMIN']):
            raise ValidationError(_("Only administrators can delete products."))
        
        return data


class ProductCartSerializer(serializers.ModelSerializer):
    """Minimal serializer for cart operations."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    basic_pricing = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category_name',
            'available_quantity', 'deposit_amount', 'main_image_url',
            'basic_pricing', 'is_rentable', 'minimum_rental_duration'
        ]
        read_only_fields = ['id']
    
    def get_main_image_url(self, obj):
        """Get main image URL."""
        if obj.main_image:
            return self.context['request'].build_absolute_uri(obj.main_image.url)
        return None
    
    def get_basic_pricing(self, obj):
        """Get basic pricing information for cart."""
        try:
            # Get the most common pricing rule (REGULAR customer, DAILY duration)
            pricing_rule = obj.pricing_rules.filter(
                customer_type='REGULAR',
                duration_type='DAILY'
            ).first()
            
            if not pricing_rule:
                # Fallback to any available pricing rule
                pricing_rule = obj.pricing_rules.filter(is_active=True).first()
            
            if pricing_rule:
                return {
                    'daily_rate': str(pricing_rule.daily_rate) if pricing_rule.daily_rate else str(pricing_rule.base_price),
                    'setup_fee': str(pricing_rule.setup_fee),
                    'delivery_fee': str(pricing_rule.delivery_fee),
                    'currency': 'USD'
                }
            
            return {
                'daily_rate': None,
                'setup_fee': '0.00',
                'delivery_fee': '0.00',
                'currency': 'USD'
            }
        except Exception:
            return {
                'daily_rate': None,
                'setup_fee': '0.00',
                'delivery_fee': '0.00',
                'currency': 'USD'
            }


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer for search results with minimal information."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    basic_pricing = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'short_description',
            'condition', 'status', 'available_quantity', 'deposit_amount',
            'main_image_url', 'average_rating', 'review_count',
            'basic_pricing', 'is_featured', 'admin_approved'
        ]
        read_only_fields = ['id']
    
    def get_main_image_url(self, obj):
        """Get main image URL."""
        if obj.main_image:
            return self.context['request'].build_absolute_uri(obj.main_image.url)
        return None
    
    def get_average_rating(self, obj):
        """Get average rating for the product."""
        cache_key = cache_key_generator('product_avg_rating', str(obj.id))
        cached_rating = get_cache_data(cache_key)
        
        if cached_rating is not None:
            return cached_rating
        
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            set_cache_data(cache_key, round(avg_rating, 1), timeout=600)
            return round(avg_rating, 1)
        return 0.0
    
    def get_review_count(self, obj):
        """Get count of approved reviews."""
        cache_key = cache_key_generator('product_review_count', str(obj.id))
        cached_count = get_cache_data(cache_key)
        
        if cached_count is not None:
            return cached_count
        
        count = obj.reviews.filter(is_approved=True).count()
        set_cache_data(cache_key, count, timeout=600)
        return count
    
    def get_basic_pricing(self, obj):
        """Get basic pricing information for search results."""
        try:
            # Get the most common pricing rule (REGULAR customer, DAILY duration)
            pricing_rule = obj.pricing_rules.filter(
                customer_type='REGULAR',
                duration_type='DAILY'
            ).first()
            
            if not pricing_rule:
                # Fallback to any available pricing rule
                pricing_rule = obj.pricing_rules.filter(is_active=True).first()
            
            if pricing_rule:
                return {
                    'daily_rate': str(pricing_rule.daily_rate) if pricing_rule.daily_rate else str(pricing_rule.base_price),
                    'currency': 'USD'
                }
            
            return {
                'daily_rate': None,
                'currency': 'USD'
            }
        except Exception:
            return {
                'daily_rate': None,
                'currency': 'USD'
            }