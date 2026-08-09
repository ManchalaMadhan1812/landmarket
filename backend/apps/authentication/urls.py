"""
Authentication URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    UserProfileViewSet,
    CurrentUserView,
    ForgotPasswordView,
)

router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')
router.register(r'login', LoginView, basename='login')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'user', CurrentUserView, basename='user')
router.register(r'forgot-password', ForgotPasswordView, basename='forgot-password')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]