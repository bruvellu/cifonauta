from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _
from django.template import loader 
from django.core.mail import EmailMultiAlternatives 
from .models import UserCifonauta
from meta.models import Curation
from django import forms


class UserCifonautaCreationForm(UserCreationForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'get-password'

    class Meta:
        model = UserCifonauta
        fields = ('first_name','last_name' ,'username', 'email', 'orcid', 'idlattes')


class UserCifonautaChangeForm(forms.ModelForm):
    specialist_of = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Curation.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "select2-options", "multiple": "multiple"}
        ),
        label=_('Especialista de')
    )
    curator_of = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Curation.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "select2-options", "multiple": "multiple"}
        ),
        label=_('Curador de')
    )

    class Meta:
        model = UserCifonauta
        fields = ('first_name','last_name' ,'username', 'email', 'orcid', 'idlattes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['curator_of'].initial = self.instance.curatorship_curator.all()
            self.fields['specialist_of'].initial = self.instance.curatorship_specialist.all()

    def save(self, commit=True):
        user_instance = super().save(commit=False)

        if commit:
            user_instance.save()

        specialist_of = self.cleaned_data.get('specialist_of', [])
        curator_of = self.cleaned_data.get('curator_of', [])

        user_instance.curatorship_specialist.set(specialist_of)
        user_instance.curatorship_curator.set(curator_of)

        return user_instance



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

class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")
        email_message.send()
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserCifonauta.get_email_field_name()
        active_users = UserCifonauta._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
        )
    def save(
        self,
        domain_override=None,
        subject_template_name="templates/users/forgot_username_email.txt",
        email_template_name="templates/users/forgot_username_email.html",
        use_https=False,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserCifonauta.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "username": user.username,
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )

