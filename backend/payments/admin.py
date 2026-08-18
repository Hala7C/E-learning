from django.contrib import admin
from .models import *

admin.site.register(CourseSubscription)
admin.site.register(Transaction)
admin.site.register(LiveSessionEnrollment)
admin.site.register(Config)
admin.site.register(AcconutDetail)
admin.site.register(Payout)