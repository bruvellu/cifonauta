from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from captcha.fields import CaptchaField

from .models import UserCifonauta

class UserCifonautaCreationForm(UserCreationForm):
    captcha = CaptchaField()
    class Meta:
        model = UserCifonauta
        fields = ('first_name','last_name' ,'username', 'email', 'orcid', 'idlattes')
