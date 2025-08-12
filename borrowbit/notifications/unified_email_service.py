import os
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from .models import Notification, EmailTemplate
from .smtp_email_service import smtp_email_service
# from .email_service import email_service as resend_email_service

logger = logging.getLogger(__name__)

class UnifiedEmailService:
    """Unified email service that can use SMTP or Resend based on configuration"""
    
    def __init__(self):
        # Determine which email service to use
        self.email_provider = os.environ.get('EMAIL_PROVIDER', 'SMTP').upper()
        
        # Validate provider
        if self.email_provider not in ['SMTP', 'RESEND']:
            logger.warning(f"Invalid EMAIL_PROVIDER: {self.email_provider}. Defaulting to SMTP.")
            self.email_provider = 'SMTP'
        
        logger.info(f"Unified Email Service initialized with provider: {self.email_provider}")
        
        # Set the active service
        if self.email_provider == 'SMTP':
            self.active_service = smtp_email_service
        else:
            self.active_service = resend_email_service
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = "",
        from_email: str = None,
        from_name: str = None,
        reply_to: str = None,
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send email using the configured provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            from_email: Sender email (optional)
            from_name: Sender name (optional)
            reply_to: Reply-to email (optional)
            attachments: List of attachment dictionaries
        
        Returns:
            Dict containing success status and response data
        """
        try:
            logger.info(f"Sending email via {self.email_provider} to {to_email}")
            result = self.active_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name,
                reply_to=reply_to,
                attachments=attachments
            )
            
            # Add provider info to result
            result['provider'] = self.email_provider
            return result
            
        except Exception as e:
            logger.error(f"Failed to send email via {self.email_provider}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.email_provider
            }
    
    def send_template_email(
        self,
        template_type: str,
        to_email: str,
        context: Dict[str, Any],
        from_email: str = None,
        from_name: str = None
    ) -> Dict[str, Any]:
        """
        Send email using a template
        
        Args:
            template_type: Type of email template to use
            to_email: Recipient email address
            context: Context data for template rendering
            from_email: Sender email (optional)
            from_name: Sender name (optional)
        
        Returns:
            Dict containing success status and response data
        """
        try:
            logger.info(f"Sending template email via {self.email_provider} to {to_email}")
            result = self.active_service.send_template_email(
                template_type=template_type,
                to_email=to_email,
                context=context,
                from_email=from_email,
                from_name=from_name
            )
            
            # Add provider info to result
            result['provider'] = self.email_provider
            return result
            
        except Exception as e:
            logger.error(f"Failed to send template email via {self.email_provider}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.email_provider
            }
    
    def send_notification_email(self, notification: Notification) -> bool:
        """
        Send email for a notification record
        
        Args:
            notification: Notification instance to send
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending notification email via {self.email_provider}")
            return self.active_service.send_notification_email(notification)
            
        except Exception as e:
            logger.error(f"Failed to send notification email via {self.email_provider}: {str(e)}")
            notification.mark_failed(str(e))
            return False
    
    def retry_failed_notifications(self, max_retries: int = 3) -> Dict[str, int]:
        """
        Retry sending failed notifications
        
        Args:
            max_retries: Maximum number of retries per notification
        
        Returns:
            Dict with retry statistics
        """
        try:
            logger.info(f"Retrying failed notifications via {self.email_provider}")
            result = self.active_service.retry_failed_notifications(max_retries)
            result['provider'] = self.email_provider
            return result
            
        except Exception as e:
            logger.error(f"Failed to retry notifications via {self.email_provider}: {str(e)}")
            return {
                "retried": 0,
                "success": 0,
                "failed": 0,
                "provider": self.email_provider,
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test email service connection
        
        Returns:
            Dict with test results
        """
        try:
            logger.info(f"Testing {self.email_provider} connection")
            
            if hasattr(self.active_service, 'test_connection'):
                result = self.active_service.test_connection()
            else:
                # For services without test_connection method, try sending a test email
                result = self.send_email(
                    to_email=self.active_service.from_email,
                    subject="Connection Test",
                    html_content="<p>This is a test email to verify the connection.</p>",
                    text_content="This is a test email to verify the connection."
                )
            
            result['provider'] = self.email_provider
            return result
            
        except Exception as e:
            logger.error(f"Failed to test {self.email_provider} connection: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.email_provider
            }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current email provider
        
        Returns:
            Dict with provider information
        """
        info = {
            "provider": self.email_provider,
            "active_service": self.active_service.__class__.__name__
        }
        
        if self.email_provider == 'SMTP':
            info.update({
                "host": self.active_service.smtp_host,
                "port": self.active_service.smtp_port,
                "tls": self.active_service.smtp_use_tls,
                "ssl": self.active_service.smtp_use_ssl,
                "username_configured": bool(self.active_service.smtp_username),
                "password_configured": bool(self.active_service.smtp_password)
            })
        else:  # RESEND
            info.update({
                "api_key_configured": bool(self.active_service.api_key),
                "from_email": self.active_service.from_email,
                "from_name": self.active_service.from_name
            })
        
        return info
    
    def switch_provider(self, provider: str) -> bool:
        """
        Switch email provider at runtime
        
        Args:
            provider: New provider ('SMTP' or 'RESEND')
        
        Returns:
            bool: True if switched successfully, False otherwise
        """
        provider = provider.upper()
        
        if provider not in ['SMTP', 'RESEND']:
            logger.error(f"Invalid provider: {provider}")
            return False
        
        try:
            if provider == 'SMTP':
                self.active_service = smtp_email_service
            else:
                self.active_service = resend_email_service
            
            self.email_provider = provider
            logger.info(f"Switched email provider to {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch provider to {provider}: {str(e)}")
            return False

# Global unified email service instance
unified_email_service = UnifiedEmailService()
