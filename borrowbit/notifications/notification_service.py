import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.template import Template, Context
from user.models import User
from .models import Notification, EmailTemplate
from .unified_email_service import unified_email_service
from .template_utils import EmailTemplateRenderer

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling different types of notifications"""
    
    @staticmethod
    def create_notification(
        user: User,
        notification_type: str,
        category: str,
        subject: str,
        message: str,
        html_content: str = "",
        related_object_type: str = "",
        related_object_id: int = None
    ) -> Notification:
        """
        Create a notification record
        
        Args:
            user: User to send notification to
            notification_type: Type of notification (EMAIL, SMS, PUSH)
            category: Category of notification
            subject: Notification subject
            message: Plain text message
            html_content: HTML content (for emails)
            related_object_type: Type of related object
            related_object_id: ID of related object
        
        Returns:
            Created notification instance
        """
        try:
            # Handle related_object_id properly
            if related_object_id is not None:
                # Convert to string to handle UUIDs and other types
                try:
                    related_object_id = str(related_object_id)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid related_object_id: {related_object_id}, setting to None")
                    related_object_id = None
            
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                category=category,
                recipient=user.email if notification_type == "EMAIL" else user.phone_number,
                subject=subject,
                message=message,
                html_content=html_content,
                related_object_type=related_object_type,
                related_object_id=related_object_id
            )
            
            logger.info(f"Created notification: {notification.id} for user {user.email}")
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification for user {user.email}: {str(e)}")
            logger.error(f"User ID: {user.id}, Type: {type(user.id)}")
            logger.error(f"Related object ID: {related_object_id}, Type: {type(related_object_id)}")
            raise
    
    @staticmethod
    def send_user_registration_email(user: User) -> bool:
        """Send welcome email to newly registered user"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "email": user.email,
                "registration_date": user.created_at.strftime("%B %d, %Y"),
                "login_url": "https://borrowbit.com/login",
                "support_email": "support@borrowbit.com"
            }
            
            # Create notification record
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="USER_REGISTRATION",
                subject="Welcome to BorrowBit!",
                message=f"Hi {context['user_name']}, welcome to BorrowBit!",
                html_content=NotificationService._get_welcome_email_html(context),
                related_object_type="user",
                related_object_id=user.id
            )
            
            # Send email
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send registration email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_rental_confirmation_email(user: User, rental_data: Dict[str, Any]) -> bool:
        """Send rental confirmation email"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "rental_id": rental_data.get("rental_id"),
                "product_name": rental_data.get("product_name"),
                "rental_date": rental_data.get("rental_date"),
                "return_date": rental_data.get("return_date"),
                "total_amount": rental_data.get("total_amount"),
                "delivery_address": rental_data.get("delivery_address"),
                "tracking_url": rental_data.get("tracking_url", ""),
                "support_email": "support@borrowbit.com"
            }
            
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="RENTAL_CONFIRMATION",
                subject=f"Rental Confirmed: {context['product_name']}",
                message=f"Your rental for {context['product_name']} has been confirmed.",
                html_content=NotificationService._get_rental_confirmation_html(context),
                related_object_type="rental",
                related_object_id=rental_data.get("rental_id")
            )
            
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send rental confirmation email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_product_delivery_email(user: User, delivery_data: Dict[str, Any]) -> bool:
        """Send product delivery notification email"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "product_name": delivery_data.get("product_name"),
                "delivery_date": delivery_data.get("delivery_date"),
                "delivery_address": delivery_data.get("delivery_address"),
                "tracking_number": delivery_data.get("tracking_number"),
                "delivery_partner": delivery_data.get("delivery_partner"),
                "estimated_time": delivery_data.get("estimated_time"),
                "support_email": "support@borrowbit.com"
            }
            
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="PRODUCT_DELIVERY",
                subject=f"Your {context['product_name']} is on its way!",
                message=f"Your {context['product_name']} is being delivered today.",
                html_content=NotificationService._get_delivery_email_html(context),
                related_object_type="delivery",
                related_object_id=delivery_data.get("delivery_id")
            )
            
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send delivery email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_product_return_reminder_email(user: User, return_data: Dict[str, Any]) -> bool:
        """Send product return reminder email"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "product_name": return_data.get("product_name"),
                "return_date": return_data.get("return_date"),
                "pickup_address": return_data.get("pickup_address"),
                "rental_id": return_data.get("rental_id"),
                "days_remaining": return_data.get("days_remaining"),
                "support_email": "support@borrowbit.com"
            }
            
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="PRODUCT_RETURN",
                subject=f"Return Reminder: {context['product_name']}",
                message=f"Please return {context['product_name']} by {context['return_date']}.",
                html_content=NotificationService._get_return_reminder_html(context),
                related_object_type="rental",
                related_object_id=return_data.get("rental_id")
            )
            
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send return reminder email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_success_email(user: User, payment_data: Dict[str, Any]) -> bool:
        """Send payment success email"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "amount": payment_data.get("amount"),
                "payment_method": payment_data.get("payment_method"),
                "transaction_id": payment_data.get("transaction_id"),
                "payment_date": payment_data.get("payment_date"),
                "rental_id": payment_data.get("rental_id"),
                "support_email": "support@borrowbit.com"
            }
            
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="PAYMENT_SUCCESS",
                subject="Payment Successful ✅",
                message=f"Payment of ${context['amount']} was successful.",
                html_content=NotificationService._get_payment_success_html(context),
                related_object_type="payment",
                related_object_id=payment_data.get("payment_id")
            )
            
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send payment success email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_email(user: User, otp_code: str) -> bool:
        """Send OTP verification email"""
        try:
            context = {
                "user_name": user.first_name or user.email,
                "otp_code": otp_code,
                "expiry_time": "10 minutes",
                "support_email": "support@borrowbit.com"
            }
            
            notification = NotificationService.create_notification(
                user=user,
                notification_type="EMAIL",
                category="OTP_VERIFICATION",
                subject="Your BorrowBit Verification Code",
                message=f"Your verification code is: {otp_code}",
                html_content=NotificationService._get_otp_email_html(context),
                related_object_type="user",
                related_object_id=user.id
            )
            
            return unified_email_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
            return False
    
    # HTML Template Methods
    @staticmethod
    def _get_welcome_email_html(context: Dict[str, Any]) -> str:
        """Generate welcome email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>Welcome to BorrowBit! We're excited to have you join our community of smart renters.</p>
        
        <p>With BorrowBit, you can:</p>
        <ul>
            <li>Rent products for any duration</li>
            <li>Save money by renting instead of buying</li>
            <li>Access a wide variety of products</li>
            <li>Enjoy hassle-free delivery and returns</li>
        </ul>
        
        <p>Your account was created on <strong>{context['registration_date']}</strong>.</p>
        
        <div style="text-align: center;">
            <a href="{context['login_url']}" class="btn">Start Renting Now</a>
        </div>
        
        <p>If you have any questions, feel free to reach out to us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Happy renting!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Welcome to BorrowBit!",
            email_body=email_body,
            context=context
        )
    
    @staticmethod
    def _get_rental_confirmation_html(context: Dict[str, Any]) -> str:
        """Generate rental confirmation email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>Great news! Your rental has been confirmed and is being processed.</p>
        
        <div class="details-box">
            <h3>Rental Details:</h3>
            <div class="details-row">
                <span class="details-label">Product:</span>
                <span class="details-value">{context['product_name']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Rental ID:</span>
                <span class="details-value">#{context['rental_id']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Rental Date:</span>
                <span class="details-value">{context['rental_date']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Return Date:</span>
                <span class="details-value">{context['return_date']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Total Amount:</span>
                <span class="details-value">${context['total_amount']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Delivery Address:</span>
                <span class="details-value">{context['delivery_address']}</span>
            </div>
        </div>
        
        <p>We'll notify you when your product is ready for delivery.</p>
        
        {f'<div style="text-align: center;"><a href="{context["tracking_url"]}" class="btn">Track Your Order</a></div>' if context.get('tracking_url') else ''}
        
        <p>If you have any questions, contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Thank you for choosing BorrowBit!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Rental Confirmed - BorrowBit",
            email_body=email_body,
            context=context
        )
    
    @staticmethod
    def _get_delivery_email_html(context: Dict[str, Any]) -> str:
        """Generate delivery notification email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>Your {context['product_name']} is being delivered today!</p>
        
        <div class="details-box">
            <h3>Delivery Details:</h3>
            <div class="details-row">
                <span class="details-label">Product:</span>
                <span class="details-value">{context['product_name']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Delivery Date:</span>
                <span class="details-value">{context['delivery_date']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Estimated Time:</span>
                <span class="details-value">{context['estimated_time']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Delivery Address:</span>
                <span class="details-value">{context['delivery_address']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Tracking Number:</span>
                <span class="details-value">{context['tracking_number']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Delivery Partner:</span>
                <span class="details-value">{context['delivery_partner']}</span>
            </div>
        </div>
        
        <p>Please ensure someone is available to receive the delivery.</p>
        
        <p>If you have any questions, contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Thank you for choosing BorrowBit!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Your Product is on the Way! - BorrowBit",
            email_body=email_body,
            context=context
        )
    
    @staticmethod
    def _get_return_reminder_html(context: Dict[str, Any]) -> str:
        """Generate return reminder email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>This is a friendly reminder that your rental period is ending soon.</p>
        
        <div class="details-box">
            <h3>Return Details:</h3>
            <div class="details-row">
                <span class="details-label">Product:</span>
                <span class="details-value">{context['product_name']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Return Date:</span>
                <span class="details-value">{context['return_date']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Days Remaining:</span>
                <span class="details-value">{context['days_remaining']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Pickup Address:</span>
                <span class="details-value">{context['pickup_address']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Rental ID:</span>
                <span class="details-value">#{context['rental_id']}</span>
            </div>
        </div>
        
        <p>Please ensure the product is ready for pickup on the return date.</p>
        
        <p>If you need to extend your rental, please contact us as soon as possible.</p>
        
        <p>If you have any questions, contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Thank you for choosing BorrowBit!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Return Reminder - BorrowBit",
            email_body=email_body,
            context=context
        )
    
    @staticmethod
    def _get_payment_success_html(context: Dict[str, Any]) -> str:
        """Generate payment success email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>Your payment has been processed successfully!</p>
        
        <div class="details-box">
            <h3>Payment Details:</h3>
            <div class="details-row">
                <span class="details-label">Amount:</span>
                <span class="details-value">${context['amount']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Payment Method:</span>
                <span class="details-value">{context['payment_method']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Transaction ID:</span>
                <span class="details-value">{context['transaction_id']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Payment Date:</span>
                <span class="details-value">{context['payment_date']}</span>
            </div>
            <div class="details-row">
                <span class="details-label">Rental ID:</span>
                <span class="details-value">#{context['rental_id']}</span>
            </div>
        </div>
        
        <p>A receipt has been sent to your email address.</p>
        
        <p>If you have any questions, contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Thank you for choosing BorrowBit!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Payment Successful - BorrowBit",
            email_body=email_body,
            context=context
        )
    
    @staticmethod
    def _get_otp_email_html(context: Dict[str, Any]) -> str:
        """Generate OTP email HTML content"""
        email_body = f"""
        <h2>Hi {context['user_name']},</h2>
        <p>Here's your verification code to complete your account setup:</p>
        
        <div class="otp-code">
            {context['otp_code']}
        </div>
        
        <p><strong>This code will expire in {context['expiry_time']}.</strong></p>
        
        <p>If you didn't request this code, please ignore this email.</p>
        
        <p>If you have any questions, contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
        
        <p>Thank you for choosing BorrowBit!<br>The BorrowBit Team</p>
        """
        
        return EmailTemplateRenderer.render_simple_email(
            subject="Your Verification Code - BorrowBit",
            email_body=email_body,
            context=context
        )
