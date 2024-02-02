from meta.models import Taxon, Person
from django.utils import timezone
from django.db import transaction

@transaction.atomic
def execute_bath_action(user, form, medias, view_name):
    try:
        with transaction.atomic():
            user_person = Person.objects.filter(user_cifonauta=user).first()
                                
            for media in medias:
                if 'status_action' in form.cleaned_data:
                    if form.cleaned_data['status_action'] != 'maintain':
                        if view_name == 'revision_media_list':
                            media.status = 'published'
                            media.date_published = timezone.now()
                            media.is_public = True
                        elif view_name == 'my_media_list':
                            media.status = 'draft'
                        elif view_name == 'editing_media_list':
                            media.status = 'submitted'

                if 'taxa_action' in form.cleaned_data:
                    if form.cleaned_data['taxa_action'] != 'maintain':
                        if form.cleaned_data['taxa']:
                            media.taxa.set(form.cleaned_data['taxa'])
                        else: 
                            media.taxa.set(Taxon.objects.filter(name='Sem táxon'))
                
                if view_name != 'my_media_list':
                    if view_name == 'editing_media_list':
                        media.specialists.add(user_person)
                    elif view_name == 'my_curations_media_list' or view_name == 'revision_media_list':
                        media.curators.add(user_person)
                
                media.save()

    except Exception as e:
        return str(e)
