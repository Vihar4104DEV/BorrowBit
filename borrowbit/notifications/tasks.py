# from celery import shared_task
from django.core.mail import send_mail  # Email sending disabled (bypassed)
from django.conf import settings
from user.models import User, OTPVerification
from .models import Notification
# from .notification_service import NotificationService
# from .unified_email_service import unified_email_service
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
        
        # Email notification using new service
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
                
                # Send email (disabled)
                send_mail(
                    "OTP Verification",
                    f"Your OTP is {otp_code}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                # Bypass actual email sending (disabled)
                notification.status = "SENT"
                notification.save(update_fields=['status'])
                logger.info(f"Bypassed email sending to {email}; OTP: {otp_code}")
                print(f"📧 Email sending bypassed for {email}: {otp_code}")
                    
            except Exception as e:
                logger.error(f"Error sending email to {email}: {str(e)}")
                print(f"❌ Error sending email to {email}: {str(e)}")
        
        # SMS notification (stub, integrate with SMS gateway)
        if phone_number:
            try:
                # Create notification record for SMS
                Notification.objects.create(
                    user=user,
                    notification_type="SMS",
                    category="OTP_VERIFICATION",
                    recipient=phone_number,
                    subject="OTP Verification",
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
        return False

# @shared_task
def send_user_registration_email(user_id):
    """Send welcome email to newly registered user"""
    try:
        user = User.objects.get(id=user_id)
        success = NotificationService.send_user_registration_email(user)
        
        if success:
            logger.info(f"Welcome email sent successfully to {user.email}")
            print(f"📧 Welcome email sent to {user.email}")
        else:
            logger.error(f"Failed to send welcome email to {user.email}")
            print(f"❌ Failed to send welcome email to {user.email}")
            
        return success
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send registration email: {e}")
        return False

# @shared_task
def send_rental_confirmation_email(user_id, rental_data):
    """Send rental confirmation email"""
    try:
        user = User.objects.get(id=user_id)
        success = NotificationService.send_rental_confirmation_email(user, rental_data)
        
        if success:
            logger.info(f"Rental confirmation email sent to {user.email}")
            print(f"📧 Rental confirmation email sent to {user.email}")
        else:
            logger.error(f"Failed to send rental confirmation email to {user.email}")
            print(f"❌ Failed to send rental confirmation email to {user.email}")
            
        return success
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send rental confirmation email: {e}")
        return False

# @shared_task
def send_product_delivery_email(user_id, delivery_data):
    """Send product delivery notification email"""
    try:
        user = User.objects.get(id=user_id)
        success = NotificationService.send_product_delivery_email(user, delivery_data)
        
        if success:
            logger.info(f"Delivery notification email sent to {user.email}")
            print(f"📧 Delivery notification email sent to {user.email}")
        else:
            logger.error(f"Failed to send delivery notification email to {user.email}")
            print(f"❌ Failed to send delivery notification email to {user.email}")
            
        return success
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send delivery notification email: {e}")
        return False

# @shared_task
def send_return_reminder_email(user_id, return_data):
    """Send product return reminder email"""
    try:
        user = User.objects.get(id=user_id)
        success = NotificationService.send_product_return_reminder_email(user, return_data)
        
        if success:
            logger.info(f"Return reminder email sent to {user.email}")
            print(f"📧 Return reminder email sent to {user.email}")
        else:
            logger.error(f"Failed to send return reminder email to {user.email}")
            print(f"❌ Failed to send return reminder email to {user.email}")
            
        return success
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send return reminder email: {e}")
        return False

# @shared_task
def send_payment_success_email(user_id, payment_data):
    """Send payment success email"""
    try:
        user = User.objects.get(id=user_id)
        success = NotificationService.send_payment_success_email(user, payment_data)
        
        if success:
            logger.info(f"Payment success email sent to {user.email}")
            print(f"📧 Payment success email sent to {user.email}")
        else:
            logger.error(f"Failed to send payment success email to {user.email}")
            print(f"❌ Failed to send payment success email to {user.email}")
            
        return success
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send payment success email: {e}")
        return False

# @shared_task
def retry_failed_notifications():
    """Retry sending failed notifications"""
    try:
        stats = unified_email_service.retry_failed_notifications()
        logger.info(f"Retry completed: {stats}")
        print(f"🔄 Retry completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to retry notifications: {e}")
        return {"retried": 0, "success": 0, "failed": 0}
