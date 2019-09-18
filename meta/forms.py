# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


METAS = (
        ('person', _('autor')),
        ('taxon', _('táxon')),
        ('size', _('tamanho')),
        ('sublocation', _('local')),
        ('city', _('cidade')),
        ('state', _('estado')),
        ('country', _('país')),
        )

ITEMS = (
        ('16', '16'),
        ('40', '40'),
        ('80', '80'),
        ('120', '120'),
        ('220', '220'),
        ('460', '460'),
        ('900', '900'),
        )

ORDER = (
        ('asc', _('ascendente')),
        ('desc', _('descendente')),
        )

ORDER_BY = (
        ('id', _('id')),
        ('stats__pageviews', _('visitas')),
        ('date', _('data da imagem')),
        ('pub_date', _('data de publicação')),
        ('timestamp', _('data de modificação')),
        ('random', _('aleatório')),
        )

DATATYPES = (
        ('photo', _('fotos')),
        ('video', _('vídeos')),
        ('all', _('todos')),
        )

OPERATORS = (
        ('and', _('E')),
        ('or', _('OU')),
        )


class SearchForm(forms.Form):
    query = forms.CharField(label=_('Buscar por'),
                widget=forms.TextInput(attrs={'size': 32}),
                help_text=_('(digite um ou mais termos)'),)


class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label=_('Navegando por'))


class DisplayForm(forms.Form):
    '''Parameters to alter search results.'''

    Size = apps.get_model('meta', 'Size')
    Person = apps.get_model('meta', 'Person')
    Tag = apps.get_model('meta', 'Tag')
    Sublocation = apps.get_model('meta', 'Sublocation')
    City = apps.get_model('meta', 'City')
    State = apps.get_model('meta', 'State')
    Country = apps.get_model('meta', 'Country')
    # Taxon = apps.get_model('meta', 'Taxon')

    query = forms.CharField(
            required=False,
            label=_('Buscar por'),
            widget=forms.TextInput(),
            )
    datatype = forms.ChoiceField(
            required=False,
            choices=DATATYPES,
            initial='all',
            label=_('Tipo de arquivo')
            )
    n = forms.ChoiceField(
            required=False,
            choices=ITEMS,
            initial='40',
            label=_('Arquivos por página')
            )
    orderby = forms.ChoiceField(
            required=False,
            choices=ORDER_BY,
            initial='random',
            label=_('Ordenar por')
            )
    order = forms.ChoiceField(
            required=False,
            choices=ORDER,
            initial='desc',
            label=_('Ordem')
            )
    highlight = forms.BooleanField(
            required=False,
            initial=False,
            label=_('Somente destaques')
            )
    operator = forms.ChoiceField(
            required=False,
            choices=OPERATORS,
            initial='and',
            label=_('Operador')
            )
    size = forms.ModelMultipleChoiceField(queryset=Size.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Tamanhos'))
    author = forms.ModelMultipleChoiceField(queryset=Person.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Autores'))
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Marcadores'))
    sublocation = forms.ModelMultipleChoiceField(queryset=Sublocation.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Localidades'))
    city = forms.ModelMultipleChoiceField(queryset=City.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Cidades'))
    state = forms.ModelMultipleChoiceField(queryset=State.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Estados'))
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(),
            widget=forms.CheckboxSelectMultiple(), required=False,
            label=_('Países'))
    # taxon = forms.ModelMultipleChoiceField(queryset=Taxon.objects.all(),
            # widget=forms.CheckboxSelectMultiple(), required=False,
            # label=_('Táxons'))


class AdminForm(forms.Form):
    '''Seleciona destaques e inclui imagens em tours.'''
    Tour = apps.get_model('meta', 'Tour')
    highlight = forms.BooleanField(required=False, initial=False, label=_('Destaque'))
    cover = forms.BooleanField(required=False, initial=False, label=_('Imagem de capa'))
    tours = forms.ModelMultipleChoiceField(queryset=Tour.objects.all(),
            widget=forms.CheckboxSelectMultiple(attrs={'class':'check-taxon'}),
            required=False, label=_('Escolher tour(s)'))
