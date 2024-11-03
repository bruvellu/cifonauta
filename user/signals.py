from django.db.models.signals import post_save
from django.dispatch import receiver

from meta.models import Person
from .models import UserCifonauta


@receiver(post_save, sender=UserCifonauta)
def create_person(sender, instance, created, **kwargs):
    if created:
        name = instance.first_name.capitalize() + ' ' + instance.last_name.capitalize()
        email = instance.email
        orcid = instance.orcid
        idlattes = instance.idlattes

        Person.objects.create(name=name, email=email, orcid=orcid, idlattes=idlattes, user_cifonauta=instance)