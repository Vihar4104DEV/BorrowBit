"""
Test cases for product management with role-based access control.
"""
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import (
    Product, ProductCategory, ProductPricing, ProductImage, 
    ProductReview, ProductMaintenance
)
from user.models import UserRole

User = get_user_model()


class ProductModelTestCase(TestCase):
    """Test cases for Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices and gadgets'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.user,
            category=self.category,
            short_description='A test product',
            description='This is a test product for testing purposes',
            deposit_amount=Decimal('100.00'),
            total_quantity=5,
            available_quantity=5
        )
    
    def test_product_creation(self):
        """Test product creation."""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.owner, self.user)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.status, 'AVAILABLE')
        self.assertTrue(self.product.is_active)
        self.assertFalse(self.product.is_deleted)
    
    def test_product_soft_delete(self):
        """Test product soft delete."""
        self.product.soft_delete()
        self.assertFalse(self.product.is_active)
        self.assertTrue(self.product.is_deleted)
    
    def test_product_restore(self):
        """Test product restore."""
        self.product.soft_delete()
        self.product.restore()
        self.assertTrue(self.product.is_active)
        self.assertFalse(self.product.is_deleted)
    
    def test_product_reserve_quantity(self):
        """Test product quantity reservation."""
        initial_available = self.product.available_quantity
        initial_reserved = self.product.reserved_quantity
        
        success = self.product.reserve_quantity(2)
        self.assertTrue(success)
        self.assertEqual(self.product.available_quantity, initial_available - 2)
        self.assertEqual(self.product.reserved_quantity, initial_reserved + 2)
    
    def test_product_release_reservation(self):
        """Test product reservation release."""
        self.product.reserve_quantity(2)
        initial_available = self.product.available_quantity
        initial_reserved = self.product.reserved_quantity
        
        success = self.product.release_reservation(1)
        self.assertTrue(success)
        self.assertEqual(self.product.available_quantity, initial_available + 1)
        self.assertEqual(self.product.reserved_quantity, initial_reserved - 1)
    
    def test_product_status_update(self):
        """Test product status update based on availability."""
        self.product.available_quantity = 0
        self.product.reserved_quantity = 2
        self.product.update_status()
        self.assertEqual(self.product.status, 'RESERVED')
        
        self.product.reserved_quantity = 0
        self.product.update_status()
        self.assertEqual(self.product.status, 'RENTED')


class ProductCategoryModelTestCase(TestCase):
    """Test cases for ProductCategory model."""
    
    def setUp(self):
        """Set up test data."""
        self.parent_category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
        
        self.child_category = ProductCategory.objects.create(
            name='Smartphones',
            slug='smartphones',
            description='Mobile phones',
            parent=self.parent_category
        )
    
    def test_category_creation(self):
        """Test category creation."""
        self.assertEqual(self.child_category.name, 'Smartphones')
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertEqual(self.parent_category.children.count(), 1)
    
    def test_category_get_all_children(self):
        """Test getting all children recursively."""
        grandchild = ProductCategory.objects.create(
            name='Android Phones',
            slug='android-phones',
            parent=self.child_category
        )
        
        children = self.parent_category.get_all_children()
        self.assertEqual(len(children), 2)
        self.assertIn(self.child_category, children)
        self.assertIn(grandchild, children)


class ProductPricingModelTestCase(TestCase):
    """Test cases for ProductPricing model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.user,
            category=self.category,
            short_description='A test product',
            deposit_amount=Decimal('100.00')
        )
        
        self.pricing = ProductPricing.objects.create(
            product=self.product,
            customer_type='REGULAR',
            duration_type='DAILY',
            base_price=Decimal('50.00'),
            price_per_unit=Decimal('10.00'),
            daily_rate=Decimal('60.00')
        )
    
    def test_pricing_creation(self):
        """Test pricing creation."""
        self.assertEqual(self.pricing.product, self.product)
        self.assertEqual(self.pricing.customer_type, 'REGULAR')
        self.assertEqual(self.pricing.duration_type, 'DAILY')
    
    def test_pricing_calculation(self):
        """Test pricing calculation."""
        price = self.pricing.calculate_price(3)  # 3 days
        expected_price = Decimal('60.00') * 3  # daily_rate * duration
        self.assertEqual(price, expected_price)
    
    def test_pricing_with_discount(self):
        """Test pricing with discount."""
        self.pricing.discount_percentage = Decimal('10.00')
        price = self.pricing.calculate_price(1)
        expected_price = Decimal('60.00') * Decimal('0.90')  # 10% discount
        self.assertEqual(price, expected_price)


