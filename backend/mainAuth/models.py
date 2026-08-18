from django.db import models

from django.contrib.auth.models import AbstractUser,PermissionsMixin,BaseUserManager

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from datetime import date

# Create your models here.
class CustomUserManager(BaseUserManager):
    def email_validator(self,email):
        try :
            validate_email(email)
        except ValidationError:
            raise ValueError(_("please enter a valid email address"))
        
        
    def create_user(self,email,first_name=None,last_name=None,password=None,**extra_fields):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("an email address is required"))
        
        if first_name is None:
            extra_fields.setdefault("provider",'google')
            user=self.model(email=email,**extra_fields)
            
        else:
            extra_fields.setdefault("provider",'email')
            user=self.model(email=email,first_name=first_name,last_name=last_name,**extra_fields)
        user.set_password(password)
    
        user.save(using=self._db)
        
        return user 
    
    def create_superuser(self,email,first_name,last_name,password,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        if extra_fields.get("is_staff") is not True :
            raise ValueError(_("is staff must be true for admin user"))
        
        if extra_fields.get("is_superuser") is not True :
            raise ValueError(_("is superuser must be true for admin user"))
        
        user=self.create_user(
            email,first_name,last_name,password,**extra_fields
        )
        user.save(using=self._db)
        
        return user
    
    
class Role(models.Model):
    # Role_CHOICES=[('admin','Admin'),('user','User'),('trainer','Trainer')]
    name=models.CharField(max_length=100,unique=True)
    def normlize_name(self,name):
        return name.lower().capitalize()
    def save(self,*args, **kwargs):
        self.name= self.normlize_name(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
            return self.name
        

    
    
    
class CustomUser(AbstractUser,PermissionsMixin):
    PROVIDER_CHOICES=[('google','Google'),('email','Email')]
    # is neccessary?
    provider=models.CharField(max_length=100,choices=PROVIDER_CHOICES,default='email')
    email=models.CharField(max_length=100,unique=True)
    otp_base32 =  models.CharField(max_length = 200, null = True)
    logged_in =   models.BooleanField(default = False)
    objects = CustomUserManager()
    
    username_validator = None
    username = None
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name','last_name']
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    


class BaseProfile(models.Model):
    GENDER_CHOICES=[(None,'None'),('male','Male'),('female','Female')]
    # user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender=models.CharField(max_length=100,choices=GENDER_CHOICES,null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='photos/', blank=True)
    def __str__(self):
        return f"{self.user.get_full_name}'s Profile"
    class Meta:
        abstract = True
    def age(self):
        today = date.today()
        if not self.birthday:
            age = None
            return age
        age = today.year - self.birthday.year
        if today.month < self.birthday.month or (today.month == self.birthday.month and today.day < self.birthday.day):
            age -= 1
        return age
    @property
    def owner(self):
        return self.user
class TeacherProfile(BaseProfile):
    STATUS_CHOICES=[('draft','Draft'),('pending','Pending'),('accepted','Accepted'),('declined','Declined')]
    status=models.CharField(max_length=100,choices=STATUS_CHOICES,default='draft')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    
    
class StudentProfile(BaseProfile):
    location=models.CharField(max_length=100,null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    
    
    
    
    
    
    
    
    
