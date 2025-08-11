from celery import shared_task
from django.core.mail import send_mail
from user.models import User, OTPVerification
from .models import Notification
from django.conf import settings
import logging

@shared_task
def send_otp_notification(email, phone_number, otp_code):
    """
    Celery task to send OTP via email and SMS, with audit logging.
    """
    try:
        # Email notification
        user = User.objects.filter(email=email).first()
        if user:
            Notification.objects.create(
                user=user,
                notification_type="EMAIL",
                recipient=email,
                message=f"Your OTP is {otp_code}"
            )
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        # SMS notification (stub, integrate with SMS gateway)
        if phone_number:
            Notification.objects.create(
                user=user,
                notification_type="SMS",
                recipient=phone_number,
                message=f"Your OTP is {otp_code}"
            )
            # TODO: Integrate with SMS gateway here
    except Exception as e:
        logging.error(f"Failed to send OTP notification: {e}")
        if user:
            Notification.objects.create(
                user=user,
                notification_type="EMAIL",
                recipient=email,
                message=f"Your OTP is {otp_code}",
                status="FAILED",
                error_message=str(e)
            )
