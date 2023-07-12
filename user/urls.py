from django.urls import path,include
from . import views

urlpatterns = [
    path('create/', views.user_creation, name='Create User'),
    path('record/', views.user_creation, name='Create User'),
    path('login/', views.login_view, name='Login'),
        path('captcha/', include('captcha.urls'))
]