class ProductAPITestCase(APITestCase):
    """Test cases for Product API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            first_name='Staff',
            last_name='User'
        )
        
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123',
            first_name='Customer',
            last_name='User'
        )
        
        # Create user roles
        UserRole.objects.create(user=self.admin_user, role='ADMIN')
        UserRole.objects.create(user=self.staff_user, role='STAFF')
        UserRole.objects.create(user=self.customer_user, role='CUSTOMER')
        
        # Create category
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.admin_user,
            category=self.category,
            short_description='A test product',
            description='This is a test product',
            deposit_amount=Decimal('100.00'),
            total_quantity=5,
            available_quantity=5,
            admin_approved=True
        )
    
    def test_product_list_authenticated(self):
        """Test product list for authenticated users."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_product_list_unauthenticated(self):
        """Test product list for unauthenticated users."""
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_product_detail_customer(self):
        """Test product detail for customer."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Test Product')
    
    def test_product_detail_admin(self):
        """Test product detail for admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Test Product')
    
    def test_product_create_customer(self):
        """Test product creation by customer."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-list')
        data = {
            'name': 'New Product',
            'category': self.category.id,
            'short_description': 'A new product',
            'description': 'This is a new product',
            'deposit_amount': '150.00',
            'total_quantity': 3
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        
        # Check that the product is not approved by default
        new_product = Product.objects.get(name='New Product')
        self.assertFalse(new_product.admin_approved)
    
    def test_product_update_owner(self):
        """Test product update by owner."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Updated Product Name'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product Name')
    
    def test_product_update_non_owner(self):
        """Test product update by non-owner."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Unauthorized Update'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_product_approve_admin(self):
        """Test product approval by admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-approve', kwargs={'pk': self.product.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertTrue(self.product.admin_approved)
    
    def test_product_approve_customer(self):
        """Test product approval by customer (should fail)."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-approve', kwargs={'pk': self.product.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_product_featured(self):
        """Test featured products endpoint."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_product_search(self):
        """Test product search endpoint."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('product-search')
        response = self.client.get(url, {'q': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_my_products(self):
        """Test my products endpoint."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-my-products')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 1)


class ProductReviewAPITestCase(APITestCase):
    """Test cases for ProductReview API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123',
            first_name='Customer',
            last_name='User'
        )
        
        UserRole.objects.create(user=self.admin_user, role='ADMIN')
        UserRole.objects.create(user=self.customer_user, role='CUSTOMER')
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            owner=self.admin_user,
            category=self.category,
            short_description='A test product',
            deposit_amount=Decimal('100.00'),
            admin_approved=True
        )
    
    def test_review_create(self):
        """Test review creation."""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'rating': 5,
            'title': 'Great Product',
            'comment': 'This is an excellent product!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductReview.objects.count(), 1)
        
        review = ProductReview.objects.first()
        self.assertEqual(review.user, self.customer_user)
        self.assertEqual(review.product, self.product)
        self.assertFalse(review.is_approved)  # Reviews need approval by default
    
    def test_review_approve_admin(self):
        """Test review approval by admin."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.customer_user,
            rating=5,
            title='Great Product',
            comment='This is an excellent product!'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('review-approve', kwargs={'pk': review.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertTrue(review.is_approved)
    
    def test_review_duplicate(self):
        """Test duplicate review prevention."""
        ProductReview.objects.create(
            product=self.product,
            user=self.customer_user,
            rating=5,
            title='Great Product',
            comment='This is an excellent product!'
        )
        
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'rating': 4,
            'title': 'Another Review',
            'comment': 'This is another review'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductCategoryAPITestCase(APITestCase):
    """Test cases for ProductCategory API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        UserRole.objects.create(user=self.admin_user, role='ADMIN')
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
    
    def test_category_list(self):
        """Test category list endpoint."""
        url = reverse('category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_category_create_admin(self):
        """Test category creation by admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'A new category'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 2)
    
    def test_category_create_customer(self):
        """Test category creation by customer (should fail)."""
        customer_user = User.objects.create_user(
            email='customer@example.com',
            password='customerpass123',
            first_name='Customer',
            last_name='User'
        )
        UserRole.objects.create(user=customer_user, role='CUSTOMER')
        
        self.client.force_authenticate(user=customer_user)
        url = reverse('category-list')
        data = {
            'name': 'Unauthorized Category',
            'description': 'This should fail'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_category_tree(self):
        """Test category tree endpoint."""
        url = reverse('category-tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)


class ProductBulkActionTestCase(APITestCase):
    """Test cases for product bulk actions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            first_name='Staff',
            last_name='User'
        )
        
        UserRole.objects.create(user=self.admin_user, role='ADMIN')
        UserRole.objects.create(user=self.staff_user, role='STAFF')
        
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        # Create multiple products
        self.products = []
        for i in range(3):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                sku=f'TEST{i:03d}',
                owner=self.admin_user,
                category=self.category,
                short_description=f'Product {i} description',
                deposit_amount=Decimal('100.00'),
                total_quantity=5,
                available_quantity=5
            )
            self.products.append(product)
    
    def test_bulk_approve_admin(self):
        """Test bulk approve by admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-bulk-action')
        data = {
            'product_ids': [str(product.id) for product in self.products],
            'action': 'approve'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for product in self.products:
            product.refresh_from_db()
            self.assertTrue(product.admin_approved)
    
    def test_bulk_delete_admin(self):
        """Test bulk delete by admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-bulk-action')
        data = {
            'product_ids': [str(product.id) for product in self.products],
            'action': 'delete'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for product in self.products:
            product.refresh_from_db()
            self.assertTrue(product.is_deleted)
    
    def test_bulk_delete_staff(self):
        """Test bulk delete by staff (should fail)."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('product-bulk-action')
        data = {
            'product_ids': [str(product.id) for product in self.products],
            'action': 'delete'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_feature_staff(self):
        """Test bulk feature by staff."""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('product-bulk-action')
        data = {
            'product_ids': [str(product.id) for product in self.products],
            'action': 'feature'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for product in self.products:
            product.refresh_from_db()
            self.assertTrue(product.is_featured)
