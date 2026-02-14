import os
import secrets
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dotenv import load_dotenv

load_dotenv()

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
        str(os.environ.get('EMAIL_HOST_USER')),
        [user_email],
        html_message=html_message,
    )

def send_otp_email_for_password_reset(user_email, otp):
    subject = "کد درخواست تغییر رمز - انجمن ACM"

    html_message = render_to_string('emails/password_reset.html', {
        'otp_code': otp,
    })

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        str(os.environ.get('EMAIL_HOST_USER')),
        [user_email],
        html_message=html_message,
    )