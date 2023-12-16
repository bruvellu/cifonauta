from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('create/', views.user_creation, name='Create User'),
    path('record/', views.user_creation, name='Create User'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('captcha/', include('captcha.urls')),
    path('reset_password/', views.PasswordResetView.as_view(), name='custom_reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/',views.PasswordResetConfirmView.as_view(), name='custom_password_reset_confirm'),
    path('reset_password_complete/', views.PasswordResetCompleteView.as_view(), name='custom_password_reset_complete'),
    path('forgot_username/', views.ForgotUsernameView.as_view(), name='forgot_username')
]