"""
Properties URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, WishlistViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'', PropertyViewSet, basename='property')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]