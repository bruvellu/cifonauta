# -*- coding: utf-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from meta.models import Image, Video, Tour

@dajaxice_register
def update_counter(request, type, id):
    '''Conta as visualizações de página.'''
    dajax = Dajax()
    if type == 'photo':
        related = Image.objects.get(id=id)
    elif type == 'video':
        related = Video.objects.get(id=id)
    elif type == 'tour':
        related = Tour.objects.get(id=id)
    #XXX Usar o F para atualizar o campo?
    stats = related.stats
    stats.pageviews += 1
    stats.save()
    #dajax.assign('#pageviews', 'innerHTML', stats.pageviews)
    #return dajax.json()
