# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .models import Media, Curadoria, Person, ModifiedMedia, Taxon, Tour
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
    taxons = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Taxon.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "select2-taxons", "multiple": "multiple"}
        ),
        label=_('Táxons'),
        help_text=_('Táxons pertencentes à mídia.')
    )

    class Meta:
        model = Media
        fields = ('title', 'caption', 'taxons', 'co_author', 'author', 'date', 'country', 'state', 'city', 'location', 'geolocation', 'license', 'terms')
        widgets = {
            'co_author': forms.SelectMultiple(attrs={"class": "select2-co-author", "multiple": "multiple"}),
        }

class UpdateMyMediaForm(forms.ModelForm):
    taxons = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Taxon.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "select2-taxons", "multiple": "multiple"}
        ),
        label=_('Táxons'),
        help_text=_('Táxons pertencentes à mídia.')
    )

    class Meta:
        model = Media
        fields = ('title', 'caption', 'taxons', 'co_author', 'author', 'date', 'country', 'state', 'city', 'location', 'geolocation', 'license')
        widgets = {
            'co_author': forms.SelectMultiple(attrs={"class": "select2-co-author", "multiple": "multiple"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['taxons'].initial = self.instance.taxon_set.all()

        if self.instance.status != 'not_edited':
            self.fields['title'].required = True

class EditMetadataForm(forms.ModelForm):
    taxons = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Taxon.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "select2-taxons", "multiple": "multiple"}
        ),
        label=_('Táxons'),
        help_text=_('Táxons pertencentes à mídia.')
    )

    class Meta:
        model = Media
        fields = ( 'title', 'author', 'co_author', 'specialist', 'caption', 'size', 'date', 'taxons', 'license', 'credit', 'country', 'state', 'city', 'location', 'geolocation', 'life_stage', 'habitat', 'microscopy', 'life_style', 'photographic_technique', 'several', 'software')
        widgets = {
            'co_author': forms.SelectMultiple(attrs={"class": "select2-co-author", "multiple": "multiple"}),
            'specialist': forms.SelectMultiple(attrs={"class": "select2-specialist", "multiple": "multiple"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].required = True
        if self.instance.pk:
            self.fields['taxons'].initial = self.instance.taxon_set.all()

class CoauthorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name',)

class ModifiedMediaForm(forms.ModelForm):
    class Meta:
        model = ModifiedMedia
        fields = ( 'title', 'caption', 'taxons', 'co_author', 'date', 'country', 'state', 'city', 'location', 'geolocation')

class MyMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('title', 'coverpath', 'file', 'status', 'timestamp')
        widgets = {
            'taxons': forms.CheckboxSelectMultiple()
        }

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'
        widgets = {
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)
        
        self.fields['media'].label_from_instance = lambda obj: obj.title

class SearchForm(forms.Form):
    query = forms.CharField(label=_('Buscar por'),
                widget=forms.TextInput(attrs={'size': 32}),
                help_text=_('(digite um ou mais termos)'),)


class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label=_('Navegando por'))


class DisplayForm(forms.Form):
    '''Parameters to filter search results.'''

    Taxon = apps.get_model('meta', 'Taxon')
    Tag = apps.get_model('meta', 'Tag')
    Person = apps.get_model('meta', 'Person')
    Location = apps.get_model('meta', 'Location')
    City = apps.get_model('meta', 'City')
    State = apps.get_model('meta', 'State')
    Country = apps.get_model('meta', 'Country')

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

    taxon = forms.ModelMultipleChoiceField(required=False,
                                           queryset=Taxon.objects.all(),
                                           widget=forms.SelectMultiple(
                                               attrs={"class": "select2-options",
                                                      "multiple": "multiple"}),
                                           label=_('Táxons'))
    tag = forms.ModelMultipleChoiceField(required=False,
                                         queryset=Tag.objects.all(),
                                         widget=forms.SelectMultiple(
                                             attrs={"class": "select2-options",
                                                    "multiple": "multiple"}),
                                         label=_('Marcadores'))
    author = forms.ModelMultipleChoiceField(required=False,
                                            queryset=Person.objects.all(),
                                            widget=forms.SelectMultiple(
                                                attrs={"class": "select2-options",
                                                       "multiple": "multiple"}),
                                            label=_('Autores'),)
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
        
        self.fields['curators'].queryset = UserCifonauta.objects.filter(is_author=True)
        self.fields['specialists'].queryset = UserCifonauta.objects.filter(is_author=True)
