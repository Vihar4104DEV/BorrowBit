"""
Views for product management with role-based access control and caching.

This module provides comprehensive CRUD operations for products, categories, pricing,
reviews, images, and maintenance records with proper permission handling and
caching strategies.
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
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Product, ProductCategory, ProductPricing, ProductImage, 
    ProductReview, ProductMaintenance
)
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductCategorySerializer, ProductPricingSerializer, ProductImageSerializer,
    ProductReviewSerializer, ProductMaintenanceSerializer, ProductBulkActionSerializer,
    ProductSearchSerializer, ProductCartSerializer
)
from .permissions import (
    ProductListPermission, ProductDetailPermission, ProductCreatePermission,
    ProductUpdatePermission, ProductDeletePermission, ProductAdminPermission,
    ProductBulkActionPermission, ProductReviewPermission, ProductMaintenancePermission,
    ProductCategoryPermission, ProductPricingPermission, ProductImagePermission
)
from user.models import UserRole
from core.utils import (
    success_response, error_response, validation_error_response, cache_key_generator, 
    set_cache_data, get_cache_data, delete_cache_data
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management with role-based access control.
    
    Provides CRUD operations for products with different permission levels:
    - Customers: Can view approved products, create reviews
    - Staff/Managers: Can manage products, view all products
    - Admins: Full access to all operations
    
    Features:
    - Role-based access control
    - Caching for performance
    - Bulk operations
    - Advanced search and filtering
    - Featured and popular products
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
        """
        Get queryset based on user role and permissions.
        
        Returns:
            QuerySet: Filtered products based on user role and permissions
        """
        user = self.request.user
        
        if not user.is_authenticated:
            return Product.objects.none()
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        role_names = [role.role for role in user_roles]
        
        # Base queryset with optimized select_related and prefetch_related
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
        """
        Get appropriate serializer based on action.
        
        Returns:
            Serializer class: Appropriate serializer for the current action
        """
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        elif self.action == 'search':
            return ProductSearchSerializer
        elif self.action in ['cart_info', 'add_to_cart']:
            return ProductCartSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        """
        Get permissions based on action.
        
        Returns:
            list: List of permission classes for the current action
        """
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
    
    def list(self, request, *args, **kwargs):
        """
        List products with caching and role-based filtering.
        
        Returns:
            Response: Standardized response with product list
        """
        try:
            # Check cache first
            cache_key = cache_key_generator('product_list', request.user.id if request.user.is_authenticated else 'anonymous')
            # cached_data = get_cache_data(cache_key)
            
            if False:
                return success_response("Products retrieved successfully (from cache)", cached_data)
            
            # Get from database
            response = super().list(request, *args, **kwargs)
            
            # Cache the response data
            set_cache_data(cache_key, response.data, timeout=300)  # Cache for 5 minutes
            
            return success_response("Products retrieved successfully", response.data)
        except Exception as e:
            return error_response(f"Error retrieving products: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve product details with caching.
        
        Returns:
            Response: Standardized response with product details
        """
        try:
            product_id = kwargs.get('pk')
            cache_key = cache_key_generator('product_detail', str(product_id))
            
            # Try to get from cache
            cached_data = get_cache_data(cache_key)
            if cached_data:
                return success_response("Product retrieved successfully", cached_data)
            
            # Get from database
            response = super().retrieve(request, *args, **kwargs)
            
            # Cache the response data (not the Response object)
            set_cache_data(cache_key, response.data, timeout=300)  # Cache for 5 minutes
            
            return success_response("Product retrieved successfully", response.data)
        except Exception as e:
            return error_response(f"Error retrieving product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product.
        
        Returns:
            Response: Standardized response with created product data
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            
            with transaction.atomic():
                product = serializer.save(owner=request.user)
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response(
                    "Product created successfully. Pending admin approval.",
                    ProductDetailSerializer(product, context={'request': request}).data
                )
        except ValidationError as e:
            return validation_error_response(e.message_dict if hasattr(e, 'message_dict') else str(e))
        except Exception as e:
            return error_response(f"Error creating product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing product.
        
        Returns:
            Response: Standardized response with updated product data
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            
            with transaction.atomic():
                product = serializer.save()
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response(
                    "Product updated successfully",
                    ProductDetailSerializer(product, context={'request': request}).data
                )
        except ValidationError as e:
            return validation_error_response(e.message_dict if hasattr(e, 'message_dict') else str(e))
        except Exception as e:
            return error_response(f"Error updating product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a product.
        
        Returns:
            Response: Standardized response confirming deletion
        """
        try:
            product = self.get_object()
            
            with transaction.atomic():
                product.soft_delete()
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response("Product deleted successfully")
        except Exception as e:
            return error_response(f"Error deleting product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a product (admin only).
        
        Returns:
            Response: Standardized response confirming approval
        """
        try:
            product = self.get_object()
            
            with transaction.atomic():
                product.admin_approved = True
                product.save(update_fields=['admin_approved', 'updated_at'])
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response("Product approved successfully")
        except Exception as e:
            return error_response(f"Error approving product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def unapprove(self, request, pk=None):
        """
        Unapprove a product (admin only).
        
        Returns:
            Response: Standardized response confirming unapproval
        """
        try:
            product = self.get_object()
            
            with transaction.atomic():
                product.admin_approved = False
                product.save(update_fields=['admin_approved', 'updated_at'])
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response("Product unapproved successfully")
        except Exception as e:
            return error_response(f"Error unapproving product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """
        Feature a product (admin only).
        
        Returns:
            Response: Standardized response confirming featuring
        """
        try:
            product = self.get_object()
            
            with transaction.atomic():
                product.is_featured = True
                product.save(update_fields=['is_featured', 'updated_at'])
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response("Product featured successfully")
        except Exception as e:
            return error_response(f"Error featuring product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def unfeature(self, request, pk=None):
        """
        Unfeature a product (admin only).
        
        Returns:
            Response: Standardized response confirming unfeaturing
        """
        try:
            product = self.get_object()
            
            with transaction.atomic():
                product.is_featured = False
                product.save(update_fields=['is_featured', 'updated_at'])
                
                # Clear related caches
                self._clear_product_caches(product)
                
                return success_response("Product unfeatured successfully")
        except Exception as e:
            return error_response(f"Error unfeaturing product: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """
        Perform bulk actions on products.
        
        Returns:
            Response: Standardized response with action results
        """
        try:
            serializer = ProductBulkActionSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return validation_error_response(serializer.errors)
            
            validated_data = serializer.validated_data
            product_ids = validated_data['product_ids']
            action = validated_data['action']
            
            products = Product.objects.filter(id__in=product_ids)
            updated_count = 0
            
            with transaction.atomic():
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
        except Exception as e:
            return error_response(f"Error performing bulk action: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products.
        
        Returns:
            Response: Standardized response with featured products
        """
        try:
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
            
            # Cache the response data
            set_cache_data(cache_key, data, timeout=600)  # Cache for 10 minutes
            
            return success_response("Featured products retrieved successfully", data)
        except Exception as e:
            return error_response(f"Error retrieving featured products: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Get popular products based on reviews and rentals.
        
        Returns:
            Response: Standardized response with popular products
        """
        try:
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
            
            # Cache the response data
            set_cache_data(cache_key, data, timeout=600)  # Cache for 10 minutes
            
            return success_response("Popular products retrieved successfully", data)
        except Exception as e:
            return error_response(f"Error retrieving popular products: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """
        Get current user's products.
        
        Returns:
            Response: Standardized response with user's products
        """
        try:
            products = self.get_queryset().filter(owner=request.user)
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return success_response("Your products retrieved successfully", serializer.data)
        except Exception as e:
            return error_response(f"Error retrieving your products: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def cart_info(self, request, pk=None):
        """
        Get product information specifically for cart operations.
        
        Returns:
            Response: Standardized response with cart-specific product data
        """
        try:
            product = self.get_object()
            serializer = ProductCartSerializer(product, context={'request': request})
            return success_response("Product cart information retrieved successfully", serializer.data)
        except Exception as e:
            return error_response(f"Error retrieving product cart information: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def bulk_cart_info(self, request):
        """
        Get cart information for multiple products.
        
        Returns:
            Response: Standardized response with cart information for multiple products
        """
        try:
            product_ids = request.data.get('product_ids', [])
            if not product_ids:
                return error_response("Product IDs are required", status.HTTP_400_BAD_REQUEST)
            
            products = self.get_queryset().filter(id__in=product_ids)
            serializer = ProductCartSerializer(products, many=True, context={'request': request})
            return success_response("Bulk cart information retrieved successfully", serializer.data)
        except Exception as e:
            return error_response(f"Error retrieving bulk cart information: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search for products.
        
        Returns:
            Response: Standardized response with search results
        """
        try:
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
            
            # Use search serializer for focused results
            serializer = ProductSearchSerializer(queryset, many=True, context={'request': request})
            return success_response("Search results retrieved successfully", serializer.data)
        except Exception as e:
            return error_response(f"Error performing search: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _clear_product_caches(self, product):
        """
        Clear all caches related to a product.
        
        Args:
            product: Product instance to clear caches for
        """
        try:
            # Clear product detail cache
            cache_key = cache_key_generator('product_detail', str(product.id))
            delete_cache_data(cache_key)
            
            # Clear product list caches for all users
            cache.delete('product_list:anonymous')
            if product.owner:
                cache_key = cache_key_generator('product_list', str(product.owner.id))
                delete_cache_data(cache_key)
            
            # Clear category products count cache
            if product.category:
                cache_key = cache_key_generator('category_products_count', str(product.category.id))
                delete_cache_data(cache_key)
                
                # Clear category list cache
                cache.delete('category_list:anonymous')
                if product.owner:
                    cache_key = cache_key_generator('category_list', str(product.owner.id))
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
        except Exception:
            # Log cache clearing errors but don't fail the main operation
            pass


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product categories.
    
    Provides CRUD operations for product categories with hierarchical structure
    and caching for improved performance.
    """
    
    queryset = ProductCategory.objects.filter(is_active=True, is_deleted=False)
    serializer_class = ProductCategorySerializer
    permission_classes = [ProductCategoryPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order']
    ordering = ['sort_order', 'name']
    
    def list(self, request, *args, **kwargs):
        """
        List categories with caching.
        
        Returns:
            Response: Standardized response with category list
        """
        try:
            # Check cache first
            cache_key = cache_key_generator('category_list', request.user.id if request.user.is_authenticated else 'anonymous')
            cached_data = get_cache_data(cache_key)
            
            if cached_data:
                return success_response("Categories retrieved successfully (from cache)", cached_data)
            
            # Get from database
            response = super().list(request, *args, **kwargs)
            
            # Cache the response data
            set_cache_data(cache_key, response.data, timeout=600)  # Cache for 10 minutes
            
            return success_response("Categories retrieved successfully", response.data)
        except Exception as e:
            return error_response(f"Error retrieving categories: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get category tree structure.
        
        Returns:
            Response: Standardized response with category tree
        """
        try:
            cache_key = cache_key_generator('category_tree', 'structure')
            cached_data = get_cache_data(cache_key)
            
            if cached_data:
                return success_response("Category tree retrieved successfully", cached_data)
            
            # Get root categories (no parent)
            root_categories = self.get_queryset().filter(parent__isnull=True)
            serializer = self.get_serializer(root_categories, many=True)
            data = serializer.data
            
            # Cache the response data
            set_cache_data(cache_key, data, timeout=1800)  # Cache for 30 minutes
            
            return success_response("Category tree retrieved successfully", data)
        except Exception as e:
            return error_response(f"Error retrieving category tree: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product reviews.
    
    Provides CRUD operations for product reviews with approval workflow
    and role-based access control.
    """
    
    serializer_class = ProductReviewSerializer
    permission_classes = [ProductReviewPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_approved']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get queryset based on user role.
        
        Returns:
            QuerySet: Filtered reviews based on user role and permissions
        """
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
        """
        Create a review and clear related caches.
        
        Args:
            serializer: Review serializer instance
        """
        try:
            review = serializer.save(user=self.request.user)
            
            # Clear product rating caches
            cache_key = cache_key_generator('product_avg_rating', str(review.product.id))
            delete_cache_data(cache_key)
            
            cache_key = cache_key_generator('product_review_count', str(review.product.id))
            delete_cache_data(cache_key)
        except Exception:
            # Log cache clearing errors but don't fail the main operation
            pass
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a review (admin only).
        
        Returns:
            Response: Standardized response confirming approval
        """
        try:
            review = self.get_object()
            
            with transaction.atomic():
                review.is_approved = True
                review.save(update_fields=['is_approved', 'updated_at'])
                
                # Clear product rating caches
                self._clear_review_caches(review)
                
                return success_response("Review approved successfully")
        except Exception as e:
            return error_response(f"Error approving review: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a review (admin only).
        
        Returns:
            Response: Standardized response confirming rejection
        """
        try:
            review = self.get_object()
            
            with transaction.atomic():
                review.is_approved = False
                review.save(update_fields=['is_approved', 'updated_at'])
                
                # Clear product rating caches
                self._clear_review_caches(review)
                
                return success_response("Review rejected successfully")
        except Exception as e:
            return error_response(f"Error rejecting review: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _clear_review_caches(self, review):
        """
        Clear caches related to a review.
        
        Args:
            review: Review instance to clear caches for
        """
        try:
            # Clear product rating caches
            cache_key = cache_key_generator('product_avg_rating', str(review.product.id))
            delete_cache_data(cache_key)
            
            cache_key = cache_key_generator('product_review_count', str(review.product.id))
            delete_cache_data(cache_key)
            
            # Clear product list caches since reviews affect product data
            cache.delete('product_list:anonymous')
            if review.product.owner:
                cache_key = cache_key_generator('product_list', str(review.product.owner.id))
                delete_cache_data(cache_key)
            
            # Clear popular products cache since ratings affect popularity
            cache.delete('popular_products:list')
        except Exception:
            # Log cache clearing errors but don't fail the main operation
            pass


class ProductPricingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product pricing.
    
    Provides CRUD operations for product pricing rules with role-based
    access control and flexible pricing strategies.
    """
    
    serializer_class = ProductPricingSerializer
    permission_classes = [ProductPricingPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'customer_type', 'duration_type']
    ordering_fields = ['priority', 'created_at']
    ordering = ['priority', 'created_at']
    
    def get_queryset(self):
        """
        Get queryset based on user role.
        
        Returns:
            QuerySet: Filtered pricing rules based on user role and permissions
        """
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
    """
    ViewSet for product images.
    
    Provides CRUD operations for product images with role-based
    access control and image management features.
    """
    
    serializer_class = ProductImageSerializer
    permission_classes = [ProductImagePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'is_primary']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'created_at']
    
    def get_queryset(self):
        """
        Get queryset based on user role.
        
        Returns:
            QuerySet: Filtered images based on user role and permissions
        """
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
    """
    ViewSet for product maintenance.
    
    Provides CRUD operations for product maintenance records with
    role-based access control and maintenance workflow management.
    """
    
    serializer_class = ProductMaintenanceSerializer
    permission_classes = [ProductMaintenancePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'maintenance_type', 'status', 'assigned_technician']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['-scheduled_date']
    
    def get_queryset(self):
        """
        Get queryset based on user role.
        
        Returns:
            QuerySet: Filtered maintenance records based on user role and permissions
        """
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
        """
        Start maintenance process.
        
        Returns:
            Response: Standardized response confirming maintenance start
        """
        try:
            maintenance = self.get_object()
            maintenance.start_maintenance()
            
            return success_response("Maintenance started successfully")
        except Exception as e:
            return error_response(f"Error starting maintenance: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def complete_maintenance(self, request, pk=None):
        """
        Complete maintenance process.
        
        Returns:
            Response: Standardized response confirming maintenance completion
        """
        try:
            maintenance = self.get_object()
            maintenance.complete_maintenance()
            
            return success_response("Maintenance completed successfully")
        except Exception as e:
            return error_response(f"Error completing maintenance: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)