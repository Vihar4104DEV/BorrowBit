# Stripe Setup Guide for BorrowBit Rental Application

## Overview
This guide explains how to set up Stripe payment gateway for the BorrowBit rental application.

## Prerequisites
1. A Stripe account (sign up at https://stripe.com)
2. Access to your Stripe dashboard
3. Python environment with the required packages installed

## Step 1: Get Your Stripe API Keys

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com/)
2. Go to **Developers** → **API keys**
3. Copy your **Publishable key** and **Secret key**
4. For webhooks, also copy your **Webhook endpoint secret**

## Step 2: Set Environment Variables

Create a `.env` file in your project root (`BorrowBit/borrowbit/`) with the following content:

```bash
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Other Django settings
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important Notes:**
- Use `pk_test_` and `sk_test_` keys for development/testing
- Use `pk_live_` and `sk_live_` keys for production
- Never commit your `.env` file to version control

## Step 3: Test Your Configuration

Run the test script to verify your Stripe setup:

```bash
cd BorrowBit/borrowbit/
python test_stripe.py
```

This script will:
- Verify your API keys are configured
- Test Stripe connection
- Create test products and prices
- Create a test checkout session
- Clean up test resources

## Step 4: Configure Webhooks (Optional for Development)

For production, you'll want to set up webhooks to handle payment status updates:

1. In your Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set the endpoint URL to: `https://yourdomain.com/api/v1/payments/webhook/`
4. Select these events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
5. Copy the webhook signing secret to your `.env` file

## Step 5: Test the Rental Order Creation

Once configured, test the rental order creation endpoint:

```bash
POST /api/v1/payments/rental-orders/create_from_cart/
```

The system will now:
1. Create a Stripe product (if it doesn't exist)
2. Create a Stripe price for the specific order
3. Create a checkout session
4. Return the checkout URL

## Troubleshooting

### Common Issues

1. **"Stripe secret key is not configured"**
   - Check that your `.env` file exists and contains `STRIPE_SECRET_KEY`
   - Verify the environment variable is being loaded

2. **"Stripe authentication failed"**
   - Verify your API key is correct
   - Check if you're using test keys in production or vice versa

3. **"Product not found"**
   - The system will automatically create products if they don't exist
   - Check your Stripe dashboard for created products

4. **"Price creation failed"**
   - Verify your Stripe account has permission to create prices
   - Check if you've reached any Stripe limits

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your `.env` file. Check the logs at `BorrowBit/borrowbit/logs/django.log` for detailed error information.

## Security Best Practices

1. **Never expose your secret key** in client-side code
2. **Use environment variables** for sensitive configuration
3. **Verify webhook signatures** in production
4. **Use HTTPS** for all production endpoints
5. **Regularly rotate your API keys**

## Production Considerations

1. **Switch to live keys** when going to production
2. **Set up proper webhook endpoints** with HTTPS
3. **Configure proper error handling** and monitoring
4. **Set up Stripe Radar** for fraud detection
5. **Monitor your Stripe dashboard** for any issues

## Support

If you encounter issues:
1. Check the Django logs for detailed error messages
2. Verify your Stripe dashboard for any account issues
3. Test with the provided test script
4. Check Stripe's [API documentation](https://stripe.com/docs/api)

## API Endpoints

The following endpoints are available for payment processing:

- `POST /api/v1/payments/rental-orders/create_from_cart/` - Create rental order and checkout session
- `GET /api/v1/payments/success/` - Handle successful payments
- `GET /api/v1/payments/cancel/` - Handle cancelled payments
- `POST /api/v1/payments/webhook/` - Handle Stripe webhooks
