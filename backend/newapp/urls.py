from django.urls import path, include
from rest_framework import routers
from . import views

# Create a router for the API views
router = routers.DefaultRouter()
router.register(r'policies', views.PolicyViewSet)
router.register(r'actions', views.ActionViewSet)
router.register(r'conditions', views.ConditionViewSet)
router.register(r'statments', views.StatmentViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', views.index1, name='index1'),
    path('actions/<int:pk>/conditions/', views.ActionViewSet.as_view({'get': 'get_action_conditions'})),
    path('policies/give_obj_perm/', views.PolicyViewSet.as_view({'post': 'give_obj_perm'})),
    path('api/', include((router.urls))),
    # path('api/addPolicy/',views.CoursePolicyView.as_view()),
]
