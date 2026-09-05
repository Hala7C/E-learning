# Create your views here.
# from .decorators import has_permission
from django.utils.translation import get_language
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import  permission_classes
from .permissions import IsTrainerUser,CoursePolicy
from rest_framework.views import APIView
from .serializers import TrainerProfileSerializers,ApproveProfileSerializers,AddCourseSerializer
from mainAuth.models import TeacherProfile
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from newapp.tasks import send_normal_email
from mainAuth.permissions import IsAdminUser
from .permissions import *
from rest_framework.viewsets import ModelViewSet
from .paginations import CustomPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db import transaction
import requests
from .models import *
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from rest_framework import routers, serializers, viewsets
from django.http import JsonResponse
from parler.utils.context import switch_language
from django.utils.translation import get_language
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from newapp.models import ObjectPerm
from .interfaces import *
# from .service import *
# from newapp.tasks import *
# from .Teams import *
# from .service import *
from newapp.tasks import  ZoomMeeting
from .service import MeetingServices
from datetime import datetime
from rest_framework import status
from .utils import create_auth_signature,create_zoom_user
from django.db.models import Count
from django.http import JsonResponse
from parler.utils.context import switch_language
from django.utils.translation import get_language
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from .serializers import *
from .signals import cycle_added
from newapp.tasks import send_notification_task
from celery import chain
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourseFilter
from .serializers import *
from django.db.models import Q
from django.db.models import Avg
from rating.models import Rating
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import get_object_or_404
from django.http import Http404
import stripe
from eLearning import settings
from mainAuth.models import StudentProfile
from rest_framework.viewsets import ModelViewSet

class StudentProfileViewSet(ModelViewSet):    
    # permission_classes = (DraftPolicy, )
    queryset = StudentProfile.objects.all()
    serializer_class= StudentProfileSerializers
    def list(self,request):
        user=request.user
        profile_exists = StudentProfile.objects.filter(user=user).get()
        ser=StudentProfileSerializers(profile_exists,context={'request': request})
        return Response(ser.data,status=status.HTTP_200_OK)

    # @permission_classes((DraftPolicy,))
    def update(self, request,pk, format=None):
            # request.data._mutable = True
            request.data['user']=request.user.id
            try:
                instance = StudentProfile.objects.get(pk=pk)
            except StudentProfile.DoesNotExist:
                return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
            ser = StudentProfileSerializers(instance, data=request.data,partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data,status=status.HTTP_200_OK)
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)


