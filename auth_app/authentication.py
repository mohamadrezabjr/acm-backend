from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from auth_app.models import User


class JWTAuthenticationByCookie(BaseAuthentication):

    def authenticate(self, request):
        token = request.COOKIES.get("access_token")

        if not token :
            return None

        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            user = User.objects.get(id = user_id)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        return (user, None)