from django.core.management.base import BaseCommand, CommandError
from django.template import engines
from django.utils.timezone import now
from notifications.unified_email_service import unified_email_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test SMTP email service connection and send test emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--provider',
            type=str,
            choices=['SMTP', 'RESEND'],
            help='Email provider to test (SMTP or RESEND)',
        )
        parser.add_argument(
            '--switch',
            action='store_true',
            help='Switch to the specified provider before testing',
        )

    def handle(self, *args, **options):
        # Switch provider if requested
        if options['provider'] and options['switch']:
            success = unified_email_service.switch_provider(options['provider'])
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Switched to {options["provider"]} provider')
                )
            else:
                raise CommandError(f'Failed to switch to {options["provider"]} provider')

        provider_info = unified_email_service.get_provider_info()
        self.stdout.write(f"Current email provider: {provider_info['provider']}")
        self.stdout.write(f"Active service: {provider_info['active_service']}")

        if provider_info['provider'] == 'SMTP':
            self.stdout.write(f"SMTP Host: {provider_info['host']}:{provider_info['port']}")
            self.stdout.write(f"TLS: {provider_info['tls']}, SSL: {provider_info['ssl']}")
            self.stdout.write(f"Username configured: {provider_info['username_configured']}")
            self.stdout.write(f"Password configured: {provider_info['password_configured']}")
        else:
            self.stdout.write(f"API Key configured: {provider_info['api_key_configured']}")
            self.stdout.write(f"From Email: {provider_info['from_email']}")
            self.stdout.write(f"From Name: {provider_info['from_name']}")

        self.stdout.write("\nTesting email service connection...")
        test_result = unified_email_service.test_connection()
        
        if test_result['success']:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Connection test successful: {test_result['message']}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Connection test failed: {test_result['error']}")
            )

        if options['to']:
            self.stdout.write(f"\nSending test email to {options['to']}...")

            # Prepare context for the email template
            context = {
                'subject': "BorrowBit Email Service Test",
                'email_body': """
                    <p>Hello,</p>
                    <p>This is a test email to verify your email service setup.</p>
                    <p>Thank you for using BorrowBit!</p>
                """,
                'year': now().year,
            }

            # Raw HTML email template with placeholders for Django templating
            raw_html_template = """
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ subject }}</title>
                <link href="https://fonts.googleapis.com/css?family=Montserrat:400,600&display=swap" rel="stylesheet">
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        background: linear-gradient(135deg, #e0f7fa 0%, #f5f6fa 100%);
                        font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
                        color: #333;
                    }
                    .email-container {
                        max-width: 650px;
                        margin: 40px auto;
                        background: #fff;
                        border-radius: 18px;
                        overflow: hidden;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                        border: 1px solid #e0e0e0;
                        animation: fadeIn 1s;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(30px);}
                        to { opacity: 1; transform: none;}
                    }
                    .header {
                        background: linear-gradient(120deg, #00A86B 60%, #00c37a 100%);
                        color: white;
                        padding: 32px 20px 24px 20px;
                        text-align: center;
                        position: relative;
                    }
                    .header img {
                        height: 64px;
                        margin-bottom: 10px;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        background: #fff;
                        padding: 6px;
                    }
                    .header h2 {
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                        letter-spacing: 1px;
                        text-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    }
                    .header .subtitle {
                        margin-top: 8px;
                        font-size: 15px;
                        font-weight: 400;
                        opacity: 0.85;
                        letter-spacing: 0.2px;
                    }
                    .content {
                        padding: 32px 28px 24px 28px;
                        font-size: 16px;
                        line-height: 1.7;
                        color: #444;
                        background: #f9fafb;
                    }
                    .content p {
                        margin-bottom: 18px;
                    }
                    .btn {
                        display: inline-block;
                        padding: 14px 32px;
                        background: linear-gradient(90deg, #00A86B 60%, #00c37a 100%);
                        color: #fff;
                        font-size: 16px;
                        font-weight: 600;
                        border-radius: 8px;
                        text-decoration: none;
                        box-shadow: 0 2px 8px rgba(0,168,107,0.10);
                        transition: background 0.3s, transform 0.2s;
                        margin: 18px 0;
                        letter-spacing: 0.5px;
                    }
                    .btn:hover {
                        background: linear-gradient(90deg, #008f5e 60%, #00b06b 100%);
                        transform: translateY(-2px) scale(1.03);
                    }
                    .divider {
                        border: none;
                        border-top: 1.5px solid #e0e0e0;
                        margin: 0 28px;
                    }
                    .footer {
                        background: #f5f6fa;
                        padding: 22px 20px 18px 20px;
                        font-size: 13px;
                        color: #888;
                        text-align: center;
                        border-top: 1px solid #eee;
                    }
                    .footer p {
                        margin: 7px 0;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 6px;
                    }
                    .footer .icon {
                        width: 17px;
                        height: 17px;
                        vertical-align: middle;
                        margin-right: 4px;
                        opacity: 0.8;
                    }
                    .social-links {
                        margin: 12px 0 0 0;
                    }
                    .social-links a {
                        display: inline-block;
                        margin: 0 7px;
                        opacity: 0.85;
                        transition: opacity 0.2s;
                    }
                    .social-links a:hover {
                        opacity: 1;
                    }
                    .social-links img {
                        width: 22px;
                        height: 22px;
                        vertical-align: middle;
                    }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <!-- Header -->
                    <div class="header">
                        <h2>BorrowBit</h2>
                        <div class="subtitle">Your Trusted Rental Partner</div>
                    </div>

                    <!-- Content -->
                    <div class="content">
                        {{ email_body|safe }}
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
                        <p style="margin-top: 12px;">&copy; {{ year }} <b>BorrowBit</b>. All Rights Reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Render the template with Django's template engine
            django_engine = engines['django']
            html_content = django_engine.from_string(raw_html_template).render(context)

            test_result = unified_email_service.send_email(
                to_email=options['to'],
                subject=context['subject'],
                html_content=html_content
            )

            if test_result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Test email sent successfully to {options['to']}")
                )
                if 'message_id' in test_result:
                    self.stdout.write(f"Message ID: {test_result['message_id']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to send test email: {test_result['error']}")
                )

        self.stdout.write("\n" + "="*50)
        self.stdout.write("CONFIGURATION TIPS:")
        self.stdout.write("="*50)
        
        if provider_info['provider'] == 'SMTP':
            if not provider_info['username_configured'] or not provider_info['password_configured']:
                self.stdout.write(
                    self.style.WARNING("⚠️  SMTP credentials not configured!")
                )
                self.stdout.write("Set these environment variables:")
                self.stdout.write("  SMTP_USERNAME=your_email@gmail.com")
                self.stdout.write("  SMTP_PASSWORD=your_app_password")
                self.stdout.write("  SMTP_HOST=smtp.gmail.com")
                self.stdout.write("  SMTP_PORT=587")
                self.stdout.write("  SMTP_USE_TLS=True")
                self.stdout.write("  SMTP_USE_SSL=False")
                self.stdout.write("\nFor Gmail, use App Passwords instead of your regular password.")
            else:
                self.stdout.write("✅ SMTP credentials are configured")
        else:
            if not provider_info['api_key_configured']:
                self.stdout.write(
                    self.style.WARNING("⚠️  Resend API key not configured!")
                )
                self.stdout.write("Set this environment variable:")
                self.stdout.write("  RESEND_API_KEY=your_resend_api_key")
            else:
                self.stdout.write("✅ Resend API key is configured")

        self.stdout.write("\nTo switch providers, use:")
        self.stdout.write("  python manage.py test_smtp --provider SMTP --switch")
        self.stdout.write("  python manage.py test_smtp --provider RESEND --switch")