class PendingTrainerProfile(ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = [DraftProfilePolicy]
    queryset = TeacherProfile.objects.all()
    serializer_class= TrainerProfileSerializers
    def list(self,request):
        PendingProfile =TeacherProfile.objects.filter(status='pending')  # Access the profile using the related name
        ser=TrainerProfileSerializers(PendingProfile,many=True,context={'request': request})
        return Response(ser.data,status=status.HTTP_200_OK)
    
    def update(self, request,pk, format=None):
        user=request.user
        try:
            instance = TeacherProfile.objects.get(pk=pk)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        ser = ApproveProfileSerializers(instance, data=request.data)
        if ser.is_valid():
            ser.save()
            s = ser.data['status']
            email_body=f'your request for being a trainer on our site <eLearning> is {s} '
            data={
                'email_body':email_body,
                'email_subject':"Training Request Resualt",
                'to_email':user.email
            }
            send_normal_email.delay(data=data)
            return Response(ser.data,status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
    
class DraftTrainerProfile(ModelViewSet):    
    permission_classes = [DraftProfilePolicy]
    queryset = TeacherProfile.objects.all()
    serializer_class= TrainerProfileSerializers
    # def list(self, request):
    #     user = request.user
    #     profile = TeacherProfile.objects.filter(user=user).first()
    #     if not profile:
    #         return Response({"error": "No profile yet."}, status=status.HTTP_404_NOT_FOUND)
    #     ser = TrainerProfileSerializers(profile, context={'request': request})
    #     return Response(ser.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        try:
            profile = TeacherProfile.objects.get(user=request.user)
        except TeacherProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()  # .copy() returns a mutable copy either way -
                                    # QueryDict.copy() and dict.copy() both work
        data['status'] = 'draft'
        data['user'] = user.id
        # data['name'] = user.get_full_name
        profile_exists = TeacherProfile.objects.filter(user=user).exists()
        if profile_exists:
            return Response({"error": "A profile for this user is alreay exist"}, status=status.HTTP_400_BAD_REQUEST)
        ser = AddTrainerProfileSerializers(data=data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, format=None):
        data = request.data.copy()
        data['status'] = 'draft'
        data['user'] = request.user.id
        try:
            instance = TeacherProfile.objects.get(pk=pk)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        ser = AddTrainerProfileSerializers(instance, data=data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request,pk):
            try:
                instance = TeacherProfile.objects.get(pk=pk)
                if instance.user==request.user:
                        instance.delete()
                        return Response(status=status.HTTP_204_NO_CONTENT)
                return Response({"massege": "You are not the owner"},status=status.HTTP_403_FORBIDDEN)
            except TeacherProfile.DoesNotExist:
                return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)


class SubmitDraftProfile(ModelViewSet):
    permission_classes = [SubmitProfilePolicy]
    queryset = TeacherProfile.objects.all()
    serializer_class= SubmitTrainerProfileSerializers
    def update(self, request,pk, format=None):
        request.data['status'] = 'pending'      
        request.data['user']=request.user.id  
        try:
                instance = get_object_or_404(TeacherProfile, id=pk)
                # instance = TeacherProfile.objects.get(pk=pk)
        except TeacherProfile.DoesNotExist:
                return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        ser = SubmitTrainerProfileSerializers(instance, data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data,status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
    

class CourseViewSet(ModelViewSet):
    # queryset = Course.objects.all()
    queryset = Course.objects.annotate(num_subscribers=Count('course_subscriptions'))

    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ['created_on','num_subscribers','average_rate']
    filterset_class = CourseFilter
    pagination_class = CustomPagination
    permission_classes=[CoursePolicy]


    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering')

        if ordering == 'average_rate':
            queryset = queryset.annotate(average_rate=Avg('ratings__rate_value')).order_by('average_rate')
        elif ordering == '-average_rate':
            queryset = queryset.annotate(average_rate=Avg('ratings__rate_value')).order_by('-average_rate')
        elif ordering == 'num_subscribers':
            queryset = queryset.order_by('num_subscribers')
        elif ordering == '-num_subscribers':
            queryset = queryset.order_by('-num_subscribers')
        elif ordering == 'created_on':
            queryset = queryset.order_by('created_on')
        elif ordering == '-created_on':
            queryset = queryset.order_by('-created_on')
        
        is_student=self.request.query_params.get('is_student')
        if is_student and is_student.lower() == 'true':
            queryset=queryset.filter(status='published',is_blocked=False)
            
        return queryset

    def list(self,request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page,many=True)
        total_courses = queryset.count()
        response_data = {
            'total_count': total_courses,
            'results': serializer.data
        }
        return self.get_paginated_response(response_data)
    
    
    @action( methods=['get'],detail=False)
    def getTrainerCourse(self,request):
        queryset = self.filter_queryset(self.get_queryset()).filter(trainer=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page if page is not None else queryset, many=True)
        response_data = {'total_count': queryset.count(), 'results': serializer.data}
        return Response({"data": response_data}, status=status.HTTP_200_OK)

    
    # TODO /clean code 
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()          
        videos_data = data.pop('videos', [])
        lives_data = data.pop('lives_data', [])
        data['trainer'] = request.user.id

        serializer = AddCourseSerializer(data=data)
        serializer.is_valid(raise_exception=True)   
        course = serializer.save()                  

        for video_data in videos_data:
            video_data = dict(video_data)
            video_data['course'] = course.id
            s = VedioSectionSerializer(data=video_data)
            s.is_valid(raise_exception=True)
            s.save()
        for live_data in lives_data:
            live_data = dict(live_data)
            live_data['course'] = course.id
            s = LiveSessionMainDataSectionSerializer(data=live_data)
            s.is_valid(raise_exception=True)
            s.save()

        ser = CourseSerializer(instance=course)
        headers = self.get_success_headers(ser.data)
        return Response(ser.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request,pk, format=None):
            try:
                instance = self.get_object()
            except Http404:                      
                return Response({"error": "Object not found."},   
                                status=status.HTTP_404_NOT_FOUND)  
            data = request.data.copy()
            data.pop('trainer', None)
            ser = AddCourseSerializer(instance, data=data, partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data, status=status.HTTP_200_OK)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AddCourseSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_translation(self, request, pk, language_code):
            instance = get_object_or_404(Course, pk=pk)

            # Get the translation in the specified language
            translation = instance.translations.filter(language_code=language_code).first()

            if translation:
                # Delete the translation
                translation.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)  
        
    def destroy(self, request,pk):
        try:
            instance = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        if instance.trainer != request.user:
            return Response({"error": "You are not the owner"},  # fixed "massege" typo
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(methods=['post'],detail=False)
    def give_obj_perm(self, request, pk):    
        instance = get_object_or_404(Course, pk=pk)          
        user = get_object_or_404(CustomUser, pk=request.data.get('user_id'))  
        perm = ObjectPerm.objects.create(content_object=instance)              
        perm.users.add(user)                                                   
        return Response({"message": "permission granted successfully"},        
                        status=status.HTTP_200_OK)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes=[CategoryPolicy]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = AddCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddCategorySerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_translation(self, request, pk, language_code):
        instance = get_object_or_404(Category, pk=pk)
        translation = instance.translations.filter(language_code=language_code).first()
        if translation:
            translation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            instance = Category.objects.get(pk=pk)
            instance.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

class EducationViewSet(ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializers

    def list(self, request, *args, **kwargs):
        user = request.user
        profile = TeacherProfile.objects.get(user=user)
        education = profile.education.all()
        serializer = EducationSerializers(education, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
           return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)
        request.data['trainer_profile'] = profile.id
        serializer = EducationSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, format=None):
        try:
            instance = Education.objects.get(pk=pk)
        except Education.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        profile = TeacherProfile.objects.get(user=request.user)
        if instance.trainer != profile:
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        serializer = EducationSerializers(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user = request.user
        profile = TeacherProfile.objects.get(user=user)
        try:
            instance = Education.objects.get(pk=pk)
            if instance.trainer == profile:
                instance.delete()
                return Response( status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        except Education.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

class EmploymentViewSet(ModelViewSet):
    queryset=Employment.objects.all()
    serializer_class=EmploymentSerializers


    def list(self,request,*args, **kwargs):
        user=request.user
        profile=TeacherProfile.objects.filter(user=user).get()
        employments=profile.employments.all()
        serializer=EmploymentSerializers(employments,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    
    def create(self,request,*args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)
        request.data['trainer_profile'] = profile.id
        serializer = EmploymentSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def update(self,request,pk,format=None):
        try:
            instance = Employment.objects.get(pk=pk)
        except Employment.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmploymentSerializers(instance, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request,pk):
        user=request.user
        profile=TeacherProfile.objects.filter(user=user).get()
        try:
            instance = Employment.objects.get(pk=pk)
            if instance.trainer==profile:
                    instance.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"massege": "You are not the owner"},status=status.HTTP_403_FORBIDDEN)
        except Employment.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
    
class SkillViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializers

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
            skills = profile.skills.all()
            serializer = SkillSerializers(skills, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)
        request.data['trainer_profile'] = profile.id
        serializer = SkillSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, pk, format=None):
        try:
            instance = Skill.objects.get(pk=pk)
        except Skill.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        profile = TeacherProfile.objects.get(user=request.user)
        if instance.trainer != profile:
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        serializer = SkillSerializers(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
            instance = Skill.objects.get(pk=pk)
            if instance.trainer == profile:
                instance.delete()
                return Response( status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        except Skill.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)

class AchievementViewSet(ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializers

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
            achievements = profile.achievements.all()
            serializer = AchievementSerializers(achievements, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)
        request.data['trainer_profile'] = profile.id
        serializer = AchievementSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk, format=None):
        try:
            instance = Achievement.objects.get(pk=pk)
        except Achievement.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        profile = TeacherProfile.objects.get(user=request.user)
        if instance.trainer != profile:
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        serializer = AchievementSerializers(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user = request.user
        try:
            profile = TeacherProfile.objects.get(user=user)
            instance = Achievement.objects.get(pk=pk)
            if instance.trainer == profile:
                instance.delete()
                return Response( status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "You are not the owner"}, status=status.HTTP_403_FORBIDDEN)
        except Achievement.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)

class VedioSectionViewSet(ModelViewSet):
    queryset = VedioSection.objects.all()
    serializer_class = VedioSectionSerializer
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes=[VedioSectionPolicy]
    def get_queryset(self):
       queryset = super().get_queryset()
       return queryset

    def create(self, request, *args, **kwargs):
        course_id=request.data['course']
        course = get_object_or_404(Course, pk=course_id)
        if course.trainer != request.user:
            return Response({"error":"you don't have right to add anything to this course becuase you are not the owner !!"},status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     data = request.data.copy()
    #     data.pop('translations', None)
    #     if request.data['translations']:
    #         instance.translations.set(request.data['translations']) 
    #     instance.vedio_url = data.get('vedio_url', instance.vedio_url)
    #     instance.video_file = data.get('video_file', instance.video_file)
    #     instance.sort = data.get('sort', instance.sort)
    #     instance.course_id = data.get('course', instance.course_id)
    #     # Save the instance
    #     instance.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LiveSessionMainDataSectionViewSet(ModelViewSet):
    queryset = LiveSessionMainDataSection.objects.all()
    serializer_class = LiveSessionMainDataSectionSerializer
    pagination_class = CustomPagination
    permission_classes=[LiveSessionMainDataPolicy]
    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course=course_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except LiveSessionMainDataSection.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        ser = UpdateLiveSessionMainDataSectionSerializer(instance, data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data,status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=False, methods=['get'])
    # def live_session_sections_info(self, request):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK) 

class CycleViewSet(ModelViewSet):
    queryset = Cycle.objects.all()
    serializer_class = CycleSerializer
    pagination_class = CustomPagination
    permission_classes=[CyclePolicy]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course=course_id)
        return queryset

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True)
        response_data = {'total_count': queryset.count(), 'results': serializer.data}
        return Response({"data": response_data}, status=status.HTTP_200_OK)
        
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            lives_data = request.data.pop('lives_data', [])
            lsCount=len(lives_data)
            request.data['lsCount']=lsCount
            res=LiveSessionMainDataSection.objects.filter(course=request.data['course']).count()
            if lsCount != res:
                raise ValueError("You must enter all live sessions details")
            serializer = CycleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            cycle=serializer.save()
            for live_data in lives_data:
                live_data['cycle'] = cycle.id
                StartTime=live_data['StartTime']
                EndTime=live_data['EndTime']
                liveSessionMainDataID=live_data['liveSessionMainDataID']
                price=live_data['price']
                mainData=LiveSessionMainDataSection.objects.get(pk=liveSessionMainDataID)
                topic=mainData.title
                agenda=mainData.description
                data={
                    "topic":topic,
                    "agenda":agenda,
                    "StartTime":StartTime,
                    "EndTime":EndTime,
                    'price':price
                }
                live_data['ZoomMeetingURL']="http://zoom.com"
                live_data_serializer = LiveSessionDetailsSerializer(data=live_data)
                live_data_serializer.is_valid(raise_exception=True)
                ldata=live_data_serializer.save()
                user=request.user.id
                strategy_type = request.data.get('strategy')
                if strategy_type == 'zoom':
                    strategy = ZoomMeeting()
                else:
                    raise ValueError('Invalid strategy')
                lsDetails_id=ldata.id
                service = MeetingServices(strategy)

                service.addMeeting(user,data,lsDetails_id)
                # aysnc
                # task_chain = chain(create_zoom.si(data,ldata.id,user) | send_notification_task.s())
                # result = task_chain.delay()
                
                
                print("ddddddddddddddddddddddddddd")
                # live_data['ZoomMeetingURL']=zoom['url']
                # live_data['zoomData']=zoom['data']
                # live_data_serializer = LiveSessionDetailsSerializer(data=live_data)
                # live_data_serializer.is_valid(raise_exception=True)
                # live_data_serializer.save()
            ser=CycleSerializer(instance=cycle)
            headers = self.get_success_headers(ser.data)
            return Response(ser.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            transaction.set_rollback(True)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


    def update(self, request,pk, format=None):
            try:
                instance = Cycle.objects.get(pk=pk)
            except Cycle.DoesNotExist:
                return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
            ser = CycleSerializer(instance, data=request.data,partial=True)
            if ser.is_valid():
                ser.save()
                return Response(ser.data,status=status.HTTP_200_OK)
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)

            
    def destroy(self, request,pk):
        try:
            instance = Cycle.objects.get(pk=pk)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cycle.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)


class LiveSessionDetailsViewSet(ModelViewSet):
    queryset = LiveSessionDetails.objects.all()
    serializer_class = LiveSessionDetailsSerializer
    pagination_class = CustomPagination
    permission_classes=[LiveSessionDetailsPolicy]
    def create(self, request, *args, **kwargs):
        serializer = LiveSessionDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            instance = LiveSessionDetails.objects.get(pk=pk)
        except LiveSessionDetails.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LiveSessionDetailsSerializer(instance, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            instance = LiveSessionDetails.objects.get(pk=pk)
            instance.delete()
            return Response( status=status.HTTP_204_NO_CONTENT)
        except LiveSessionDetails.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        
        

