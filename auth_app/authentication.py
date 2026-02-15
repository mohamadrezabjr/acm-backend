from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, T, AuthUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model


class JWTAuthenticationByCookie(BaseAuthentication):

    def authenticate(self, request):
        User = get_user_model()
        token = request.COOKIES.get("access_token")

        if not token :
            return None

        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            user = User.objects.get(id = user_id)

        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        else :
            token_version = access_token.get('token_version')
            if token_version < user.token_version:
                raise AuthenticationFailed("Invalid or expired token")

        return (user, None)

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls: type[T], user: AuthUser) -> T:
        token = super().for_user(user)
        token['token_version'] = user.token_version
        return token