from django.urls import path,include
from . import views

urlpatterns = [
    path('create/', views.user_creation, name='Create User'),
    path('record/', views.user_creation, name='Create User'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
    path('captcha/', include('captcha.urls')),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset_custom'),
    path('reset/confirm/<str:uidb64>/<str:token>/',views.PasswordResetConfirmView.as_view(), name='password_reset_confirm_custom'),
    path('forgot_username/', views.ForgotUsernameView.as_view(), name='forgot_username')
]
