from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Define a router for the DashbordViewset
router = DefaultRouter()
urlpatterns = [

    
    path('groups/', GroupAPIView.as_view(), name='group-crud'),
    path('permissions/', PermissionListAPIView.as_view(), name='permission-list'),
    path('groups/permissions/', GroupPermissionAPIView.as_view(), name='group-permissions'),
    path('users/groups/', UserGroupAPIView.as_view(), name='user-groups'),

    # Two-factor authentication views
    path('set-two-factor-auth/', Set2FAView.as_view(), name='set-2fa'),
    path('verify-two-factor-auth/', Verify2FAView.as_view(), name='verify-2fa'),
    # Include router URLs
    path('', include(router.urls)),
]
