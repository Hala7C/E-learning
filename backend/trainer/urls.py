from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Define router for ViewSets
router = DefaultRouter()
router.register(r'draftProfile', DraftTrainerProfile, basename='draftProfile')
router.register(r'PendingTrainerProfile', PendingTrainerProfile, basename='PendingTrainerProfile')
router.register(r'course',CourseViewSet)
router.register(r'category',CategoryViewSet)
router.register(r'education',EducationViewSet)
router.register(r'employment',EmploymentViewSet)
router.register(r'skill',SkillViewSet)
router.register(r'achievement',AchievementViewSet)
router.register(r'video',VedioSectionViewSet)
router.register(r'live_session',LiveSessionMainDataSectionViewSet)
router.register(r'cycle',CycleViewSet)
router.register(r'details',LiveSessionDetailsViewSet)
router.register(r'studentProfile',StudentProfileViewSet)


admin_router = DefaultRouter()
admin_router.register(r'courses', CourseViewSet, basename='admin-courses')
urlpatterns = [


    # URLs related to specific resources
    path('course/<int:pk>/delete_translation/<str:language_code>/', CourseViewSet.as_view({'delete': 'delete_translation'}), name='delete_translation'),
    path('course/<int:pk>/give_obj_perm/', CourseViewSet.as_view({'post': 'give_obj_perm'}), name='give_obj_perm'),
    path('category/<int:pk>/delete_translation/<str:language_code>/', CategoryViewSet.as_view({'delete': 'delete_translation'}), name='delete_translation'),
    path('course/getTrainerCourse/', CourseViewSet.as_view({'get': 'getTrainerCourse'}), name='getTrainerCourse'),
    path('live_session/pk/getLiveSectionInfo/', LiveSessionMainDataSectionViewSet.as_view({'get': 'getLiveSectionInfo'}), name='getTrainerCourse'),
    path('submitDraftProfile/<int:pk>/', SubmitDraftProfile.as_view({'put': 'update'})),
    path('',include(router.urls)),



]