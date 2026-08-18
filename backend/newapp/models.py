from django.db import models
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from mainAuth.models import CustomUser

class Statment(models.Model):
    # Class_CHOICES=[('course','Course')]
    view_name=models.CharField(max_length=100,unique=True)

    class Meta:
        verbose_name_plural = "Statments"

    def __str__(self):
        return self.view_name

class Action(models.Model):
    name=models.CharField(max_length=100)
    statment=models.ForeignKey('Statment', on_delete=models.CASCADE,related_name='actions')
    def __str__(self):
        return f'{self.name}_{self.statment}'

class Conditions(models.Model):
    name=models.CharField(max_length=250)
    actions=models.ManyToManyField(Action)


    class Meta:
        verbose_name_plural = "Conditions"

    def __str__(self):
        return self.name
    
class Policy(models.Model):
    EFFECT_CHOICES=[('allow','allow'),("deny","deny")]
    action = models.CharField(max_length=255)
    principal = models.CharField(max_length=255)
    effect = models.CharField(max_length=255,choices=EFFECT_CHOICES,default='deny')
    conditions = models.TextField(null=True, blank=True)
    statmant=models.ForeignKey(Statment,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Policies"

    def __str__(self):
        return self.action
    


class ObjectPerm(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    users=models.ManyToManyField(CustomUser)


class Notification(models.Model):
    message = models.CharField(max_length=100)
    group_name=models.CharField(max_length=50,default='all')
    is_read=models.BooleanField(default=False)
    def __str__(self):
        return self.message