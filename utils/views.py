from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError

from meta.forms import BatchActionsForm
from meta.models import Person


@transaction.atomic
def execute_batch_action(request, medias, person, view_name):
    try:
        with transaction.atomic():
            for media in medias:
                form = BatchActionsForm(request.POST, instance=media, person=person, view_name=view_name)
                form.save()
    except Exception as error:
        messages.error(request, 'Houve um erro ao tentar aplicar as ações em lote')
        if isinstance(error, ValidationError):
            messages.error(request, *error)
        return True
