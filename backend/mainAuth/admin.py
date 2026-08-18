from django.contrib import admin

# Register your models here.
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Role)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)