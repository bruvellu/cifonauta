from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import PasswordResetForm
from captcha.fields import CaptchaField

from .models import UserCifonauta
from django import forms


class UserCifonautaCreationForm(UserCreationForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'get-password'

    class Meta:
        model = UserCifonauta
        fields = ('first_name','last_name' ,'username', 'email', 'orcid', 'idlattes')


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['class'] = 'get-password'

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = UserCifonauta.objects.filter(username=username).first()

            if not user or not user.check_password(password):
                raise forms.ValidationError('Credenciais inválidas')

        return cleaned_data

class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='E-mail', max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    def get_users(self, email):
        active_users = UserCifonauta.objects.filter(email__iexact=email, is_active=True)
        return active_users