import secrets
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.html import strip_tags

def generate_random_otp():
    return f"{secrets.randbelow(1_000_000):06d}"

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def send_otp_email_for_registration(user_email, otp):
    subject = 'کد تایید ثبت‌نام - انجمن ACM'


    # Render HTML template
    html_message = render_to_string('emails/otp_verification.html', {
        'otp_code': otp,
    })

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'acm@khu.ac.ir',
        [user_email],
        html_message=html_message,
    )