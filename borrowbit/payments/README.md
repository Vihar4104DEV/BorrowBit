# Payment Management System

This module provides comprehensive payment management for the rental system, including Stripe integration, rental order management, and webhook handling.

## Features

- **Rental Order Management**: Create and manage rental orders from cart items
- **Stripe Integration**: Secure payment processing with Stripe Checkout
- **Webhook Handling**: Automated payment status updates and inventory management
- **Role-based Access Control**: Secure access based on user roles
- **Database Optimization**: Efficient queries with proper indexing and caching
- **Comprehensive Testing**: Full test coverage for all functionality

## API Endpoints

### 1. Create Rental Order from Cart

**Endpoint**: `POST /payments/rental-orders/create_from_cart/`

**Description**: Creates a rental order from cart items and generates a Stripe checkout session.

**Request Body**:
```json
{
  "cart_items": [
    {
      "product_id": "uuid",
      "quantity": 2
    }
  ],
  "rental_start_date": "2024-01-15T10:00:00Z",
  "rental_end_date": "2024-01-17T10:00:00Z",
  "notes": "Optional notes"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Rental order created successfully",
  "data": {
    "order_id": "uuid",
    "order_number": "RO202401150001",
    "total_amount": "154.25",
    "checkout_url": "https://checkout.stripe.com/test",
    "session_id": "cs_test_123"
  }
}
```

**Features**:
- Validates product availability and rental dates
- Calculates pricing including tax and deposits
- Reserves product quantities
- Creates Stripe checkout session
- Generates unique order numbers

### 2. List User Orders

**Endpoint**: `GET /payments/rental-orders/my_orders/`

**Description**: Retrieves all rental orders for the authenticated user with caching.

**Response**:
```json
{
  "success": true,
  "message": "Orders retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "order_number": "RO202401150001",
      "customer_name": "John Doe",
      "status": "CONFIRMED",
      "status_display": "Confirmed",
      "rental_start_date": "2024-01-15T10:00:00Z",
      "rental_end_date": "2024-01-17T10:00:00Z",
      "total_amount": "154.25",
      "items_count": 2,
      "created_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

**Features**:
- Role-based access control
- Caching for performance optimization
- Pagination support
- Filtering and sorting

### 3. Cancel Rental Order

**Endpoint**: `POST /payments/rental-orders/{id}/cancel_order/`

**Description**: Cancels a rental order and releases reserved quantities.

**Response**:
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

**Features**:
- Validates order status
- Releases reserved quantities
- Updates payment statuses
- Clears cached data

### 4. Stripe Webhook

**Endpoint**: `POST /payments/stripe/webhook/`

**Description**: Handles Stripe webhook events for payment status updates.

**Supported Events**:
- `checkout.session.completed`: Payment successful
- `payment_intent.succeeded`: Payment confirmed
- `payment_intent.payment_failed`: Payment failed
- `charge.refunded`: Payment refunded

**Features**:
- Secure webhook signature verification
- Automated inventory management
- Payment status updates
- Order status management
- Notification creation

### 5. Payment Success/Cancel Pages

**Endpoints**:
- `GET /payments/success/?session_id={session_id}`
- `GET /payments/cancel/?order_id={order_id}`

**Description**: Handle frontend redirects after payment completion or cancellation.

## Database Models

### RentalOrder
- Manages rental order information
- Tracks order status and financial details
- Generates unique order numbers
- Handles rental date management

### RentalOrderItem
- Stores individual items in rental orders
- Calculates pricing and totals
- Links products to orders

### Payment
- Tracks payment transactions
- Integrates with payment gateways
- Manages payment statuses and metadata

### PaymentGateway
- Configures payment gateway settings
- Stores API credentials securely
- Supports multiple gateway types

### PaymentSchedule
- Manages installment payment plans
- Tracks payment due dates
- Links to actual payments

### PaymentNotification
- Handles payment-related notifications
- Supports multiple notification types
- Tracks delivery status

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```bash
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### 2. Stripe Webhook Configuration

1. Go to your Stripe Dashboard
2. Navigate to Developers > Webhooks
3. Add endpoint: `https://yourdomain.com/payments/stripe/webhook/`
4. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
5. Copy the webhook signing secret

### 3. Database Migrations

```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 4. Create Payment Gateway

```python
from payments.models import PaymentGateway

PaymentGateway.objects.create(
    name='Stripe Payment Gateway',
    gateway_type='STRIPE',
    is_active=True,
    is_test_mode=True
)
```

## Usage Examples

### Frontend Integration

```javascript
// Create rental order
const createOrder = async (cartItems, rentalDates) => {
  const response = await fetch('/payments/rental-orders/create_from_cart/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      cart_items: cartItems,
      rental_start_date: rentalDates.start,
      rental_end_date: rentalDates.end
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Redirect to Stripe checkout
    window.location.href = data.data.checkout_url;
  }
};

// Handle payment success
const handlePaymentSuccess = async (sessionId) => {
  const response = await fetch(`/payments/success/?session_id=${sessionId}`);
  const data = await response.json();
  
  if (data.success) {
    // Show success message
    showSuccessMessage('Payment completed successfully!');
  }
};
```

### Backend Integration

```python
from payments.models import RentalOrder, Payment
from payments.serializers import RentalOrderDetailSerializer

# Get user orders
user_orders = RentalOrder.objects.filter(customer=request.user)

# Serialize orders
serializer = RentalOrderDetailSerializer(user_orders, many=True)
orders_data = serializer.data

# Get order details
order = RentalOrder.objects.get(id=order_id)
payments = order.payments.all()
```

## Security Features

- **CSRF Protection**: All endpoints except webhooks are CSRF protected
- **Authentication Required**: All endpoints require user authentication
- **Role-based Access**: Users can only access their own data
- **Webhook Verification**: Stripe webhook signatures are verified
- **Input Validation**: Comprehensive validation of all input data
- **SQL Injection Protection**: Uses Django ORM with parameterized queries

## Performance Optimization

- **Database Indexing**: Proper indexes on frequently queried fields
- **Select Related**: Optimized queries with related field fetching
- **Caching**: Redis-based caching for frequently accessed data
- **Pagination**: Efficient handling of large datasets
- **Query Optimization**: Minimized database queries

## Testing

Run the test suite:

```bash
python manage.py test payments
```

Test coverage includes:
- Model creation and validation
- API endpoint functionality
- Stripe webhook handling
- Permission system
- Error handling
- Edge cases

## Error Handling

The system provides comprehensive error handling:

- **Validation Errors**: Detailed validation error messages
- **Business Logic Errors**: Clear error messages for business rule violations
- **System Errors**: Graceful handling of unexpected errors
- **Logging**: Comprehensive logging for debugging and monitoring

## Monitoring and Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Error Tracking**: Detailed error information for debugging
- **Performance Monitoring**: Query execution time tracking
- **Webhook Monitoring**: Stripe webhook delivery tracking

## Future Enhancements

- **Installment Payments**: Support for payment plans
- **Multiple Payment Methods**: Additional payment gateways
- **Advanced Notifications**: Email and SMS notifications
- **Analytics**: Payment and order analytics
- **Refund Management**: Automated refund processing
- **Subscription Support**: Recurring rental payments

## Support

For questions or issues:

1. Check the test files for usage examples
2. Review the admin interface for data management
3. Check logs for detailed error information
4. Verify Stripe webhook configuration
5. Ensure proper environment variable setup

## Contributing

When contributing to the payment system:

1. Follow the existing code style
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure proper error handling
5. Test with Stripe test mode first
