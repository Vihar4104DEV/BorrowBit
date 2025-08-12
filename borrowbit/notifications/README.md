# BorrowBit Email System

A comprehensive email sending system for the BorrowBit rental platform.

## Features

- ✅ **Resend API Integration** - Fast, reliable email delivery
- ✅ **Email Templates** - Pre-built templates for common notifications
- ✅ **Template Variables** - Dynamic content with Django template syntax
- ✅ **Retry Mechanism** - Automatic retry for failed emails
- ✅ **Email Tracking** - Track sent, failed, and pending emails
- ✅ **Admin Interface** - Manage templates and view email history
- ✅ **API Endpoints** - RESTful API for sending emails
- ✅ **Beautiful HTML Templates** - Professional email designs

## Quick Start

### 1. Setup Email Configuration

1. **Sign up for Resend** (Free tier: 100 emails/day)
   - Go to [https://resend.com](https://resend.com)
   - Create an account and get your API key

2. **Configure Environment Variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your credentials
   RESEND_API_KEY=re_your_api_key_here
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   FROM_NAME=BorrowBit
   ```

3. **Set up Email Templates**
   ```bash
   python manage.py setup_email_templates
   ```

### 2. Test Your Email System

```bash
# Run the test script
python test_email.py
```

### 3. Send Your First Email

```python
from notifications.email_service import email_service

# Send a simple email
result = email_service.send_email(
    to_email="customer@example.com",
    subject="Welcome to BorrowBit!",
    html_content="<h1>Welcome!</h1><p>Thank you for joining BorrowBit.</p>"
)

if result['success']:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {result['error']}")
```

## API Endpoints

### Send Custom Email
```http
POST /api/notifications/email-service/send_email/
Content-Type: application/json

{
    "to_email": "customer@example.com",
    "subject": "Welcome to BorrowBit!",
    "html_content": "<h1>Welcome!</h1><p>Thank you for joining.</p>",
    "text_content": "Welcome! Thank you for joining.",
    "from_email": "noreply@borrowbit.com",
    "from_name": "BorrowBit"
}
```

### Send Template Email
```http
POST /api/notifications/email-service/send_template_email/
Content-Type: application/json

{
    "to_email": "customer@example.com",
    "template_type": "WELCOME_EMAIL",
    "context": {
        "user_name": "John Doe",
        "registration_date": "January 15, 2024",
        "login_url": "https://borrowbit.com/login",
        "support_email": "support@borrowbit.com"
    }
}
```

### Test Email Connection
```http
POST /api/notifications/email-service/test_connection/
```

## Available Email Templates

| Template Type | Description | Variables |
|---------------|-------------|-----------|
| `WELCOME_EMAIL` | Welcome email for new users | `user_name`, `registration_date`, `login_url`, `support_email` |
| `OTP_VERIFICATION` | OTP verification code | `user_name`, `otp_code`, `expiry_time`, `support_email` |
| `RENTAL_CONFIRMATION` | Rental confirmation | `user_name`, `product_name`, `rental_id`, `rental_date`, `return_date`, `total_amount`, `delivery_address`, `tracking_url`, `support_email` |
| `PRODUCT_DELIVERY` | Product delivery notification | `user_name`, `product_name`, `delivery_date`, `delivery_address`, `tracking_number`, `delivery_partner`, `estimated_time`, `support_email` |
| `PRODUCT_RETURN` | Return reminder | `user_name`, `product_name`, `return_date`, `pickup_address`, `rental_id`, `days_remaining`, `support_email` |
| `PAYMENT_SUCCESS` | Payment confirmation | `user_name`, `amount`, `payment_method`, `transaction_id`, `payment_date`, `rental_id`, `support_email` |
| `PAYMENT_FAILED` | Payment failure notification | `user_name`, `amount`, `payment_method`, `error_message`, `support_email` |

## Using the Notification Service

### Send Welcome Email
```python
from notifications.notification_service import NotificationService
from user.models import User

user = User.objects.get(email="customer@example.com")
success = NotificationService.send_user_registration_email(user)
```

### Send OTP Email
```python
success = NotificationService.send_otp_email(user, "123456")
```

### Send Rental Confirmation
```python
rental_data = {
    "rental_id": "RENT-001",
    "product_name": "iPhone 15 Pro",
    "rental_date": "2024-01-15",
    "return_date": "2024-01-22",
    "total_amount": "150.00",
    "delivery_address": "123 Main St, City, State 12345"
}

success = NotificationService.send_rental_confirmation_email(user, rental_data)
```

## Email Templates Management

### View Templates
```http
GET /api/notifications/email-templates/
```

### Create/Update Template
```http
POST /api/notifications/email-templates/
Content-Type: application/json

{
    "name": "Custom Welcome Email",
    "template_type": "WELCOME_EMAIL",
    "subject": "Welcome {{ user_name }}!",
    "html_content": "<h1>Welcome {{ user_name }}!</h1>",
    "text_content": "Welcome {{ user_name }}!",
    "is_active": true
}
```

### Template Variables
Use Django template syntax in your templates:
- `{{ variable_name }}` - Display variable value
- `{% if condition %}` - Conditional statements
- `{% for item in items %}` - Loops

## Monitoring and Analytics

### View Email Statistics
```http
GET /api/notifications/notifications/stats/
```

### Retry Failed Emails
```http
POST /api/notifications/notifications/retry_failed/
```

### View Email History
```http
GET /api/notifications/notifications/
```

## Configuration Options

### Environment Variables
- `RESEND_API_KEY` - Your Resend API key
- `DEFAULT_FROM_EMAIL` - Default sender email
- `FROM_NAME` - Default sender name

### SMTP Fallback (Optional)
If you prefer SMTP over Resend:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
```

## Best Practices

1. **Always use templates** for consistent branding
2. **Test emails** before sending to customers
3. **Monitor delivery rates** and failed emails
4. **Use meaningful subjects** that encourage opens
5. **Include both HTML and text** versions
6. **Set up proper reply-to addresses**
7. **Respect unsubscribe preferences**

## Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check your `RESEND_API_KEY` environment variable
   - Ensure the key is valid and active

2. **"Template not found"**
   - Run `python manage.py setup_email_templates`
   - Check template type spelling

3. **"Email not delivered"**
   - Check spam folder
   - Verify recipient email address
   - Check Resend dashboard for delivery status

4. **"Rate limit exceeded"**
   - Resend free tier: 100 emails/day
   - Upgrade plan for higher limits

### Debug Mode
Enable debug logging in settings:
```python
LOGGING = {
    'loggers': {
        'notifications': {
            'level': 'DEBUG',
        },
    },
}
```

## Support

For issues or questions:
- Check the logs in `borrowbit/logs/django.log`
- Review Resend dashboard for delivery status
- Contact support with error details
