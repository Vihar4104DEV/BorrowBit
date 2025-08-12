from django.core.management.base import BaseCommand
from notifications.models import EmailTemplate

class Command(BaseCommand):
    help = 'Set up default email templates for the application'

    def handle(self, *args, **options):
        templates_data = [
            {
                'name': 'Welcome Email',
                'template_type': 'WELCOME_EMAIL',
                'subject': 'Welcome to BorrowBit, {{ user_name }}!',
                'html_content': '<h1>Welcome {{ user_name }}!</h1><p>Welcome to BorrowBit!</p>',
                'text_content': 'Welcome {{ user_name }}! Welcome to BorrowBit!'
            },
            {
                'name': 'OTP Verification',
                'template_type': 'OTP_VERIFICATION',
                'subject': 'Your BorrowBit Verification Code',
                'html_content': '<h1>Your verification code: {{ otp_code }}</h1>',
                'text_content': 'Your verification code: {{ otp_code }}'
            },
            {
                'name': 'Rental Confirmation',
                'template_type': 'RENTAL_CONFIRMATION',
                'subject': 'Rental Confirmed: {{ product_name }}',
                'html_content': '<h1>Rental Confirmed!</h1><p>Your rental for {{ product_name }} is confirmed.</p>',
                'text_content': 'Rental Confirmed! Your rental for {{ product_name }} is confirmed.'
            }
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates_data:
            template, created = EmailTemplate.objects.update_or_create(
                template_type=template_data['template_type'],
                defaults={
                    'name': template_data['name'],
                    'subject': template_data['subject'],
                    'html_content': template_data['html_content'],
                    'text_content': template_data['text_content'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up {created_count} new templates and updated {updated_count} existing templates.'
            )
        )
