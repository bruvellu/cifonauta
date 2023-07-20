from django.shortcuts import render, redirect
from .forms import UserCifonautaCreationForm, LoginForm, PasswordResetForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
# Create your views here.

def user_creation(request):
    if request.method == 'POST':
        form = UserCifonautaCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your user is created, please log in.')
            return redirect('Login')
    else:
        form = UserCifonautaCreationForm()
    return render(request, 'users/user_creation.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

class PasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = '/user/login'

class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = '/user/login'
    template_name = 'users/password_reset_confirm.html'