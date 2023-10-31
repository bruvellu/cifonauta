from django.shortcuts import render, redirect
from .forms import UserCifonautaCreationForm, LoginForm, PasswordResetForm, ForgotUsernameForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
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
    def post(self, request, *args, **keyargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            messages.success(request, "Foi enviada uma mensagem para seu e-mail com instruções para redefinição da senha.")
            return super().form_valid(form)
        
class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = '/user/login'
    template_name = 'users/password_reset_confirm.html'
    def post(self, request, *args, **keyargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            messages.sucess(request, "Senha redefinida com sucesso")
            return super().form_valid(form)
        
class ForgotUsernameView(FormView):
    form_class = ForgotUsernameForm 
    success_url = '/user/login'
    title = _('Esqueceu o Nome de Usuário')
    email_template_name = 'users/forgot_username_email.html'
    subject_template_name = 'users/forgot_username_email.txt'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    template_name = 'users/forgot_username.html'
    def post(self, request, *args, **keyargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            messages.success(request, "Foi enviada uma mensagem de recuperação de nome de usuário para o seu e-mail")
            return self.form_valid(form)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)
