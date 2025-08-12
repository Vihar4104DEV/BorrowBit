import os
from datetime import datetime
from django.template import Template, Context
from django.template.loader import get_template
from django.conf import settings

class EmailTemplateRenderer:
    """Utility class for rendering email templates with consistent base design"""
    
    @staticmethod
    def render_email_template(template_name: str, context: dict) -> str:
        """
        Render an email template using the base template
        
        Args:
            template_name: Name of the specific email template
            context: Context data for the template
            
        Returns:
            Rendered HTML string
        """
        try:
            # Add common context variables
            context.update({
                'year': datetime.now().year,
                'subject': context.get('subject', 'BorrowBit Notification'),
            })
            
            # Get the base template
            base_template = get_template('notifications/base_email_template.html')
            
            # Render the base template with context
            rendered_html = base_template.render(context)
            
            return rendered_html
            
        except Exception as e:
            # Fallback to simple HTML if template rendering fails
            print(f"Template rendering failed: {e}")
            return EmailTemplateRenderer._get_fallback_html(context)
    
    @staticmethod
    def _get_fallback_html(context: dict) -> str:
        """Generate fallback HTML with the new design"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{context.get('subject', 'BorrowBit Notification')}</title>
        <link href="https://fonts.googleapis.com/css?family=Montserrat:400,600&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #e0f7fa 0%, #f5f6fa 100%);
                font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
                color: #333;
            }}
            .email-container {{
                max-width: 650px;
                margin: 40px auto;
                background: #fff;
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                border: 1px solid #e0e0e0;
            }}
            .header {{
                background: linear-gradient(120deg, #00A86B 60%, #00c37a 100%);
                color: white;
                padding: 32px 20px 24px 20px;
                text-align: center;
                position: relative;
            }}
            .header img {{
                height: 64px;
                margin-bottom: 10px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                background: #fff;
                padding: 6px;
            }}
            .header h2 {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 1px;
                text-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            .header .subtitle {{
                margin-top: 8px;
                font-size: 15px;
                font-weight: 400;
                opacity: 0.85;
                letter-spacing: 0.2px;
            }}
            .content {{
                padding: 32px 28px 24px 28px;
                font-size: 16px;
                line-height: 1.7;
                color: #444;
                background: #f9fafb;
            }}
            .btn {{
                display: inline-block;
                padding: 14px 32px;
                background: linear-gradient(90deg, #00A86B 60%, #00c37a 100%);
                color: #fff;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                text-decoration: none;
                box-shadow: 0 2px 8px rgba(0,168,107,0.10);
                margin: 18px 0;
                letter-spacing: 0.5px;
            }}
            .divider {{
                border: none;
                border-top: 1.5px solid #e0e0e0;
                margin: 0 28px;
            }}
            .footer {{
                background: #f5f6fa;
                padding: 22px 20px 18px 20px;
                font-size: 13px;
                color: #888;
                text-align: center;
                border-top: 1px solid #eee;
            }}
            .footer p {{
                margin: 7px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
            }}
            .footer .icon {{
                width: 17px;
                height: 17px;
                vertical-align: middle;
                margin-right: 4px;
                opacity: 0.8;
            }}
            .social-links {{
                margin: 12px 0 0 0;
            }}
            .social-links a {{
                display: inline-block;
                margin: 0 7px;
                opacity: 0.85;
            }}
            .social-links img {{
                width: 22px;
                height: 22px;
                vertical-align: middle;
            }}
            .details-box {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .details-box h3 {{
                margin-top: 0;
                color: #00A86B;
                font-size: 18px;
                font-weight: 600;
            }}
            .details-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }}
            .details-row:last-child {{
                border-bottom: none;
            }}
            .details-label {{
                font-weight: 600;
                color: #555;
            }}
            .details-value {{
                color: #333;
            }}
            .otp-code {{
                background: linear-gradient(135deg, #00A86B 0%, #00c37a 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                font-size: 32px;
                font-weight: 700;
                letter-spacing: 4px;
                margin: 20px 0;
                box-shadow: 0 4px 16px rgba(0,168,107,0.2);
            }}
        </style>
        </head>
        <body>

        <div class="email-container">

            <!-- Header -->
            <div class="header">
                <img src="https://via.placeholder.com/64x64/00A86B/FFFFFF?text=BB" alt="BorrowBit Logo">
                <h2>BorrowBit</h2>
                <div class="subtitle">Your Trusted Rental Partner</div>
            </div>

            <!-- Content -->
            <div class="content">
                {context.get('email_body', '')}
            </div>

            <hr class="divider">

            <!-- Footer -->
            <div class="footer">
                <p><img class="icon" src="https://cdn-icons-png.flaticon.com/512/25/25694.png" alt="address"> 123 Rental Street, Mumbai, India</p>
                <p><img class="icon" src="https://cdn-icons-png.flaticon.com/512/159/159832.png" alt="phone"> +91 9876543210</p>
                <p><img class="icon" src="https://cdn-icons-png.flaticon.com/512/561/561127.png" alt="email"> support@borrowbit.com</p>
                <div class="social-links">
                    <a href="https://facebook.com/" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" alt="Facebook"></a>
                    <a href="https://twitter.com/" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" alt="Twitter"></a>
                    <a href="https://instagram.com/" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733558.png" alt="Instagram"></a>
                </div>
                <p style="margin-top: 12px;">&copy; {context.get('year', datetime.now().year)} <b>BorrowBit</b>. All Rights Reserved.</p>
            </div>

        </div>

        </body>
        </html>
        """
    
    @staticmethod
    def render_simple_email(subject: str, email_body: str, context: dict = None) -> str:
        """
        Render a simple email using the base template
        
        Args:
            subject: Email subject
            email_body: HTML content for the email body
            context: Additional context data
            
        Returns:
            Rendered HTML string
        """
        if context is None:
            context = {}
            
        context.update({
            'subject': subject,
            'email_body': email_body,
        })
        
        return EmailTemplateRenderer.render_email_template('base_email_template.html', context)
