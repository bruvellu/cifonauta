from django.shortcuts import render, redirect
from .forms import UserCifonautaCreationForm, LoginForm, PasswordResetForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from meta.models import Person

def user_creation(request):
    if request.method == 'POST':
        form = UserCifonautaCreationForm(request.POST)
        if form.is_valid():
            user_instance = form.save(commit=False)

            user_instance.first_name = form.cleaned_data['first_name'].capitalize()
            user_instance.last_name = form.cleaned_data['last_name'].capitalize()
            
            name = user_instance.first_name + ' ' + user_instance.last_name
            email = form.cleaned_data['email']
            orcid = form.cleaned_data['orcid']
            idlattes = form.cleaned_data['idlattes']

            Person.objects.create(name=name, email=email, orcid=orcid, idlattes=idlattes)

            user_instance.save()

            messages.success(request, 'Usuário criado com sucesso')
            return redirect('Login')
        else:
            messages.error(request, 'Dados inválidos')
            
    else:
        form = UserCifonautaCreationForm()

    errors = {}
    for field in form:
        if field.errors:
            errors[field.name] = field.errors[0]

    return render(request, 'users/user_creation.html', {'form': form, 'errors': errors})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso')
                return redirect('home')
        else:
            if not form['captcha'].errors:
                messages.error(request, 'Usuário ou senha incorretos')  
            else:
                messages.error(request, 'Captcha incorreto')  
        
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Você se desconectou')
    return redirect('Login')

class PasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = '/user/login'

class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = '/user/login'
    template_name = 'users/password_reset_confirm.html'