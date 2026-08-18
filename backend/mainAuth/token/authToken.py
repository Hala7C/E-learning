
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

class CustomTokenStrategy:
    @classmethod
    def obtain(cls, user):
        token, created = Token.objects.get_or_create(user=user)
        print(token)
        return {
            "access": str(token),
            "user": user,
        }