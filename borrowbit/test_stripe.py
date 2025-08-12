#!/usr/bin/env python
"""
Test script to verify Stripe configuration and basic operations.
Run this script to test if Stripe is properly configured.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borrowbit.settings')
django.setup()

import stripe
from django.conf import settings

def test_stripe_configuration():
    """Test if Stripe is properly configured."""
    print("Testing Stripe configuration...")
    
    # Check if Stripe secret key is set
    if not settings.STRIPE_SECRET_KEY:
        print("❌ ERROR: STRIPE_SECRET_KEY is not configured")
        print("Please set the STRIPE_SECRET_KEY environment variable")
        return False
    
    print(f"✅ STRIPE_SECRET_KEY is configured: {settings.STRIPE_SECRET_KEY[:10]}...")
    
    # Set Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Test basic Stripe connection
    try:
        # Try to list products (this will test the connection)
        products = stripe.Product.list(limit=1)
        print("✅ Stripe connection successful")
        print(f"   Found {len(products.data)} existing products")
        return True
    except stripe.error.AuthenticationError:
        print("❌ ERROR: Stripe authentication failed")
        print("   Please check your STRIPE_SECRET_KEY")
        return False
    except stripe.error.StripeError as e:
        print(f"❌ ERROR: Stripe error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
        return False

def test_stripe_operations():
    """Test basic Stripe operations."""
    print("\nTesting Stripe operations...")
    
    try:
        # Test product creation
        print("Creating test product...")
        test_product = stripe.Product.create(
            name="Test Product",
            description="A test product for verification",
            metadata={'test': 'true'}
        )
        print(f"✅ Created test product: {test_product.id}")
        
        # Test price creation
        print("Creating test price...")
        test_price = stripe.Price.create(
            product=test_product.id,
            unit_amount=1000,  # $10.00
            currency='usd',
            metadata={'test': 'true'}
        )
        print(f"✅ Created test price: {test_price.id}")
        
        # Test checkout session creation
        print("Creating test checkout session...")
        test_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': test_price.id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
            metadata={'test': 'true'}
        )
        print(f"✅ Created test checkout session: {test_session.id}")
        print(f"   Checkout URL: {test_session.url}")
        
        # Clean up test resources
        print("Cleaning up test resources...")
        stripe.Price.modify(test_price.id, active=False)
        print("✅ Test price archived")
        
        return True
        
    except stripe.error.StripeError as e:
        print(f"❌ ERROR: Stripe operation failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("=" * 50)
    print("STRIPE CONFIGURATION TEST")
    print("=" * 50)
    
    # Test configuration
    if not test_stripe_configuration():
        print("\n❌ Stripe configuration test failed")
        print("Please fix the configuration issues before proceeding")
        return
    
    # Test operations
    if test_stripe_operations():
        print("\n✅ All Stripe tests passed!")
        print("Your Stripe integration is working correctly")
    else:
        print("\n❌ Stripe operations test failed")
        print("There may be issues with your Stripe account or API access")

if __name__ == "__main__":
    main()
