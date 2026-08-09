from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPlanViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='plans')
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
]
