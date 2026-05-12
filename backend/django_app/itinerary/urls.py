from django.urls import path
from . import views

urlpatterns = [
    # Itinerary CRUD
    path('', views.itinerary_list, name='itinerary_list'),
    path('<int:pk>/', views.itinerary_detail, name='itinerary_detail'),

    # Stop management
    path('<int:pk>/add-stop/', views.add_stop, name='add_stop'),
    path('<int:pk>/remove-stop/<int:stop_id>/', views.remove_stop, name='remove_stop'),
    path('<int:pk>/stops/<int:stop_id>/update/', views.update_stop, name='update_stop'),

    # Reorder stops
    path('<int:pk>/reorder/', views.reorder_stops, name='reorder_stops'),

    # Recommendations
    path('recommendations/', views.get_recommendations, name='recommendations'),
]
