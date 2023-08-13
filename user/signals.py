from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Curadoria, UserCifonauta


@receiver(m2m_changed, sender=UserCifonauta.specialist_of.through)
def update_specialists(sender, instance, action, model, pk_set, **kwargs):
    if action == 'post_add':
        if model == Curadoria and pk_set:
            curadorias = Curadoria.objects.filter(id__in=pk_set)
            for curadoria in curadorias:
                curadoria.specialists.add(instance)

    elif action == "post_remove":
        if model == Curadoria and pk_set:
            curadorias = Curadoria.objects.filter(id__in=pk_set)
            for curadoria in curadorias:
                curadoria.specialists.remove(instance)
                

@receiver(m2m_changed, sender=UserCifonauta.curator_of.through)
def update_curators(sender, instance, action, model, pk_set, **kwargs):
    if action == 'post_add':
        if model == Curadoria and pk_set:
            curadorias = Curadoria.objects.filter(id__in=pk_set)
            for curadoria in curadorias:
                curadoria.curators.add(instance)

    elif action == "post_remove":
        if model == Curadoria and pk_set:
            
            curadorias = Curadoria.objects.filter(id__in=pk_set)
            for curadoria in curadorias:
                curadoria.curators.remove(instance)