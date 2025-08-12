import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.template import Template, Context
from django.utils import timezone
from .models import Notification, EmailTemplate

logger = logging.getLogger(__name__)

class SMTPEmailService:
    """SMTP-based email service for sending notifications"""
    
    def __init__(self):
        # SMTP Configuration
        self.smtp_host = os.environ.get('SMTP_HOST') or getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT') or getattr(settings, 'SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME') or getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD') or getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = os.environ.get('SMTP_USE_TLS', 'True').lower() == 'true'
        self.smtp_use_ssl = os.environ.get('SMTP_USE_SSL', 'False').lower() == 'true'
        
        # Email Configuration
        self.from_email = os.environ.get('DEFAULT_FROM_EMAIL') or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@borrowbit.com')
        self.from_name = os.environ.get('FROM_NAME') or getattr(settings, 'FROM_NAME', 'BorrowBit')
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
        
        logger.info(f"SMTP Email service initialized with host: {self.smtp_host}:{self.smtp_port}")
        logger.info(f"TLS: {self.smtp_use_tls}, SSL: {self.smtp_use_ssl}")
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = "",
        from_email: str = None,
        from_name: str = None,
        reply_to: str = None,
        attachments: List[Dict] = None
    ) -> MIMEMultipart:
        """Create a MIME message with all components"""
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name or self.from_name} <{from_email or self.from_email}>"
        msg['To'] = to_email
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Add text part
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        # Add HTML part
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                try:
                    with open(attachment['file_path'], 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment.get("filename", "attachment")}'
                    )
                    msg.attach(part)
                except Exception as e:
                    logger.error(f"Failed to attach file {attachment.get('file_path')}: {e}")
        
        return msg
    
    def _get_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        if self.smtp_use_ssl:
            # Use SSL connection
            context = ssl.create_default_context()
            smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context)
        else:
            # Use regular connection
            smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            # Start TLS if required
            if self.smtp_use_tls:
                smtp.starttls(context=ssl.create_default_context())
        
        # Login if credentials are provided
        if self.smtp_username and self.smtp_password:
            smtp.login(self.smtp_username, self.smtp_password)
        
        return smtp
    
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
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            from_email: Sender email (optional)
            from_name: Sender name (optional)
            reply_to: Reply-to email (optional)
            attachments: List of attachment dictionaries with 'file_path' and 'filename' keys
        
        Returns:
            Dict containing success status and response data
        """
        smtp = None
        try:
            # Create message
            msg = self._create_message(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name,
                reply_to=reply_to,
                attachments=attachments
            )
            
            # Create SMTP connection
            smtp = self._get_smtp_connection()
            
            # Send email
            logger.info(f"Attempting to send email to {to_email}")
            smtp.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipient": to_email
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "authentication"
            }
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient refused: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "recipient"
            }
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP server disconnected: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "connection"
            }
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "smtp"
            }
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "unknown"
            }
        finally:
            if smtp:
                try:
                    smtp.quit()
                except Exception as e:
                    logger.warning(f"Error closing SMTP connection: {e}")
    
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
            # Get template
            template = EmailTemplate.objects.filter(
                template_type=template_type,
                is_active=True
            ).first()
            
            if not template:
                logger.error(f"Template not found for type: {template_type}")
                return {
                    "success": False,
                    "error": f"Template not found for type: {template_type}"
                }
            
            # Render template with context
            subject_template = Template(template.subject)
            html_template = Template(template.html_content)
            text_template = Template(template.text_content) if template.text_content else None
            
            context_obj = Context(context)
            
            subject = subject_template.render(context_obj)
            html_content = html_template.render(context_obj)
            text_content = text_template.render(context_obj) if text_template else ""
            
            # Send email
            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email {template_type} to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
            # Send email
            result = self.send_email(
                to_email=notification.recipient,
                subject=notification.subject,
                html_content=notification.html_content,
                text_content=notification.message
            )
            
            if result["success"]:
                notification.mark_sent()
                logger.info(f"Notification email sent successfully: {notification.id}")
                return True
            else:
                notification.mark_failed(result["error"])
                logger.error(f"Failed to send notification email: {result['error']}")
                return False
                
        except Exception as e:
            notification.mark_failed(str(e))
            logger.error(f"Exception sending notification email: {str(e)}")
            return False
    
    def retry_failed_notifications(self, max_retries: int = 3) -> Dict[str, int]:
        """
        Retry sending failed notifications
        
        Args:
            max_retries: Maximum number of retries per notification
        
        Returns:
            Dict with retry statistics
        """
        failed_notifications = Notification.objects.filter(
            status__in=["FAILED", "RETRYING"],
            retry_count__lt=max_retries,
            notification_type="EMAIL"
        )
        
        success_count = 0
        failure_count = 0
        
        for notification in failed_notifications:
            if self.send_notification_email(notification):
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "retried": failed_notifications.count(),
            "success": success_count,
            "failed": failure_count
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection and authentication
        
        Returns:
            Dict with test results
        """
        smtp = None
        try:
            smtp = self._get_smtp_connection()
            
            # Try to send a test email to ourselves
            test_msg = MIMEMultipart('alternative')
            test_msg['Subject'] = 'SMTP Connection Test'
            test_msg['From'] = f"{self.from_name} <{self.from_email}>"
            test_msg['To'] = self.from_email
            
            text_part = MIMEText('This is a test email to verify SMTP configuration.', 'plain', 'utf-8')
            test_msg.attach(text_part)
            
            smtp.send_message(test_msg)
            
            return {
                "success": True,
                "message": "SMTP connection test successful",
                "host": self.smtp_host,
                "port": self.smtp_port,
                "tls": self.smtp_use_tls,
                "ssl": self.smtp_use_ssl
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": self.smtp_host,
                "port": self.smtp_port,
                "tls": self.smtp_use_tls,
                "ssl": self.smtp_use_ssl
            }
        finally:
            if smtp:
                try:
                    smtp.quit()
                except Exception as e:
                    logger.warning(f"Error closing SMTP connection: {e}")

# Global SMTP email service instance
smtp_email_service = SMTPEmailService()
