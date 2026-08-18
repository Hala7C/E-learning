from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Define a router for the DashbordViewset
router = DefaultRouter()
router.register(r'dashbord', DashbordViewset)

urlpatterns = [

    path('default_user_statistic/', DashbordViewset.as_view({'get': 'default_user_statistic'}), name='default-user-statistic'),
    path('type_user_statistic/', DashbordViewset.as_view({'get': 'type_user_statistic'}), name='type-user-statistic'),
    path('default_date_join_user_statistic/', DashbordViewset.as_view({'get': 'default_date_join_user_statistic'}), name='default-date-join-user-statistic'),
    path('users_joined_last_month/', DashbordViewset.as_view({'get': 'users_joined_last_month'}), name='users-joined-last-month'),
    path('users_joined_last_three_month/', DashbordViewset.as_view({'get': 'users_joined_last_three_month'}), name='users-joined-last-three-month'),
    path('users_joined_last_year/', DashbordViewset.as_view({'get': 'users_joined_last_year'}), name='users-joined-last-year'),
    path('block_user/<int:pk>/', DashbordViewset.as_view({'get': 'block_user'}), name='block-user'),
    path('unblock_user/<int:pk>/', DashbordViewset.as_view({'get': 'unblock_user'}), name='unblock-user'),
    path('list_active_user/', DashbordViewset.as_view({'get': 'list_active_user'}), name='get-active-user'),
    path('list_blocked_user/', DashbordViewset.as_view({'get': 'list_blocked_user'}), name='get-blocked-user'),
    path('list_trainers/', DashbordViewset.as_view({'get': 'list_trainers'}), name='list_trainers'),
    path('list_students/', DashbordViewset.as_view({'get': 'list_students'}), name='list_students'),
    path('student_information/<int:pk>/', DashbordViewset.as_view({'get': 'student_information'}), name='get-student'),
    path('trainer_information/<int:pk>/', DashbordViewset.as_view({'get': 'trainer_information'}), name='get-trainer'),
    path('block_course/<int:pk>/', DashbordViewset.as_view({'get': 'block_course'}), name='get-block_course'),
    path('unblock_course/<int:pk>/', DashbordViewset.as_view({'get': 'unblock_course'}), name='get-unblock_course'),
    path('finicial_data/', DashbordViewset.as_view({'get': 'finicial_data'}), name='finicial_data'),
    path('courses/count/', DashbordViewset.as_view({'get': 'list_courses'}), name='list_courses'),
    path('cycles/count/', DashbordViewset.as_view({'get': 'list_cycles'}), name='list_cycles'),
    path('course_per_category/', DashbordViewset.as_view({'get': 'course_per_category'}), name='course_per_category'),
    path('course/disable/<int:pk>/', DashbordViewset.as_view({'put': 'disable_course'}), name='disable_course'),
    path('course/enable/<int:pk>/', DashbordViewset.as_view({'put': 'enable_course'}), name='enable_course'),


    # Include router URLs
    path('', include(router.urls)),
]