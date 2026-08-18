from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Token '):
            return None

        token = auth_header.split(' ')[1]

        try:
            user = User.objects.get(auth_token=token)
            return user, token

        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')