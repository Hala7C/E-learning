from rest_framework import serializers
from mainAuth.models import StudentProfile,TeacherProfile,CustomUser
from .models import Course
from django.contrib.auth import get_user_model
from rest_framework import serializers
import sys
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from parler_rest.serializers import TranslatableModelSerializer
from newapp.mixins import TranslatedSerializerMixin
from parler_rest.fields import TranslatedFieldsField
from rest_framework import routers, serializers, viewsets
from django.utils.translation import activate
from .models import *
from datetime import datetime,date
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Avg
from rating.models import Rating
from django.db.models import Q
from parler_rest.fields import TranslatedField
from django.utils.translation import get_language
from payments.models import CourseSubscription

class StudentProfileSerializers(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    age=serializers.IntegerField(read_only=True)
    class Meta:
            model = StudentProfile
            fields=['id','name','gender','birthday','age','bio','profile_picture','user','location']
            



class AddTrainerProfileSerializers(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    age=serializers.IntegerField(read_only=True)

    class Meta:
            model = TeacherProfile
            fields=['id','name','gender','birthday','age','bio','profile_picture','status','user']
            
            
class SubmitTrainerProfileSerializers(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    age=serializers.IntegerField(read_only=True)

    class Meta:
            model = TeacherProfile
            fields=['id','name','gender','birthday','age','bio','profile_picture','status','user']
    def validate(self,attrs):
        user=attrs.get('user')
        profile= user.teacherprofile
        education=profile.education.count()
        skills=profile.skills.count()
        employments=profile.employments.count()
        if  education ==0 :
            raise serializers.ValidationError("education section is required")
        if  skills ==0 :
            raise serializers.ValidationError("skills section is required")
        if  employments ==0 :
            raise serializers.ValidationError("Employment section is required")
        return super().validate(attrs)
    
class ApproveProfileSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
            model = TeacherProfile
            fields=['status']
            
            
class EducationSerializers(serializers.HyperlinkedModelSerializer):
    trainer_profile = serializers.PrimaryKeyRelatedField(queryset=TrainerProfile.objects.all(),source='trainer')
    class Meta:
            model = Education
            fields=['id','institution','degree','year','trainer_profile']


class EmploymentSerializers(serializers.HyperlinkedModelSerializer):
    trainer_profile = serializers.PrimaryKeyRelatedField(queryset=TrainerProfile.objects.all(),source='trainer')
    class Meta:
            model = Employment
            fields=['id','company','position','start_date','end_date','trainer_profile']


class SkillSerializers(serializers.HyperlinkedModelSerializer):
    trainer_profile = serializers.PrimaryKeyRelatedField(queryset=TrainerProfile.objects.all(),source='trainer')
    class Meta:
            model = Skill
            fields=['id','name','description','proficiency_level','trainer_profile']


class AchievementSerializers(serializers.HyperlinkedModelSerializer):
    trainer_profile = serializers.PrimaryKeyRelatedField(queryset=TrainerProfile.objects.all(),source='trainer')
    class Meta:
            model = Achievement
            fields=['id','title','description','date_achieved','trainer_profile']


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username','email']
        
class CategorySerializer(TranslatableModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','created_on']
        
class AddCategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)
    class Meta:
        model = Category
        fields = ['id','translations','created_on']
        
class TrainerProfileSerializers(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    education = EducationSerializers(many=True, read_only=True)
    employments = EmploymentSerializers(many=True, read_only=True)
    skills = SkillSerializers(many=True, read_only=True)
    achievements = AchievementSerializers(many=True, read_only=True)
    age=serializers.IntegerField(read_only=True)
    class Meta:
            model = TeacherProfile
            fields=['id','name','gender','birthday','age','bio','profile_picture','achievements','education','employments','skills','status','user']


class VedioSectionSerializer(TranslatableModelSerializer):
    # translations = TranslatedFieldsField(shared_model=VedioSection)
    course=serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    class Meta:
        model = VedioSection
        fields = ['id','title','description','vedio_url','video_file','sort','course']
    
    def get_video_url(self, obj):
        return str(obj.vedio_url)
    def create(self, validated_data):
        translations_data = {
            get_language(): {'title': validated_data.pop('title')}
        }
        instance = super().create(validated_data)
        self.update_translations(instance, translations_data)
        return instance
    def update(self, instance, validated_data):
        translations_data = {
            get_language(): {'title': validated_data.pop('title')}
        }
        instance = super().update(instance, validated_data)
        self.update_translations(instance, translations_data)
        return instance

    def update_translations(self, instance, translations_data):
        for lang_code, translation_data in translations_data.items():
            instance.set_current_language(lang_code)
            for field_name, field_value in translation_data.items():
                setattr(instance, field_name, field_value)
        instance.save_translations()

class LiveSessionMainDataSectionSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=LiveSessionMainDataSection)
    course=serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = LiveSessionMainDataSection
        fields = ['id','translations','sort','course']
        
class UpdateLiveSessionMainDataSectionSerializer(TranslatableModelSerializer):
    # translations = TranslatedFieldsField(shared_model=LiveSessionMainDataSection)
    course=serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    class Meta:
        model = LiveSessionMainDataSection
        fields = ['id','title','description','sort','course']
        
    def update(self, instance, validated_data):
        translations_data = {
            get_language(): {'title': validated_data.pop('title')}
        }
        instance = super().update(instance, validated_data)
        self.update_translations(instance, translations_data)
        return instance

    def update_translations(self, instance, translations_data):
        for lang_code, translation_data in translations_data.items():
            instance.set_current_language(lang_code)
            for field_name, field_value in translation_data.items():
                setattr(instance, field_name, field_value)
        instance.save_translations()
    

class LiveSessionDetailsSerializer(serializers.ModelSerializer):
    cycle=serializers.PrimaryKeyRelatedField(queryset=Cycle.objects.all())
    liveSessionMainDataID=serializers.PrimaryKeyRelatedField(queryset=LiveSessionMainDataSection.objects.all())
    class Meta:
        model = LiveSessionDetails
        fields = ['id','cycle','liveSessionMainDataID','ZoomMeetingURL','zoomData','StartTime','EndTime','price']       
    def to_representation(self,instance):
        representation=super().to_representation(instance)
        content_type = ContentType.objects.get_for_model(LiveSessionDetails)
        average_rate = Rating.objects.filter(content_type=content_type, object_id=instance.id).aggregate(Avg('rate_value'))['rate_value__avg']
        representation['average_rate']=average_rate
        return representation    


class CycleSerializer(serializers.ModelSerializer):
    course=serializers.PrimaryKeyRelatedField(queryset= Course.objects.all())
    livesessiondetails=LiveSessionDetailsSerializer(many=True,required=False,read_only=True)

    class Meta:
        model = Cycle
        fields = ['id','course','NumberCycle','StartDate','EndDate','livesessiondetails']

    def validate(self,data):
            return super().validate(data)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        cycle = Cycle.objects.get(id=instance.id)
        num_subscribers = CourseSubscription.objects.filter(cycle=cycle).count()
        representation['num_subscribers']=num_subscribers      
        return representation

class CourseSerializer(TranslatableModelSerializer):
    trainer =  serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    category =  serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    livesessionmaindatasections=LiveSessionMainDataSectionSerializer(many=True ,read_only=True)
    vediosections=VedioSectionSerializer(many=True, read_only=True)
    cycles=CycleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id','title','content','created_on','category','status','trainer','vediosections','livesessionmaindatasections','cycles']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        current_date = date.today()
        content_type = ContentType.objects.get_for_model(Course)
        average_rate = Rating.objects.filter(content_type=content_type, object_id=instance.id).aggregate(Avg('rate_value'))['rate_value__avg']
        representation['average_rate']=average_rate 
        course = Course.objects.get(id=instance.id)
        num_subscribers = CourseSubscription.objects.filter(course=course).count()
        representation['num_subscribers']=num_subscribers      
        # Filter cycles based on specific time range
        cycles = representation['cycles']
        # filtered_cycles = [cycle for cycle in cycles if datetime.strptime(cycle['StartDate'], "%Y-%m-%d ") >= current_date <= datetime.strptime(cycle['EndDate'], "%Y-%m-%d ")]
        filtered_cycles = [cycle for cycle in cycles if datetime.strptime(cycle['StartDate'], '%Y-%m-%d').date() <= current_date <= datetime.strptime(cycle['EndDate'], '%Y-%m-%d').date()]
        representation['cycles'] = filtered_cycles
        return representation
        
class AddCourseSerializer(TranslatableModelSerializer):
    # translations = TranslatedFieldsField(shared_model=Course)
    trainer =  serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    category =  serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    lives=LiveSessionMainDataSectionSerializer(many=True,required=False)
    videos=VedioSectionSerializer(many=True,required=False)
    title = serializers.CharField()
    content= serializers.CharField(required=False)
    class Meta:
        model = Course
        fields = ['id','title','content','category','status','trainer','videos','lives']
    def create(self, validated_data):
        translations_data = {
            get_language(): {'title': validated_data.pop('title')}
        }
        instance = super().create(validated_data)
        self.update_translations(instance, translations_data)
        return instance
    def update(self, instance, validated_data):
        translations_data = {
            get_language(): {'title': validated_data.pop('title')}
        }
        instance = super().update(instance, validated_data)
        self.update_translations(instance, translations_data)
        return instance

    def update_translations(self, instance, translations_data):
        for lang_code, translation_data in translations_data.items():
            instance.set_current_language(lang_code)
            for field_name, field_value in translation_data.items():
                setattr(instance, field_name, field_value)
        instance.save_translations()