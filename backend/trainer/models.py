from django.db import models
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields
from django.utils import timezone
from mainAuth.models import CustomUser,TeacherProfile as TrainerProfile
from django.contrib.contenttypes.fields import GenericRelation
from rating.models import Rating

class Category(TranslatableModel):
    translations = TranslatedFields(
    name=models.CharField(_("name"),max_length=100,null=False),
    )
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
            ordering = ['-created_on']
            verbose_name = _("category")
            verbose_name_plural = _("categorys")

    def __str__(self):
        return self.name
    
    
class Course(TranslatableModel):
    course_status = [
            (_('unpublish'),_('unpublish')),
            (_('published'),_('published')),]
    translations = TranslatedFields(
        title = models.CharField(_("Title"), max_length=200, unique=True ,null=False),
        content =models.TextField(_("content"),blank=True, unique=False),
        
    )
    status = models.CharField(max_length=100 , choices = course_status ,default='unpublish')
    trainer = models.ForeignKey(CustomUser , on_delete=models.CASCADE,related_name='courses')
    category = models.ForeignKey(Category ,on_delete=models.CASCADE,related_name='courses',null=True)  
    created_on = models.DateTimeField(auto_now_add= True)
    ratings = GenericRelation(Rating,related_query_name='course_rating')
    is_blocked = models.BooleanField(default=False, verbose_name=_('Blocked'))
    class Meta:
        ordering = ['-created_on']
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title
    @property
    def owner(self):
        return self.trainer

class Education(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE,related_name='education')
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    year = models.IntegerField()

class Employment(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE,related_name='employments')
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    
class Skill(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE,related_name='skills')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    proficiency_level = models.IntegerField(choices=((1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')))
    
class Achievement(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE,related_name='achievements')
    title = models.CharField(max_length=100,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_achieved = models.DateField(blank=True, null=True)


class VedioSection(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Title"), max_length=200, unique=True ,null=False),
        description =models.TextField(_("description"), max_length=200),
    )
    vedio_url = models.URLField(null = True,blank=True)
    video_file =models.FileField(_("Video File"), upload_to='video/%y', null=True, blank=True)
    sort= models.IntegerField()
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True,blank=True,related_name='vediosections')

    def __str__(self):
        return self.title 
    @property
    def owner(self):
        return self.course.trainer
class LiveSessionMainDataSection(TranslatableModel):
    translations = TranslatedFields (
        title = models.CharField(_("Title"), max_length=200, unique=True ,null=False),
        description =models.TextField(_("description"), max_length=200),
    ) 
    sort = models.IntegerField()
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True,blank=True,related_name='livesessionmaindatasections')

    def __str__(self):
        return self.title   
    @property
    def owner(self):
        return self.course.trainer

class Cycle(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='cycles')
    NumberCycle = models.IntegerField()
    StartDate =models.DateField()
    EndDate = models.DateField()
    @property
    def owner(self):
        return self.course.trainer
class LiveSessionDetails(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE,related_name='livesessiondetails')
    liveSessionMainDataID = models.ForeignKey(LiveSessionMainDataSection , on_delete=models.CASCADE ) 
    ZoomMeetingURL = models.URLField(max_length=500)
    zoomData=models.JSONField(blank=True,null=True)
    StartTime = models.DateTimeField()
    EndTime = models.DateTimeField()
    price=models.DecimalField(max_digits=5, decimal_places=2,null=True)
    def __str__(self):
        return f"Live session ID: {self.id}" 
    @property
    def owner(self):
        return self.cycle.owner



