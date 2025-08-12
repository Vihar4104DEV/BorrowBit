"""
Django management command to generate sample product data.

This command creates:
- Product categories with hierarchical structure
- Products with realistic attributes
- Product pricing rules for different customer types
- Product reviews with ratings
- Product maintenance records

Usage:
    python manage.py generate_sample_products [--count=50] [--clear]
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker
from datetime import timedelta

from products.models import (
    ProductCategory, Product, ProductPricing, 
    ProductReview, ProductMaintenance
)
from user.models import UserRole

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generate sample product data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of products to generate (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before generating new data'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=15,
            help='Number of categories to generate (default: 15)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']
        category_count = options['categories']

        self.stdout.write(
            self.style.SUCCESS(f'Starting to generate {count} products with {category_count} categories...')
        )

        try:
            with transaction.atomic():
                if clear_existing:
                    self.clear_existing_data()
                
                # Generate categories first
                categories = self.generate_categories(category_count)
                
                # Generate products
                products = self.generate_products(count, categories)
                
                # Generate pricing rules
                self.generate_pricing_rules(products)
                
                # Generate reviews
                self.generate_reviews(products)
                
                # Generate maintenance records
                self.generate_maintenance_records(products)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully generated:\n'
                        f'- {len(categories)} categories\n'
                        f'- {len(products)} products\n'
                        f'- Pricing rules for all products\n'
                        f'- Reviews for products\n'
                        f'- Maintenance records for products'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating sample data: {str(e)}')
            )
            raise

    def clear_existing_data(self):
        """Clear existing sample data."""
        self.stdout.write('Clearing existing sample data...')
        
        # Clear in reverse dependency order
        ProductMaintenance.objects.all().delete()
        ProductReview.objects.all().delete()
        ProductPricing.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        
        self.stdout.write('Existing sample data cleared.')

    def generate_categories(self, count):
        """Generate product categories with hierarchical structure."""
        categories = []
        
        # Main categories
        main_categories = [
            'Electronics', 'Tools & Equipment', 'Party & Events', 
            'Sports & Recreation', 'Home & Garden', 'Professional Services',
            'Transportation', 'Fashion & Accessories', 'Books & Media',
            'Health & Wellness', 'Construction', 'Agriculture',
            'Entertainment', 'Education', 'Business'
        ]
        
        for i, name in enumerate(main_categories[:count//2]):
            category = ProductCategory.objects.create(
                name=name,
                description=fake.text(max_nb_chars=200),
                icon=f'icon-{name.lower().replace(" ", "-")}',
                sort_order=i,
                is_featured=random.choice([True, False])
            )
            categories.append(category)
            self.stdout.write(f'Created main category: {name}')
        
        # Sub-categories
        sub_category_data = {
            'Electronics': ['Laptops', 'Smartphones', 'Cameras', 'Audio Equipment', 'Gaming Consoles'],
            'Tools & Equipment': ['Power Tools', 'Hand Tools', 'Garden Tools', 'Construction Tools', 'Cleaning Equipment'],
            'Party & Events': ['Tables & Chairs', 'Tents & Canopies', 'Audio Systems', 'Decorations', 'Catering Equipment'],
            'Sports & Recreation': ['Bicycles', 'Camping Gear', 'Fitness Equipment', 'Water Sports', 'Team Sports'],
            'Home & Garden': ['Furniture', 'Kitchen Appliances', 'Garden Tools', 'Cleaning Supplies', 'DIY Tools'],
            'Professional Services': ['Photography', 'Videography', 'DJ Services', 'Catering', 'Event Planning'],
            'Transportation': ['Cars', 'Motorcycles', 'Bicycles', 'Scooters', 'Boats'],
            'Fashion & Accessories': ['Formal Wear', 'Costumes', 'Jewelry', 'Bags', 'Shoes'],
            'Books & Media': ['Books', 'Magazines', 'DVDs', 'CDs', 'Digital Media'],
            'Health & Wellness': ['Fitness Equipment', 'Yoga Mats', 'Massage Chairs', 'Saunas', 'Exercise Bikes'],
            'Construction': ['Excavators', 'Cranes', 'Scaffolding', 'Concrete Mixers', 'Safety Equipment'],
            'Agriculture': ['Tractors', 'Irrigation Systems', 'Harvesting Tools', 'Greenhouse Equipment', 'Storage Silos'],
            'Entertainment': ['Karaoke Machines', 'Projectors', 'Gaming Systems', 'Musical Instruments', 'Party Games'],
            'Education': ['Projectors', 'Whiteboards', 'Computers', 'Lab Equipment', 'Educational Toys'],
            'Business': ['Office Furniture', 'Computers', 'Printers', 'Meeting Equipment', 'Presentation Tools']
        }
        
        for parent_name, sub_names in sub_category_data.items():
            try:
                parent = ProductCategory.objects.get(name=parent_name)
                for sub_name in sub_names:
                    if len(categories) < count:
                        sub_category = ProductCategory.objects.create(
                            name=sub_name,
                            parent=parent,
                            description=fake.text(max_nb_chars=150),
                            icon=f'icon-{sub_name.lower().replace(" ", "-")}',
                            sort_order=len(categories),
                            is_featured=random.choice([True, False])
                        )
                        categories.append(sub_category)
                        self.stdout.write(f'Created sub-category: {sub_name} under {parent_name}')
            except ProductCategory.DoesNotExist:
                continue
        
        return categories

    def generate_products(self, count, categories):
        """Generate products with realistic attributes."""
        products = []
        
        # Get or create a default user for product ownership
        default_user = self.get_or_create_default_user()
        
        # Product templates for different categories
        product_templates = {
            'Electronics': {
                'names': ['Professional Laptop', 'High-End Smartphone', 'DSLR Camera', 'Wireless Headphones', 'Gaming Console'],
                'conditions': ['NEW', 'EXCELLENT', 'GOOD'],
                'materials': ['Aluminum', 'Plastic', 'Glass', 'Metal'],
                'brands': ['Apple', 'Samsung', 'Sony', 'Canon', 'Nintendo']
            },
            'Tools & Equipment': {
                'names': ['Power Drill', 'Circular Saw', 'Garden Rake', 'Safety Helmet', 'Work Gloves'],
                'conditions': ['EXCELLENT', 'GOOD', 'FAIR'],
                'materials': ['Steel', 'Plastic', 'Rubber', 'Aluminum'],
                'brands': ['DeWalt', 'Makita', 'Black & Decker', 'Stanley', 'Milwaukee']
            },
            'Party & Events': {
                'names': ['Folding Table', 'Party Tent', 'PA System', 'LED Lights', 'Champagne Glasses'],
                'conditions': ['EXCELLENT', 'GOOD', 'FAIR'],
                'materials': ['Plastic', 'Fabric', 'Metal', 'Glass'],
                'brands': ['Coleman', 'Eureka', 'JBL', 'Philips', 'Libbey']
            },
            'Sports & Recreation': {
                'names': ['Mountain Bike', 'Camping Tent', 'Treadmill', 'Kayak', 'Basketball'],
                'conditions': ['EXCELLENT', 'GOOD', 'FAIR'],
                'materials': ['Aluminum', 'Nylon', 'Rubber', 'Plastic'],
                'brands': ['Trek', 'North Face', 'Life Fitness', 'Pelican', 'Spalding']
            },
            'Home & Garden': {
                'names': ['Garden Chair', 'Kitchen Mixer', 'Hedge Trimmer', 'Vacuum Cleaner', 'Ladder'],
                'conditions': ['EXCELLENT', 'GOOD', 'FAIR'],
                'materials': ['Wood', 'Metal', 'Plastic', 'Fabric'],
                'brands': ['IKEA', 'KitchenAid', 'Black & Decker', 'Dyson', 'Werner']
            }
        }
        
        for i in range(count):
            # Select random category
            category = random.choice(categories)
            
            # Get template based on category or use generic
            template = product_templates.get(category.name, {
                'names': [f'Product {i+1}'],
                'conditions': ['EXCELLENT', 'GOOD', 'FAIR'],
                'materials': ['Metal', 'Plastic', 'Wood'],
                'brands': ['Generic Brand']
            })
            
            # Generate product name
            if category.parent:
                # Sub-category
                name = f"{random.choice(template['names'])} - {category.name}"
            else:
                # Main category
                name = f"{random.choice(template['names'])} for {category.name}"
            
            # Generate SKU
            sku = f"{category.name[:3].upper()}-{i+1:04d}-{random.randint(1000, 9999)}"
            
            # Generate slug
            slug = f"{name.lower().replace(' ', '-').replace('&', 'and')}-{i+1}"
            
            # Create product
            product = Product.objects.create(
                name=name,
                slug=slug,
                sku=sku,
                owner=default_user,
                category=category,
                short_description=fake.text(max_nb_chars=100),
                description=fake.text(max_nb_chars=500),
                specifications={
                    'weight': f"{random.uniform(0.5, 50.0):.1f} kg",
                    'dimensions': f"{random.randint(10, 200)} x {random.randint(10, 200)} x {random.randint(10, 200)} cm",
                    'color': random.choice(['Black', 'White', 'Silver', 'Blue', 'Red', 'Green']),
                    'material': random.choice(template['materials']),
                    'brand': random.choice(template['brands']),
                    'model': f"Model-{random.randint(100, 999)}"
                },
                features=[
                    'High Quality',
                    'Durable',
                    'Easy to Use',
                    'Professional Grade',
                    'Eco-Friendly'
                ],
                dimensions={
                    'length': random.randint(10, 200),
                    'width': random.randint(10, 200),
                    'height': random.randint(10, 200)
                },
                weight=Decimal(str(random.uniform(0.5, 50.0))),
                color=random.choice(['Black', 'White', 'Silver', 'Blue', 'Red', 'Green']),
                material=random.choice(template['materials']),
                brand=random.choice(template['brands']),
                model=f"Model-{random.randint(100, 999)}",
                condition=random.choice(template['conditions']),
                status='AVAILABLE',
                total_quantity=random.randint(1, 10),
                available_quantity=random.randint(1, 10),
                deposit_amount=Decimal(str(random.uniform(50.0, 500.0))),
                warehouse_location=f"Section {random.choice(['A', 'B', 'C'])}-{random.randint(1, 20)}",
                storage_requirements=fake.text(max_nb_chars=100),
                is_rentable=random.choice([True, True, True, False]),  # Mostly rentable
                minimum_rental_duration=random.choice([1, 2, 4, 8, 24]),  # Hours
                maximum_rental_duration=random.choice([168, 720, 2160, 8760]),  # Hours to weeks/months
                is_featured=random.choice([True, False, False, False]),  # 25% featured
                is_popular=random.choice([True, False, False, False]),  # 25% popular
                admin_approved=random.choice([True, True, True, False]),  # Mostly approved
                sort_order=i,
                purchase_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                warranty_expiry=timezone.now().date() + timedelta(days=random.randint(30, 730)),
                last_maintenance=timezone.now().date() - timedelta(days=random.randint(0, 90)),
                next_maintenance=timezone.now().date() + timedelta(days=random.randint(30, 180))
            )
            
            products.append(product)
            self.stdout.write(f'Created product: {name}')
        
        return products

    def generate_pricing_rules(self, products):
        """Generate pricing rules for products."""
        customer_types = ['REGULAR', 'CORPORATE', 'VIP', 'STAFF']
        duration_types = ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY']
        
        for product in products:
            # Generate multiple pricing rules for different customer types and durations
            for customer_type in customer_types:
                for duration_type in duration_types:
                    # Base pricing logic
                    if duration_type == 'HOURLY':
                        base_price = Decimal(str(random.uniform(5.0, 50.0)))
                        price_per_unit = base_price
                    elif duration_type == 'DAILY':
                        base_price = Decimal(str(random.uniform(20.0, 200.0)))
                        price_per_unit = base_price
                    elif duration_type == 'WEEKLY':
                        base_price = Decimal(str(random.uniform(100.0, 1000.0)))
                        price_per_unit = base_price
                    else:  # MONTHLY
                        base_price = Decimal(str(random.uniform(300.0, 3000.0)))
                        price_per_unit = base_price
                    
                    # Customer type discounts
                    if customer_type == 'CORPORATE':
                        discount_percentage = Decimal(str(random.uniform(5.0, 15.0)))
                    elif customer_type == 'VIP':
                        discount_percentage = Decimal(str(random.uniform(10.0, 25.0)))
                    elif customer_type == 'STAFF':
                        discount_percentage = Decimal(str(random.uniform(20.0, 40.0)))
                    else:  # REGULAR
                        discount_percentage = Decimal('0.0')
                    
                    # Create pricing rule
                    ProductPricing.objects.create(
                        product=product,
                        customer_type=customer_type,
                        duration_type=duration_type,
                        base_price=base_price,
                        price_per_unit=price_per_unit,
                        hourly_rate=base_price if duration_type == 'HOURLY' else None,
                        daily_rate=base_price if duration_type == 'DAILY' else None,
                        weekly_rate=base_price if duration_type == 'WEEKLY' else None,
                        monthly_rate=base_price if duration_type == 'MONTHLY' else None,
                        discount_percentage=discount_percentage,
                        bulk_discount_threshold=random.randint(5, 20),
                        bulk_discount_percentage=Decimal(str(random.uniform(5.0, 20.0))),
                        seasonal_multiplier=Decimal(str(random.uniform(0.8, 1.5))),
                        setup_fee=Decimal(str(random.uniform(0.0, 50.0))),
                        delivery_fee=Decimal(str(random.uniform(0.0, 100.0))),
                        late_return_fee_per_day=Decimal(str(random.uniform(5.0, 25.0))),
                        priority=random.randint(1, 10),
                        overrides_lower_priority=random.choice([True, False])
                    )
            
            self.stdout.write(f'Created pricing rules for: {product.name}')

    def generate_reviews(self, products):
        """Generate product reviews."""
        # Get or create some users for reviews
        users = self.get_or_create_review_users()
        
        for product in products:
            # Generate 1-5 reviews per product
            review_count = random.randint(1, 5)
            
            for i in range(review_count):
                user = random.choice(users)
                
                # Check if user already reviewed this product
                if not ProductReview.objects.filter(product=product, user=user).exists():
                    ProductReview.objects.create(
                        product=product,
                        user=user,
                        rating=random.randint(1, 5),
                        title=fake.sentence(nb_words=4),
                        comment=fake.text(max_nb_chars=200),
                        is_verified_purchase=random.choice([True, False]),
                        is_approved=random.choice([True, True, True, False])  # Mostly approved
                    )
            
            self.stdout.write(f'Created {review_count} reviews for: {product.name}')

    def generate_maintenance_records(self, products):
        """Generate maintenance records for products."""
        maintenance_types = ['PREVENTIVE', 'CORRECTIVE', 'INSPECTION', 'REPAIR', 'CLEANING']
        statuses = ['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        
        # Get or create some users for technicians
        technicians = self.get_or_create_technician_users()
        
        for product in products:
            # Generate 0-3 maintenance records per product
            maintenance_count = random.randint(0, 3)
            
            for i in range(maintenance_count):
                maintenance_type = random.choice(maintenance_types)
                status = random.choice(statuses)
                
                # Generate dates
                scheduled_date = timezone.now() + timedelta(days=random.randint(-30, 90))
                start_date = None
                completed_date = None
                
                if status in ['IN_PROGRESS', 'COMPLETED']:
                    start_date = scheduled_date + timedelta(days=random.randint(0, 7))
                
                if status == 'COMPLETED':
                    completed_date = start_date + timedelta(days=random.randint(1, 14))
                
                # Create maintenance record
                ProductMaintenance.objects.create(
                    product=product,
                    maintenance_type=maintenance_type,
                    status=status,
                    scheduled_date=scheduled_date,
                    start_date=start_date,
                    completed_date=completed_date,
                    description=fake.text(max_nb_chars=150),
                    technician_notes=fake.text(max_nb_chars=100) if status in ['IN_PROGRESS', 'COMPLETED'] else '',
                    cost=Decimal(str(random.uniform(50.0, 500.0))) if status == 'COMPLETED' else None,
                    assigned_technician=random.choice(technicians) if status != 'SCHEDULED' else None
                )
            
            if maintenance_count > 0:
                self.stdout.write(f'Created {maintenance_count} maintenance records for: {product.name}')

    def get_or_create_default_user(self):
        """Get or create a default user for product ownership."""
        try:
            user = User.objects.get(email='admin@example.com')
        except User.DoesNotExist:
            user = User.objects.create_user(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_verified=True,
                is_active=True
            )
            
            # Create admin role
            UserRole.objects.create(
                user=user,
                role='ADMIN',
                assigned_by=user,
                is_active=True
            )
            
            self.stdout.write('Created default admin user: admin@example.com')
        
        return user

    def get_or_create_review_users(self):
        """Get or create users for writing reviews."""
        users = []
        
        for i in range(10):
            email = f'user{i+1}@example.com'
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    password='user123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_verified=True,
                    is_active=True
                )
                
                # Create customer role
                UserRole.objects.create(
                    user=user,
                    role='CUSTOMER',
                    assigned_by=user,
                    is_active=True
                )
                
                self.stdout.write(f'Created review user: {email}')
            
            users.append(user)
        
        return users

    def get_or_create_technician_users(self):
        """Get or create users for technician roles."""
        technicians = []
        
        for i in range(5):
            email = f'tech{i+1}@example.com'
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    password='tech123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_verified=True,
                    is_active=True
                )
                
                # Create staff role
                UserRole.objects.create(
                    user=user,
                    role='STAFF',
                    assigned_by=user,
                    is_active=True
                )
                
                self.stdout.write(f'Created technician user: {email}')
            
            technicians.append(user)
        
        return technicians
