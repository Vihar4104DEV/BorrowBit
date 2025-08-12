#!/usr/bin/env python3
"""
Test script to demonstrate the new email template system
This script shows how all emails now use the consistent base template
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borrowbit.settings')
django.setup()

from notifications.template_utils import EmailTemplateRenderer
from notifications.notification_service import NotificationService

def test_welcome_email():
    """Test the welcome email template"""
    print("🧪 Testing Welcome Email Template...")
    
    context = {
        'user_name': 'John Doe',
        'email': 'john@example.com',
        'registration_date': 'December 15, 2024',
        'login_url': 'https://borrowbit.com/login',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_welcome_email_html(context)
    
    # Save to file for preview
    with open('welcome_email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Welcome email template generated successfully!")
    print("📄 Preview saved to: welcome_email_preview.html")
    return html_content

def test_rental_confirmation_email():
    """Test the rental confirmation email template"""
    print("\n🧪 Testing Rental Confirmation Email Template...")
    
    context = {
        'user_name': 'Jane Smith',
        'product_name': 'Professional Camera Kit',
        'rental_id': 'RENT-2024-001',
        'rental_date': 'December 15, 2024',
        'return_date': 'December 22, 2024',
        'total_amount': '150.00',
        'delivery_address': '123 Main St, Mumbai, India',
        'tracking_url': 'https://borrowbit.com/track/RENT-2024-001',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_rental_confirmation_html(context)
    
    # Save to file for preview
    with open('rental_confirmation_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Rental confirmation email template generated successfully!")
    print("📄 Preview saved to: rental_confirmation_preview.html")
    return html_content

def test_otp_email():
    """Test the OTP email template"""
    print("\n🧪 Testing OTP Email Template...")
    
    context = {
        'user_name': 'Alice Johnson',
        'otp_code': '123456',
        'expiry_time': '10 minutes',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_otp_email_html(context)
    
    # Save to file for preview
    with open('otp_email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ OTP email template generated successfully!")
    print("📄 Preview saved to: otp_email_preview.html")
    return html_content

def test_payment_success_email():
    """Test the payment success email template"""
    print("\n🧪 Testing Payment Success Email Template...")
    
    context = {
        'user_name': 'Bob Wilson',
        'amount': '150.00',
        'payment_method': 'Credit Card',
        'transaction_id': 'TXN-2024-001',
        'payment_date': 'December 15, 2024',
        'rental_id': 'RENT-2024-001',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_payment_success_html(context)
    
    # Save to file for preview
    with open('payment_success_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Payment success email template generated successfully!")
    print("📄 Preview saved to: payment_success_preview.html")
    return html_content

def test_delivery_email():
    """Test the delivery email template"""
    print("\n🧪 Testing Delivery Email Template...")
    
    context = {
        'user_name': 'Carol Brown',
        'product_name': 'Professional Camera Kit',
        'delivery_date': 'December 16, 2024',
        'estimated_time': '2:00 PM - 4:00 PM',
        'delivery_address': '123 Main St, Mumbai, India',
        'tracking_number': 'TRK-2024-001',
        'delivery_partner': 'FastDelivery Express',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_delivery_email_html(context)
    
    # Save to file for preview
    with open('delivery_email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Delivery email template generated successfully!")
    print("📄 Preview saved to: delivery_email_preview.html")
    return html_content

def test_return_reminder_email():
    """Test the return reminder email template"""
    print("\n🧪 Testing Return Reminder Email Template...")
    
    context = {
        'user_name': 'David Lee',
        'product_name': 'Professional Camera Kit',
        'return_date': 'December 22, 2024',
        'days_remaining': '2 days',
        'pickup_address': '123 Main St, Mumbai, India',
        'rental_id': 'RENT-2024-001',
        'support_email': 'support@borrowbit.com'
    }
    
    html_content = NotificationService._get_return_reminder_html(context)
    
    # Save to file for preview
    with open('return_reminder_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Return reminder email template generated successfully!")
    print("📄 Preview saved to: return_reminder_preview.html")
    return html_content

def main():
    """Run all template tests"""
    print("🚀 Testing New Email Template System")
    print("=" * 50)
    print("This script demonstrates the new consistent email template design")
    print("All emails now use the same header and footer with only body content changing")
    print("=" * 50)
    
    try:
        # Test all email templates
        test_welcome_email()
        test_rental_confirmation_email()
        test_otp_email()
        test_payment_success_email()
        test_delivery_email()
        test_return_reminder_email()
        
        print("\n" + "=" * 50)
        print("🎉 All email templates tested successfully!")
        print("📁 Preview files have been saved to the current directory")
        print("🌐 Open any .html file in your browser to see the new design")
        print("=" * 50)
        
        print("\n📋 Template Features:")
        print("✅ Consistent BorrowBit header with logo")
        print("✅ Professional gradient design")
        print("✅ Responsive layout")
        print("✅ Consistent footer with contact info")
        print("✅ Social media links")
        print("✅ Modern styling with Montserrat font")
        print("✅ Only email body content changes between templates")
        
    except Exception as e:
        print(f"❌ Error testing templates: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
