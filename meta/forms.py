# -*- coding: utf-8 -*-

from django import forms
from meta.models import *
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


METAS = (
        (u'author', _(u'autor')),
        (u'taxon', _(u'táxon')),
        (u'size', _(u'tamanho')),
        (u'sublocation', _(u'local')),
        (u'city', _(u'cidade')),
        (u'state', _(u'estado')),
        (u'country', _(u'país')),
        )

ITEMS = (
        (16, 16),
        (40, 40),
        (80, 80),
        (120, 120),
        (220, 220),
        (460, 460),
        (900, 900),
        )

ORDER = (
        ('asc', _(u'ascendente')),
        ('desc', _(u'descendente')),
        )

ORDER_BY = (
        ('id', _(u'id')),
        ('stats__pageviews', _(u'visitas')),
        ('date', _(u'data da imagem')),
        ('pub_date', _(u'data de publicação')),
        ('timestamp', _(u'data de modificação')),
        ('random', _(u'aleatório')),
        )


class SearchForm(forms.Form):
    query = forms.CharField(
            label=_('Buscar por'),
            widget=forms.TextInput(attrs={'size': 32}),
            help_text=_('(digite um ou mais termos)'),
            )


class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label=_('Navegando por'))
    #TODO Incluir um checkbox para mostrar apenas highlights?


class DisplayForm(forms.Form):
    '''Formulário para alterar parâmetros dos resultados de buscas.

    Pode ser alterado por qual metadado as imagens serão ordenadas, se esta ordem será ascendente ou descendente, o número de resultados por página e se é para mostrar apenas os destaques.
    '''
    #FIXME Incluir caracteres especiais quebra a tradução!
    n = forms.ChoiceField(choices=ITEMS, label=_('Exibir'))
    orderby = forms.ChoiceField(choices=ORDER_BY, label=_('Ordenar por'))
    order = forms.ChoiceField(choices=ORDER, label=_('Ordem'))
    highlight = forms.BooleanField(required=False, initial=False, label=_('Somente destaques'))


class AdminForm(forms.Form):
    '''Seleciona destaques e inclui imagens em tours.'''
    def get_tours():
        tours = Tour.objects.all()
        tuplelist_tours = [(tour.id, tour.name) for tour in tours]
        tuple_tours = tuple(tuplelist_tours)
        return tuple_tours

    highlight = forms.BooleanField(required=False, initial=False, label=_('Destaque'))
    cover = forms.BooleanField(required=False, initial=False, label=_('Imagem de capa'))
    tours = forms.MultipleChoiceField(choices=get_tours(), widget=forms.CheckboxSelectMultiple(attrs={'class':'check-taxon'}), required=False, label=_('Escolher tour(s)'))
