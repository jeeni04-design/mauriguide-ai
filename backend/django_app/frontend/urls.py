from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/tourist/', views.tourist_register, name='tourist_register'),
    path('register/local/', views.local_register, name='local_register'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plan/', views.plan_trip, name='plan_trip'),
]
