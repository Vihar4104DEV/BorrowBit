# Products App

This Django app provides comprehensive product management functionality for a rental platform, including products, categories, pricing, reviews, and maintenance records.

## Features

- **Product Management**: CRUD operations for rental products
- **Category Management**: Hierarchical product categories
- **Pricing Rules**: Flexible pricing based on duration and customer type
- **Product Reviews**: Customer ratings and feedback system
- **Maintenance Tracking**: Product maintenance and repair records
- **Role-based Access Control**: Different permissions for different user roles
- **Caching**: Performance optimization with Redis caching
- **API Endpoints**: RESTful API with standardized responses

## API Endpoints

### Products
- `GET /api/products/` - List products (limited information for listing)
- `GET /api/products/{id}/` - Get product details (full information)
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `GET /api/products/featured/` - Get featured products
- `GET /api/products/popular/` - Get popular products
- `GET /api/products/my_products/` - Get user's own products
- `GET /api/products/search/` - Search products
- `GET /api/products/{id}/cart_info/` - Get product info for cart
- `POST /api/products/bulk_cart_info/` - Get cart info for multiple products

### Categories
- `GET /api/categories/` - List categories
- `GET /api/categories/tree/` - Get category tree structure

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `POST /api/reviews/{id}/approve/` - Approve review (admin)
- `POST /api/reviews/{id}/reject/` - Reject review (admin)

### Maintenance
- `GET /api/maintenance/` - List maintenance records
- `POST /api/maintenance/` - Create maintenance record
- `POST /api/maintenance/{id}/start_maintenance/` - Start maintenance
- `POST /api/maintenance/{id}/complete_maintenance/` - Complete maintenance

## Data Generation

Use the management command to generate sample data for testing and development:

```bash
# Generate 50 products with 15 categories (default)
python manage.py generate_sample_products

# Generate 100 products with 20 categories
python manage.py generate_sample_products --count=100 --categories=20

# Clear existing data and generate new data
python manage.py generate_sample_products --clear

# Generate only 25 products
python manage.py generate_sample_products --count=25
```

### What Gets Generated

1. **Categories**: Main categories with sub-categories
2. **Products**: Realistic products with various attributes
3. **Pricing Rules**: Multiple pricing rules per product (hourly, daily, weekly, monthly)
4. **Reviews**: 1-5 reviews per product with ratings
5. **Maintenance Records**: 0-3 maintenance records per product
6. **Users**: Admin, customer, and technician users with appropriate roles

### Sample Data Structure

- **Main Categories**: Electronics, Tools & Equipment, Party & Events, Sports & Recreation, Home & Garden, etc.
- **Sub-categories**: Laptops, Power Tools, Tents, Bicycles, Furniture, etc.
- **Product Attributes**: Name, description, specifications, dimensions, weight, condition, pricing
- **Pricing**: Different rates for different customer types (Regular, Corporate, VIP, Staff)
- **Reviews**: Ratings from 1-5 with realistic comments
- **Maintenance**: Various types (Preventive, Corrective, Inspection, Repair, Cleaning)

## Serializers

### ProductListSerializer
Shows essential information for product listings and cart operations:
- Basic product details
- Category and owner information
- Basic pricing (daily rate, setup fee, delivery fee)
- Rating and review count
- Availability status

### ProductDetailSerializer
Shows complete product information:
- All product fields
- Full pricing rules
- Complete review details
- Maintenance records
- Detailed specifications

### ProductCartSerializer
Minimal information for cart operations:
- Product ID, name, SKU
- Basic pricing
- Availability and rental constraints

### ProductSearchSerializer
Focused information for search results:
- Essential product details
- Basic pricing
- Rating and review summary

## Caching Strategy

- **Product List**: Cached per user (5 minutes)
- **Product Detail**: Cached per product (5 minutes)
- **Categories**: Cached per user (10 minutes)
- **Featured/Popular Products**: Cached globally (10 minutes)
- **Category Tree**: Cached globally (30 minutes)

## Permissions

- **Customers**: Can view approved products, create reviews
- **Staff/Managers**: Can manage products, view all products
- **Admins**: Full access to all operations
- **Product Owners**: Can manage their own products

## Usage Examples

### Generate Sample Data
```bash
cd borrowbit
python manage.py generate_sample_products --count=75 --categories=18
```

### Test API Endpoints
```bash
# List products
curl -X GET "http://localhost:8000/api/products/"

# Get product details
curl -X GET "http://localhost:8000/api/products/{product_id}/"

# Search products
curl -X GET "http://localhost:8000/api/products/search/?q=laptop"

# Get cart information
curl -X GET "http://localhost:8000/api/products/{product_id}/cart_info/"
```

## Dependencies

- Django 5.2+
- Django REST Framework
- Django Filter
- Django Redis
- Faker (for sample data generation)

## Notes

- All products require admin approval before being visible to customers
- Pricing rules support multiple customer types and duration types
- Reviews are moderated and require approval
- Maintenance records track product lifecycle
- Caching improves performance for frequently accessed data
- Role-based permissions ensure data security
