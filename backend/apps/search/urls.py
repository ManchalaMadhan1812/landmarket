"""
Search URLs
"""

from django.urls import path
from . import views

urlpatterns = [
    path('properties/', views.search_properties, name='search_properties'),
    path('nearby/', views.search_nearby_properties, name='search_nearby'),
    path('autocomplete/', views.location_autocomplete, name='location_autocomplete'),
    path('survey/', views.search_by_survey_number, name='survey_search'),
]