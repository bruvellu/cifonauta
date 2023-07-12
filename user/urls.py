from django.urls import path,include
from . import views

urlpatterns = [
    path('create/', views.user_creation, name='Create User'),
    path('captcha/', include('captcha.urls')),
]
