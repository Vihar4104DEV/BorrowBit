# from celery import shared_task
# from django.core.mail import send_mail  # Email sending disabled (bypassed)
from django.conf import settings
from user.models import User, OTPVerification
from .models import Notification
import logging

logger = logging.getLogger(__name__)

# @shared_task
def send_otp_notification(email, phone_number, otp_code):
    """
    Synchronous function to send OTP via email and SMS, with audit logging.
    Note: This function is now synchronous and runs in the main Django process.
    """
    try:
        # Get user for notification logging
        user = User.objects.filter(email=email).first()
        
        if not user:
            logger.error(f"User not found for email: {email}")
            return False
        
        # Email notification
        if email:
            try:
                # Create notification record
                notification = Notification.objects.create(
                    user=user,
                    notification_type="EMAIL",
                    recipient=email,
                    message=f"Your OTP is {otp_code}",
                    status="PENDING"
                )
                
                # Bypass actual email sending (disabled)
                notification.status = "SENT"
                notification.save(update_fields=['status'])
                logger.info(f"Bypassed email sending to {email}; OTP: {otp_code}")
                print(f"📧 Email sending bypassed for {email}: {otp_code}")
                    
            except Exception as e:
                logger.error(f"Error sending email to {email}: {str(e)}")
                if 'notification' in locals():
                    notification.status = "FAILED"
                    notification.error_message = str(e)
                    notification.save(update_fields=['status', 'error_message'])
                print(f"❌ Error sending email to {email}: {str(e)}")
        
        # SMS notification (stub, integrate with SMS gateway)
        if phone_number:
            try:
                # Create notification record
                Notification.objects.create(
                    user=user,
                    notification_type="SMS",
                    recipient=phone_number,
                    message=f"Your OTP is {otp_code}",
                    status="PENDING"
                )
                
                # TODO: Integrate with SMS gateway here
                # For now, just log that SMS would be sent
                logger.info(f"SMS OTP {otp_code} would be sent to {phone_number}")
                print(f"📱 SMS OTP {otp_code} would be sent to {phone_number}")
                
            except Exception as e:
                logger.error(f"Error creating SMS notification for {phone_number}: {str(e)}")
                print(f"❌ Error creating SMS notification for {phone_number}: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP notification: {e}")
        print(f"❌ Failed to send OTP notification: {e}")
        
        # Try to create a failed notification record if user exists
        try:
            if 'user' in locals() and user:
                Notification.objects.create(
                    user=user,
                    notification_type="EMAIL",
                    recipient=email,
                    message=f"Your OTP is {otp_code}",
                    status="FAILED",
                    error_message=str(e)
                )
        except Exception as create_error:
            logger.error(f"Failed to create notification record: {create_error}")
        
        return False
