# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Media, Curadoria, UserPreRegistration
from django.contrib.auth import get_user_model
from user.models import UserCifonauta


METAS = (
        ('person', _('autor')),
        ('taxon', _('táxon')),
        # ('size', _('tamanho')),
        ('location', _('local')),
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
        ('or', _('OU')),
        ('and', _('E')),
        )

class UploadMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('file', 'author', 'co_author', 'title', 'caption', 'date',  'has_taxons', 'taxons', 'country', 'state', 'city', 'location', 'geolocation',) #Faltando direito autoral
        widgets = {
            'taxons': forms.CheckboxSelectMultiple(),
            'has_taxons': forms.RadioSelect()
        }


class UserPreRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserPreRegistration
        fields = ('first_name', 'last_name', 'orcid')


class MyMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = '__all__'
        widgets = {
            'taxons': forms.CheckboxSelectMultiple()
        }


class SearchForm(forms.Form):
    query = forms.CharField(label=_('Buscar por'),
                widget=forms.TextInput(attrs={'size': 32}),
                help_text=_('(digite um ou mais termos)'),)


class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label=_('Navegando por'))


class DisplayForm(forms.Form):
    '''Parameters to filter search results.'''

    Person = apps.get_model('meta', 'Person')
    Tag = apps.get_model('meta', 'Tag')
    Location = apps.get_model('meta', 'Location')
    City = apps.get_model('meta', 'City')
    State = apps.get_model('meta', 'State')
    Country = apps.get_model('meta', 'Country')
    Taxon = apps.get_model('meta', 'Taxon')

    query = forms.CharField(required=False,
                            label=_('Buscar por'),
                            widget=forms.TextInput(attrs={"query": "query"}),)
    datatype = forms.ChoiceField(required=False,
                                 choices=DATATYPES,
                                 initial='all',
                                 label=_('Tipo de arquivo'),
                                 widget=forms.Select(attrs={"fields": "fields"}))
    n = forms.ChoiceField(required=False,
                          choices=ITEMS,
                          initial='40',
                          label=_('Arquivos por página'))
    orderby = forms.ChoiceField(required=False,
                                choices=ORDER_BY,
                                initial='random',
                                label=_('Ordenar por'),
                                widget=forms.Select(attrs={"fields": "fields"}))
    order = forms.ChoiceField(required=False,
                              choices=ORDER,
                              initial='desc',
                              label=_('Ordem'))
    highlight = forms.BooleanField(required=False,
                                   initial=False,
                                   label=_('Somente destaques'),
                                   widget=forms.CheckboxInput(attrs={"fields": "fields"}))
    operator = forms.ChoiceField(required=False,
                                 choices=OPERATORS,
                                 initial='and',
                                 label=_('Operador'))

    author = forms.ModelMultipleChoiceField(required=False,
                                            queryset=Person.objects.all(),
                                            widget=forms.SelectMultiple(
                                                attrs={"class": "select2-options",
                                                       "multiple": "multiple"}),
                                            label=_('Autores'),)
    tag = forms.ModelMultipleChoiceField(required=False,
                                         queryset=Tag.objects.all(),
                                         widget=forms.SelectMultiple(
                                             attrs={"class": "select2-options",
                                                    "multiple": "multiple"}),
                                         label=_('Marcadores'))
    location = forms.ModelMultipleChoiceField(required=False,
                                         queryset=Location.objects.all(),
                                         widget=forms.SelectMultiple(
                                             attrs={"class": "select2-options",
                                                    "multiple": "multiple"}),
                                         label=_('Localidades'))
    city = forms.ModelMultipleChoiceField(required=False,
                                          queryset=City.objects.all(),
                                          widget=forms.SelectMultiple(
                                              attrs={"class": "select2-options",
                                                     "multiple": "multiple"}),
                                          label=_('Cidades'))
    state = forms.ModelMultipleChoiceField(required=False,
                                           queryset=State.objects.all(),
                                           widget=forms.SelectMultiple(
                                               attrs={"class": "select2-options",
                                                      "multiple": "multiple"}),
                                           label=_('Estados'))
    country = forms.ModelMultipleChoiceField(required=False,
                                             queryset=Country.objects.all(),
                                             widget=forms.SelectMultiple(
                                                 attrs={"class": "select2-options",
                                                        "multiple": "multiple"}),
                                             label=_('Países'))
    taxon = forms.ModelMultipleChoiceField(required=False,
                                           queryset=Taxon.objects.all(),
                                           widget=forms.SelectMultiple(
                                               attrs={"class": "select2-options",
                                                      "multiple": "multiple"}),
                                           label=_('Táxons'))


class AdminForm(forms.Form):
    '''Seleciona destaques e inclui imagens em tours.'''
    Tour = apps.get_model('meta', 'Tour')
    highlight = forms.BooleanField(required=False, initial=False, label=_('Destaque'))
    cover = forms.BooleanField(required=False, initial=False, label=_('Imagem de capa'))
    tours = forms.ModelMultipleChoiceField(queryset=Tour.objects.all(),
            widget=forms.CheckboxSelectMultiple(attrs={'class':'check-taxon'}),
            required=False, label=_('Escolher tour(s)'))
    

class CuradoriaAdminForm(forms.ModelForm):
    class Meta:
        model = Curadoria
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curators'].queryset = self.fields['curators'].queryset.filter(is_author=True)
        self.fields['specialists'].queryset = self.fields['specialists'].queryset.filter(is_author=True)
