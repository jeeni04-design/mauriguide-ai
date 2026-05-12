from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.get_all_datasets, name='all_datasets'),
    path('water/', views.get_water_activities, name='water_activities'),
    path('land/', views.get_land_activities, name='land_activities'),
    path('hikes/', views.get_hikes, name='hikes'),
    path('food/', views.get_food_outlets, name='food_outlets'),
    path('beaches/', views.get_beaches, name='beaches'),
    path('sites/', views.get_sites, name='sites'),
    path('search/', views.search_locations, name='search'),
]
