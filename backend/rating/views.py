from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.contenttypes.models import ContentType
from .models import Rating
from .serializers import RatingSerializer
from mainAuth.models import CustomUser
from trainer.models import Course, LiveSessionDetails

class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def list(self, request):
        rate = Rating.objects.all()
        serializer = RatingSerializer(rate, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        choice = request.data.get('choice')
        content_type_model = 'mainAuth' if choice == 'trainer' else 'trainer'
        content_type = ContentType.objects.get(app_label=content_type_model, model=choice)
        request.data['user'] = user.id
        request.data['content_type'] = content_type.id
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
