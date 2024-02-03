from django.db import transaction
from django.forms import ValidationError
from django.contrib import messages
from meta.forms import BashActionsForm
from meta.models import Person

@transaction.atomic
def execute_bash_action(request, medias, user, view_name):
    user_person = Person.objects.filter(user_cifonauta=user).first()

    try:
        with transaction.atomic():
            for media in medias:
                form = BashActionsForm(request.POST, instance=media, user_person=user_person, view_name=view_name)
                form.save()
    except Exception as error:
        messages.error(request, 'Houve um erro ao tentar aplicar as ações em lote')
        if isinstance(error, ValidationError):
            messages.error(request, *error)
        return True
