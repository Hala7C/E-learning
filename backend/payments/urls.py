from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Define a router for the viewsets
router = DefaultRouter()
router.register(r'subscribe', CourseSubscrubtionViewSet)
router.register(r'transaction', TransactionViewSet)
# router.register(r'enrollment', EnrollmentViewSet)
router.register(r'account', AccountDetailViewSet)
router.register(r'payouts', PayoutViewSet)



urlpatterns = [
    # Home page
    path('', HomePageView.as_view(), name='home'),
    
    # Router URLs
    path('r/', include(router.urls)),
    
    # Stripe related URLs
    path('config/', stripe_config),
    path('create-checkout-session/', CreateCheckoutApiView.as_view()),
    path('success/', SuccessView.as_view()),
    path('cancelled/', CancelledView.as_view()),
    path('webhook/', stripe_webhook),
    # path('bank/', PayoutView.as_view({'post': 'create_bank_account_token'}), name='payout'),
    path('update_status/<int:pk>/',PayoutViewSet.as_view({'patch':'update_status'}),name='update_status'),
    path('create_stripe_payout/',PayoutViewSet.as_view({'post':'create_stripe_payout'}),name='create_stripe_payout'),

    
    # Account related URLs
    path('account/total/transactions/', AccountDetailViewSet.as_view({'get': 'get_total_trainer_transactions'})),
    path('account/transactions/', AccountDetailViewSet.as_view({'get': 'get_trainer_transactions'})),
    path('account/get_revenue/', AccountDetailViewSet.as_view({'get': 'get_revenue'})),
    path('account/get_balance/', AccountDetailViewSet.as_view({'get': 'get_balance'})),
    path('authorize/', StripeAuthorizeView.as_view(), name='authorizeStripe'),
    path('oauth/callback/', StripeAuthorizeCallbackView.as_view(), name='authorize_callback'),
]
