from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Curadoria, UserCifonauta

@receiver(m2m_changed, sender=UserCifonauta.groups.through)
def add_curadoria_to_user(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        # Check if a new group was added to the user
        if pk_set:
            
            group_curadoria = Curadoria.objects.filter(groups__in=pk_set)
            instance.curadoria.add(*group_curadoria)
            print(group_curadoria)