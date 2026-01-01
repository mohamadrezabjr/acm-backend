import secrets
from rest_framework_simplejwt.tokens import RefreshToken

def generate_random_otp():
    return f"{secrets.randbelow(1_000_000):06d}"

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }