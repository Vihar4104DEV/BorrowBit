"""
Views for product management with role-based access control and caching.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Product, ProductCategory, ProductPricing, ProductImage, 
    ProductReview, ProductMaintenance
)
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductCategorySerializer, ProductPricingSerializer, ProductImageSerializer,
    ProductReviewSerializer, ProductMaintenanceSerializer, ProductBulkActionSerializer
)
from .permissions import (
    ProductListPermission, ProductDetailPermission, ProductCreatePermission,
    ProductUpdatePermission, ProductDeletePermission, ProductAdminPermission,
    ProductBulkActionPermission, ProductReviewPermission, ProductMaintenancePermission,
    ProductCategoryPermission, ProductPricingPermission, ProductImagePermission
)
from user.models import UserRole
from core.utils import (
    success_response, error_response, cache_key_generator, 
    set_cache_data, get_cache_data, delete_cache_data
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management with role-based access control.
    
    Provides CRUD operations for products with different permission levels:
    - Customers: Can view approved products, create reviews
    - Staff/Managers: Can manage products, view all products
    - Admins: Full access to all operations
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category', 'owner', 'condition', 'status', 'is_rentable', 
        'admin_approved', 'is_featured', 'is_popular', 'brand', 'material'
    ]
    search_fields = ['name', 'description', 'short_description', 'sku', 'brand', 'model']
    ordering_fields = ['name', 'created_at', 'updated_at', 'deposit_amount', 'available_quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role and permissions."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Product.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset
        queryset = Product.objects.select_related('category', 'owner').prefetch_related(
            'pricing_rules', 'product_images', 'reviews'
        ).filter(is_deleted=False)
        
        # Admin and Super Admin can see all products
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names:
            return queryset
        
        # Staff and Manager can see all products
        if 'STAFF' in role_names or 'MANAGER' in role_names:
            return queryset
        
        # Customers can only see approved and active products
        if 'CUSTOMER' in role_names:
            return queryset.filter(admin_approved=True, is_active=True)
        
        # Product owners can see their own products
        return queryset.filter(owner=user)
    
    def get_serializer_class(self):
        """Get appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action == 'list':
            permission_classes = [ProductListPermission]
        elif self.action == 'retrieve':
            permission_classes = [ProductDetailPermission]
        elif self.action == 'create':
            permission_classes = [ProductCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [ProductUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [ProductDeletePermission]
        elif self.action in ['approve', 'unapprove', 'feature', 'unfeature']:
            permission_classes = [ProductAdminPermission]
        elif self.action == 'bulk_action':
            permission_classes = [ProductBulkActionPermission]
        else:
            permission_classes = [ProductListPermission]
        
        return [permission() for permission in permission_classes]
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """List products with caching and role-based filtering."""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve product details with caching."""
        product_id = kwargs.get('pk')
        cache_key = cache_key_generator('product_detail', str(product_id))
        
        # Try to get from cache
        cached_data = get_cache_data(cache_key)
        if cached_data:
            return success_response("Product retrieved successfully", cached_data)
        
        # Get from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the response
        set_cache_data(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        
        return response
    
    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        product = serializer.save()
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response(
            "Product created successfully. Pending admin approval.",
            ProductDetailSerializer(product, context={'request': request}).data
        )
    
    def update(self, request, *args, **kwargs):
        """Update an existing product."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        product = serializer.save()
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response(
            "Product updated successfully",
            ProductDetailSerializer(product, context={'request': request}).data
        )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a product."""
        product = self.get_object()
        product.soft_delete()
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response("Product deleted successfully")
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a product (admin only)."""
        product = self.get_object()
        product.admin_approved = True
        product.save(update_fields=['admin_approved', 'updated_at'])
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response("Product approved successfully")
    
    @action(detail=True, methods=['post'])
    def unapprove(self, request, pk=None):
        """Unapprove a product (admin only)."""
        product = self.get_object()
        product.admin_approved = False
        product.save(update_fields=['admin_approved', 'updated_at'])
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response("Product unapproved successfully")
    
    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """Feature a product (admin only)."""
        product = self.get_object()
        product.is_featured = True
        product.save(update_fields=['is_featured', 'updated_at'])
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response("Product featured successfully")
    
    @action(detail=True, methods=['post'])
    def unfeature(self, request, pk=None):
        """Unfeature a product (admin only)."""
        product = self.get_object()
        product.is_featured = False
        product.save(update_fields=['is_featured', 'updated_at'])
        
        # Clear related caches
        self._clear_product_caches(product)
        
        return success_response("Product unfeatured successfully")
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on products."""
        serializer = ProductBulkActionSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(str(serializer.errors))
        
        validated_data = serializer.validated_data
        product_ids = validated_data['product_ids']
        action = validated_data['action']
        
        products = Product.objects.filter(id__in=product_ids)
        updated_count = 0
        
        for product in products:
            if action == 'activate':
                product.is_active = True
                product.save(update_fields=['is_active', 'updated_at'])
                updated_count += 1
            elif action == 'deactivate':
                product.is_active = False
                product.save(update_fields=['is_active', 'updated_at'])
                updated_count += 1
            elif action == 'approve':
                product.admin_approved = True
                product.save(update_fields=['admin_approved', 'updated_at'])
                updated_count += 1
            elif action == 'unapprove':
                product.admin_approved = False
                product.save(update_fields=['admin_approved', 'updated_at'])
                updated_count += 1
            elif action == 'feature':
                product.is_featured = True
                product.save(update_fields=['is_featured', 'updated_at'])
                updated_count += 1
            elif action == 'unfeature':
                product.is_featured = False
                product.save(update_fields=['is_featured', 'updated_at'])
                updated_count += 1
            elif action == 'delete':
                product.soft_delete()
                updated_count += 1
            
            # Clear product caches
            self._clear_product_caches(product)
        
        return success_response(f"Bulk action '{action}' completed on {updated_count} products")
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        cache_key = cache_key_generator('featured_products', 'list')
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return success_response("Featured products retrieved successfully", cached_data)
        
        products = self.get_queryset().filter(
            is_featured=True, 
            admin_approved=True, 
            is_active=True
        )[:10]
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        data = serializer.data
        
        # Cache the response
        set_cache_data(cache_key, data, timeout=600)  # Cache for 10 minutes
        
        return success_response("Featured products retrieved successfully", data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular products based on reviews and rentals."""
        cache_key = cache_key_generator('popular_products', 'list')
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return success_response("Popular products retrieved successfully", cached_data)
        
        products = self.get_queryset().filter(
            admin_approved=True, 
            is_active=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            avg_rating__gte=4.0,
            review_count__gte=1
        ).order_by('-avg_rating', '-review_count')[:10]
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        data = serializer.data
        
        # Cache the response
        set_cache_data(cache_key, data, timeout=600)  # Cache for 10 minutes
        
        return success_response("Popular products retrieved successfully", data)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get current user's products."""
        products = self.get_queryset().filter(owner=request.user)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return success_response("Your products retrieved successfully", serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for products."""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        condition = request.query_params.get('condition')
        
        queryset = self.get_queryset().filter(admin_approved=True, is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(brand__icontains=query) |
                Q(model__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Price filtering would need to be implemented based on pricing rules
        # This is a simplified version
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return success_response("Search results retrieved successfully", serializer.data)
    
    def _clear_product_caches(self, product):
        """Clear all caches related to a product."""
        # Clear product detail cache
        cache_key = cache_key_generator('product_detail', str(product.id))
        delete_cache_data(cache_key)
        
        # Clear category products count cache
        cache_key = cache_key_generator('category_products_count', str(product.category.id))
        delete_cache_data(cache_key)
        
        # Clear product rating cache
        cache_key = cache_key_generator('product_avg_rating', str(product.id))
        delete_cache_data(cache_key)
        
        # Clear product review count cache
        cache_key = cache_key_generator('product_review_count', str(product.id))
        delete_cache_data(cache_key)
        
        # Clear featured and popular products cache
        cache.delete('featured_products:list')
        cache.delete('popular_products:list')


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for product categories."""
    
    queryset = ProductCategory.objects.filter(is_active=True, is_deleted=False)
    serializer_class = ProductCategorySerializer
    permission_classes = [ProductCategoryPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order']
    ordering = ['sort_order', 'name']
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def list(self, request, *args, **kwargs):
        """List categories with caching."""
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure."""
        cache_key = cache_key_generator('category_tree', 'structure')
        cached_data = get_cache_data(cache_key)
        
        if cached_data:
            return success_response("Category tree retrieved successfully", cached_data)
        
        # Get root categories (no parent)
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        data = serializer.data
        
        # Cache the response
        set_cache_data(cache_key, data, timeout=1800)  # Cache for 30 minutes
        
        return success_response("Category tree retrieved successfully", data)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for product reviews."""
    
    serializer_class = ProductReviewSerializer
    permission_classes = [ProductReviewPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_approved']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return ProductReview.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        queryset = ProductReview.objects.select_related('user', 'product')
        
        # Admins and staff can see all reviews
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Users can see approved reviews and their own reviews
        return queryset.filter(
            Q(is_approved=True) | Q(user=user)
        )
    
    def perform_create(self, serializer):
        """Create a review and clear related caches."""
        review = serializer.save(user=self.request.user)
        
        # Clear product rating caches
        cache_key = cache_key_generator('product_avg_rating', str(review.product.id))
        delete_cache_data(cache_key)
        
        cache_key = cache_key_generator('product_review_count', str(review.product.id))
        delete_cache_data(cache_key)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a review (admin only)."""
        review = self.get_object()
        review.is_approved = True
        review.save(update_fields=['is_approved', 'updated_at'])
        
        # Clear product rating caches
        cache_key = cache_key_generator('product_avg_rating', str(review.product.id))
        delete_cache_data(cache_key)
        
        cache_key = cache_key_generator('product_review_count', str(review.product.id))
        delete_cache_data(cache_key)
        
        return success_response("Review approved successfully")
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a review (admin only)."""
        review = self.get_object()
        review.is_approved = False
        review.save(update_fields=['is_approved', 'updated_at'])
        
        # Clear product rating caches
        cache_key = cache_key_generator('product_avg_rating', str(review.product.id))
        delete_cache_data(cache_key)
        
        cache_key = cache_key_generator('product_review_count', str(review.product.id))
        delete_cache_data(cache_key)
        
        return success_response("Review rejected successfully")


class ProductPricingViewSet(viewsets.ModelViewSet):
    """ViewSet for product pricing."""
    
    serializer_class = ProductPricingSerializer
    permission_classes = [ProductPricingPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'customer_type', 'duration_type']
    ordering_fields = ['priority', 'created_at']
    ordering = ['priority', 'created_at']
    
    def get_queryset(self):
        """Get queryset based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return ProductPricing.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        queryset = ProductPricing.objects.select_related('product')
        
        # Admins and staff can see all pricing
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Product owners can see their own product pricing
        return queryset.filter(product__owner=user)


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for product images."""
    
    serializer_class = ProductImageSerializer
    permission_classes = [ProductImagePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'is_primary']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'created_at']
    
    def get_queryset(self):
        """Get queryset based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return ProductImage.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        queryset = ProductImage.objects.select_related('product')
        
        # Admins and staff can see all images
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Product owners can see their own product images
        return queryset.filter(product__owner=user)


class ProductMaintenanceViewSet(viewsets.ModelViewSet):
    """ViewSet for product maintenance."""
    
    serializer_class = ProductMaintenanceSerializer
    permission_classes = [ProductMaintenancePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'maintenance_type', 'status', 'assigned_technician']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['-scheduled_date']
    
    def get_queryset(self):
        """Get queryset based on user role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return ProductMaintenance.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        queryset = ProductMaintenance.objects.select_related('product', 'assigned_technician')
        
        # Admins and staff can see all maintenance records
        if 'ADMIN' in role_names or 'SUPER_ADMIN' in role_names or 'STAFF' in role_names:
            return queryset
        
        # Product owners can see maintenance for their own products
        return queryset.filter(product__owner=user)
    
    @action(detail=True, methods=['post'])
    def start_maintenance(self, request, pk=None):
        """Start maintenance process."""
        maintenance = self.get_object()
        maintenance.start_maintenance()
        
        return success_response("Maintenance started successfully")
    
    @action(detail=True, methods=['post'])
    def complete_maintenance(self, request, pk=None):
        """Complete maintenance process."""
        maintenance = self.get_object()
        maintenance.complete_maintenance()
        
        return success_response("Maintenance completed successfully")
