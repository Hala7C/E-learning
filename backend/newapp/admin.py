from django.contrib import admin
from .models import *
from parler.admin import TranslatableAdmin

# Register your models here.
admin.site.register(Statment)
admin.site.register(Action)
admin.site.register(Policy)
admin.site.register(Notification)
admin.site.register(Conditions)
admin.site.register(ObjectPerm)