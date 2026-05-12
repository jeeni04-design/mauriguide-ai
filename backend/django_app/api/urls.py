from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('auth/verify/', views.verify_token, name='verify_token'),
    path('auth/login/', views.login_api, name='login'),
    path('auth/logout/', views.logout_api, name='logout'),
    path('auth/register/', views.register_api, name='register'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('health/', views.api_health, name='health'),
    path('places/', views.get_all_places, name='places'),   # ← new
]
