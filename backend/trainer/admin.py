from django.contrib import admin
from .models import *
from parler.admin import TranslatableAdmin

class CategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'created_on')
    fieldsets = (
        (None, {
            'fields': ['name'],
        }),
    )

admin.site.register(Category, CategoryAdmin)

class CourseAdmin(TranslatableAdmin):
    list_display = ('title', 'content', 'category', 'status', 'trainer')
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category', 'status', 'trainer'),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.trainer = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Course, CourseAdmin)


admin.site.register(Education)
admin.site.register(Employment)
admin.site.register(Skill)
admin.site.register(Achievement)

class VedioSectionAdmin(TranslatableAdmin):
    list_display =('title','description','vedio_url','video_file','sort','course')
    fieldsets = (
        (None ,
        {
            'fields':('title','description','vedio_url','video_file','sort','course'),
        }),
    )
    def save_model(self , request,obj,form,change):
        obj.author_id =request.user.id
        super().save_model(request,obj,form,change)
admin.site.register(VedioSection, VedioSectionAdmin)

class LiveSessionMainDataSectionAdmin(TranslatableAdmin):
    list_display =('title','description','sort','course')
    fieldsets = (
        (None ,
        {
            'fields':('title','description','sort','course'),
        }),
    )
    def save_model(self , request,obj,form,change):
        obj.author_id =request.user.id
        super().save_model(request,obj,form,change)
        
admin.site.register(LiveSessionMainDataSection, LiveSessionMainDataSectionAdmin)
admin.site.register(Cycle)
admin.site.register(LiveSessionDetails)
