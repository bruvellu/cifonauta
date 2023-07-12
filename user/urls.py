from django.urls import path
from . import views

urlpatterns = [
    path('record/', views.user_creation, name='Create User'),
    path('login/', views.login_view, name='Login')
]
