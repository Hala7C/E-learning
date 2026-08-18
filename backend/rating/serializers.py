from rest_framework import serializers
from .models import Rating
from mainAuth.serializers import UserRegistrationSerializer

class RatingSerializer(serializers.ModelSerializer):
    CONTENTTYPE_CHOICIES=[('course','course'),('trainer','trainer'),('liveSessions','liveSessions')]
    choice=serializers.ChoiceField(choices=CONTENTTYPE_CHOICIES,read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'rate_value','content_type' ,'user', 'object_id','choice']

