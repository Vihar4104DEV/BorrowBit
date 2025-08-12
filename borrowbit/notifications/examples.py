"""
Example scripts for using the BorrowBit Email Notification System

This file contains examples of how to use the email notification system
for different scenarios like user registration, rental confirmations, etc.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borrowbit.settings')
django.setup()

from user.models import User
from notifications.unified_email_service import unified_email_service
from notifications.notification_service import NotificationService
from notifications.models import EmailTemplate

def example_send_simple_email():
    """Example: Send a simple email"""
    print("📧 Sending simple email...")
    
    result = unified_email_service.send_email(
        to_email="test@example.com",
        subject="Hello from BorrowBit!",
        html_content="""
        <html>
        <body>
            <h1>Welcome to BorrowBit!</h1>
            <p>This is a test email from your notification system.</p>
            <p>If you received this, your email service is working correctly!</p>
        </body>
        </html>
        """,
        text_content="Welcome to BorrowBit! This is a test email."
    )
    
    if result['success']:
        print("✅ Email sent successfully!")
        print(f"Provider: {result.get('provider', 'Unknown')}")
    else:
        print("❌ Failed to send email:")
        print(f"Error: {result['error']}")

def example_send_template_email():
    """Example: Send email using a template"""
    print("📧 Sending template email...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890"
        }
    )
    
    # Send welcome email using template
    success = NotificationService.send_user_registration_email(user)
    
    if success:
        print("✅ Welcome email sent successfully!")
    else:
        print("❌ Failed to send welcome email")

def example_send_rental_confirmation():
    """Example: Send rental confirmation email"""
    print("📧 Sending rental confirmation...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+1234567890"
        }
    )
    
    # Rental data
    rental_data = {
        "rental_id": "RENT-2024-001",
        "product_name": "MacBook Pro 16-inch",
        "rental_date": "2024-01-15",
        "return_date": "2024-01-22",
        "total_amount": "299.99",
        "delivery_address": "123 Main St, City, State 12345",
        "tracking_url": "https://tracking.example.com/123456"
    }
    
    success = NotificationService.send_rental_confirmation_email(user, rental_data)
    
    if success:
        print("✅ Rental confirmation sent successfully!")
    else:
        print("❌ Failed to send rental confirmation")

def example_send_otp_email():
    """Example: Send OTP verification email"""
    print("📧 Sending OTP email...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "Alice",
            "last_name": "Johnson",
            "phone_number": "+1234567890"
        }
    )
    
    # Generate OTP
    otp_code = "123456"
    
    success = NotificationService.send_otp_email(user, otp_code)
    
    if success:
        print("✅ OTP email sent successfully!")
    else:
        print("❌ Failed to send OTP email")

def example_send_payment_confirmation():
    """Example: Send payment confirmation email"""
    print("📧 Sending payment confirmation...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            "first_name": "Bob",
            "last_name": "Wilson",
            "phone_number": "+1234567890"
        }
    )
    
    # Payment data
    payment_data = {
        "amount": "299.99",
        "payment_method": "Credit Card",
        "transaction_id": "TXN-2024-001",
        "payment_date": "2024-01-15 10:30:00",
        "rental_id": "RENT-2024-001",
        "payment_id": "PAY-2024-001"
    }
    
    success = NotificationService.send_payment_success_email(user, payment_data)
    
    if success:
        print("✅ Payment confirmation sent successfully!")
    else:
        print("❌ Failed to send payment confirmation")

def example_test_connection():
    """Example: Test email service connection"""
    print("🔧 Testing email service connection...")
    
    # Get provider info
    provider_info = unified_email_service.get_provider_info()
    print(f"Current provider: {provider_info['provider']}")
    print(f"Active service: {provider_info['active_service']}")
    
    # Test connection
    test_result = unified_email_service.test_connection()
    
    if test_result['success']:
        print("✅ Connection test successful!")
        print(f"Message: {test_result['message']}")
    else:
        print("❌ Connection test failed:")
        print(f"Error: {test_result['error']}")

def example_switch_provider():
    """Example: Switch between email providers"""
    print("🔄 Switching email providers...")
    
    # Get current provider
    current_provider = unified_email_service.get_provider_info()['provider']
    print(f"Current provider: {current_provider}")
    
    # Switch to the other provider
    new_provider = "RESEND" if current_provider == "SMTP" else "SMTP"
    success = unified_email_service.switch_provider(new_provider)
    
    if success:
        print(f"✅ Switched to {new_provider} provider")
        
        # Test the new provider
        test_result = unified_email_service.test_connection()
        if test_result['success']:
            print("✅ New provider connection test successful!")
        else:
            print(f"❌ New provider connection test failed: {test_result['error']}")
    else:
        print(f"❌ Failed to switch to {new_provider} provider")

def example_create_email_template():
    """Example: Create a custom email template"""
    print("📝 Creating custom email template...")
    
    template, created = EmailTemplate.objects.get_or_create(
        template_type="CUSTOM_WELCOME",
        defaults={
            "name": "Custom Welcome Email",
            "subject": "Welcome to {{ company_name }}, {{ user_name }}!",
            "html_content": """
            <html>
            <body>
                <h1>Welcome to {{ company_name }}!</h1>
                <p>Hi {{ user_name }},</p>
                <p>Thank you for joining {{ company_name }}. We're excited to have you on board!</p>
                <p>Your account was created on {{ registration_date }}.</p>
                <p>Best regards,<br>The {{ company_name }} Team</p>
            </body>
            </html>
            """,
            "text_content": """
            Welcome to {{ company_name }}!
            
            Hi {{ user_name }},
            
            Thank you for joining {{ company_name }}. We're excited to have you on board!
            
            Your account was created on {{ registration_date }}.
            
            Best regards,
            The {{ company_name }} Team
            """,
            "is_active": True
        }
    )
    
    if created:
        print("✅ Custom email template created!")
    else:
        print("ℹ️  Custom email template already exists")
    
    # Send email using the custom template
    context = {
        "user_name": "John Doe",
        "company_name": "BorrowBit",
        "registration_date": "January 15, 2024"
    }
    
    result = unified_email_service.send_template_email(
        template_type="CUSTOM_WELCOME",
        to_email="test@example.com",
        context=context
    )
    
    if result['success']:
        print("✅ Custom template email sent successfully!")
    else:
        print(f"❌ Failed to send custom template email: {result['error']}")

def main():
    """Run all examples"""
    print("🚀 BorrowBit Email Notification System Examples")
    print("=" * 50)
    
    # Test connection first
    example_test_connection()
    print()
    
    # Run examples
    examples = [
        example_send_simple_email,
        example_send_template_email,
        example_send_rental_confirmation,
        example_send_otp_email,
        example_send_payment_confirmation,
        example_create_email_template,
    ]
    
    for example in examples:
        try:
            example()
            print()
        except Exception as e:
            print(f"❌ Error running example: {e}")
            print()
    
    print("✅ All examples completed!")

if __name__ == "__main__":
    main()
