from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import UserCifonauta

class UserCifonautaCreationForm(UserCreationForm):
    class Meta:
        model = UserCifonauta
        fields = ('first_name','last_name' ,'username', 'email', 'orcid', 'idlattes')
