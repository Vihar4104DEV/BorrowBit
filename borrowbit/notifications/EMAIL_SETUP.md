# Email Notification System Setup Guide

This guide will help you set up the email notification system for BorrowBit using either SMTP (Gmail, Outlook, custom SMTP) or Resend API.

## Overview

The notification system supports two email providers:
- **SMTP**: For Gmail, Outlook, Yahoo, or any custom SMTP server
- **Resend**: A modern email API service (free tier: 100 emails/day)

### Email Template System

All emails now use a **consistent base template** with:
- **Professional Header**: BorrowBit logo, branding, and gradient design
- **Dynamic Body**: Content changes based on email type (welcome, rental confirmation, OTP, etc.)
- **Consistent Footer**: Contact information, social media links, and copyright
- **Modern Design**: Responsive layout with Montserrat font and professional styling

This ensures brand consistency across all email communications while maintaining flexibility for different content types.

## Quick Setup

### 1. Choose Your Email Provider

Set the `EMAIL_PROVIDER` environment variable:
```bash
# For SMTP (Gmail, Outlook, etc.)
EMAIL_PROVIDER=SMTP

# For Resend API
EMAIL_PROVIDER=RESEND
```

### 2. Configure Your Chosen Provider

#### Option A: SMTP Configuration (Recommended)

For **Gmail**:
```bash
EMAIL_PROVIDER=SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=True
SMTP_USE_SSL=False
DEFAULT_FROM_EMAIL=your_email@gmail.com
FROM_NAME=BorrowBit
```

For **Outlook/Hotmail**:
```bash
EMAIL_PROVIDER=SMTP
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
SMTP_USE_TLS=True
SMTP_USE_SSL=False
DEFAULT_FROM_EMAIL=your_email@outlook.com
FROM_NAME=BorrowBit
```

For **Yahoo**:
```bash
EMAIL_PROVIDER=SMTP
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=True
SMTP_USE_SSL=False
DEFAULT_FROM_EMAIL=your_email@yahoo.com
FROM_NAME=BorrowBit
```

For **Custom SMTP Server**:
```bash
EMAIL_PROVIDER=SMTP
SMTP_HOST=your_smtp_server.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_USE_TLS=True
SMTP_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=BorrowBit
```

#### Option B: Resend Configuration

```bash
EMAIL_PROVIDER=RESEND
RESEND_API_KEY=your_resend_api_key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=BorrowBit
```

## Gmail App Password Setup

If using Gmail, you need to create an App Password:

1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled
4. Go to App passwords
5. Generate a new app password for "Mail"
6. Use this password in `SMTP_PASSWORD`

## Testing Your Configuration

### Test Email Templates

To preview all email templates with the new design:

```bash
cd borrowbit/notifications
python test_new_templates.py
```

This will generate HTML preview files for all email types:
- `welcome_email_preview.html`
- `rental_confirmation_preview.html`
- `otp_email_preview.html`
- `payment_success_preview.html`
- `delivery_email_preview.html`
- `return_reminder_preview.html`

Open any of these files in your browser to see the new consistent design.

### Test Email Sending

### 1. Test Connection

```bash
python manage.py test_smtp
```

This will test the connection and show configuration details.

### 2. Send Test Email

```bash
python manage.py test_smtp --to your_email@example.com
```

This will send a test email to verify everything is working.

### 3. Switch Providers

```bash
# Switch to SMTP
python manage.py test_smtp --provider SMTP --switch

# Switch to Resend
python manage.py test_smtp --provider RESEND --switch
```

## API Endpoints

### Test Email Service
```http
POST /api/notifications/email-service/test_connection/
```

### Send Custom Email
```http
POST /api/notifications/email-service/send_email/
{
    "to_email": "recipient@example.com",
    "subject": "Test Email",
    "html_content": "<p>Hello World!</p>",
    "text_content": "Hello World!"
}
```

### Send Template Email
```http
POST /api/notifications/email-service/send_template_email/
{
    "template_type": "WELCOME_EMAIL",
    "to_email": "recipient@example.com",
    "context": {
        "user_name": "John Doe",
        "registration_date": "January 1, 2024"
    }
}
```

## Available Email Templates

The system includes these pre-built templates:

- `USER_REGISTRATION` - Welcome email for new users
- `RENTAL_CONFIRMATION` - Rental confirmation email
- `PRODUCT_DELIVERY` - Product delivery notification
- `PRODUCT_RETURN` - Return reminder email
- `PAYMENT_SUCCESS` - Payment confirmation
- `PAYMENT_FAILED` - Payment failure notification
- `DELIVERY_UPDATE` - Delivery status update
- `WELCOME_EMAIL` - Welcome message
- `PASSWORD_RESET` - Password reset email
- `OTP_VERIFICATION` - OTP verification email

## Environment Variables Reference

### SMTP Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_PROVIDER` | Email provider (SMTP/RESEND) | SMTP |
| `SMTP_HOST` | SMTP server hostname | smtp.gmail.com |
| `SMTP_PORT` | SMTP server port | 587 |
| `SMTP_USERNAME` | SMTP username/email | - |
| `SMTP_PASSWORD` | SMTP password/app password | - |
| `SMTP_USE_TLS` | Use TLS encryption | True |
| `SMTP_USE_SSL` | Use SSL encryption | False |

### Resend Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_PROVIDER` | Email provider (SMTP/RESEND) | SMTP |
| `RESEND_API_KEY` | Resend API key | - |

### General Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_FROM_EMAIL` | Default sender email | noreply@borrowbit.com |
| `FROM_NAME` | Default sender name | BorrowBit |

## Troubleshooting

### Common SMTP Issues

1. **Authentication Failed**
   - Check username and password
   - For Gmail, use App Password instead of regular password
   - Enable "Less secure app access" (not recommended)

2. **Connection Refused**
   - Check SMTP host and port
   - Verify firewall settings
   - Try different ports (587, 465, 25)

3. **TLS/SSL Issues**
   - Try `SMTP_USE_TLS=True` and `SMTP_USE_SSL=False`
   - For port 465, use `SMTP_USE_SSL=True`
   - For port 587, use `SMTP_USE_TLS=True`

### Common Resend Issues

1. **API Key Invalid**
   - Verify your Resend API key
   - Check if the key has proper permissions

2. **Domain Not Verified**
   - Verify your domain in Resend dashboard
   - Use a verified domain for `DEFAULT_FROM_EMAIL`

## Security Best Practices

1. **Never commit credentials to version control**
   - Use environment variables
   - Use `.env` files (not committed to git)

2. **Use App Passwords for Gmail**
   - Don't use your regular Gmail password
   - Generate app-specific passwords

3. **Verify your domain**
   - Use a verified domain for sending emails
   - This improves deliverability

4. **Monitor email logs**
   - Check the notification logs for failed emails
   - Set up monitoring for email delivery rates

## Production Deployment

### Environment Variables
Create a `.env` file in your project root:
```bash
# Email Configuration
EMAIL_PROVIDER=SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_production_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=True
SMTP_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Your Company Name

# Other Django settings
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Monitoring
Set up monitoring for:
- Email delivery success rates
- Failed notification attempts
- SMTP connection issues
- API rate limits (for Resend)

## Support

If you encounter issues:

1. Check the logs in `borrowbit/logs/django.log`
2. Run the test command: `python manage.py test_smtp`
3. Verify your environment variables
4. Test with a simple email client first

For additional help, check the Django documentation on email configuration or the Resend documentation for API-specific issues.
