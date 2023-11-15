# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .models import Media, Curadoria, Person, ModifiedMedia, Taxon, Tour
from user.models import UserCifonauta
from django.template import loader 
from django.core.mail import EmailMultiAlternatives


METAS = (
        ('author', _('autor')),
        ('taxon', _('táxon')),
        ('location', _('local')),
        ('city', _('cidade')),
        ('state', _('estado')),
        ('country', _('país')),
        )

ITEMS = (
        ('20', '20'),
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
        ('rank', _('ranking')),
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
        fields = ('title', 'caption', 'taxa', 'user', 'authors', 'date', 'country', 'state', 'city', 'location', 'geolocation', 'license', 'terms')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
        }

class UpdateMyMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('title', 'caption', 'taxa', 'user', 'authors', 'date', 'country', 'state', 'city', 'location', 'geolocation', 'license')
        widgets = {
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.status != 'not_edited':
            self.fields['title'].required = True

class SendEmailForm(forms.Form):
    def send_mail(
            self,
            sender,
            medias,
            subject_template_name,
            email_template_name,
            from_email=None,
            html_email_template_name=None,
        ):
            receiver = UserCifonauta.objects.filter(id=medias[0].user.id).first()

            email = receiver.email

            context = {
                "single_media": True if len(medias) == 1 else False,
                "media_names": [media.title for media in medias],
                "sender_name": sender.get_full_name(),
                "timestamp": medias[0].timestamp,
            }

            subject = subject_template_name
            # Email subject must not contain newlines
            subject = "".join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)

            email_message = EmailMultiAlternatives(subject, body, from_email, [email])
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)
                email_message.attach_alternative(html_email, "text/html")
            email_message.send()

class EditMetadataForm(forms.ModelForm, SendEmailForm):
    class Meta:
        model = Media
        fields = ('title', 'user', 'authors', 'caption', 'date', 'taxa', 'license', 'country', 'state', 'city', 'location', 'geolocation')
        widgets = {
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'specialists': forms.SelectMultiple(attrs={"class": "select2-specialists", "multiple": "multiple"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].required = True

class CoauthorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name',)

class ModifiedMediaForm(forms.ModelForm):
    class Meta:
        model = ModifiedMedia
        fields = ( 'title', 'caption', 'taxa', 'authors', 'date', 'country', 'state', 'city', 'location', 'geolocation', 'license')

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

class SpecialistActionForm(forms.ModelForm, SendEmailForm):
    STATUS_CHOICES = [
        ('maintain', _('Manter status')),
        ('to_review', _('Enviar para revisão')),
        ('publish', _('Publicar')),
    ]

    TAXA_CHOICES = (
        ('maintain', _('Manter táxons')),
        ('overwrite', _('Sobrescrever táxons')),
    )

    status_action = forms.ChoiceField(label=_('Status'), choices=STATUS_CHOICES, initial='maintain')
    taxa_action = forms.ChoiceField(label=_('Táxons'), choices=TAXA_CHOICES, initial='maintain')

    class Meta:
        model = Media
        fields = ( 'status_action', 'taxa_action', 'taxa',)
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"})
        }

class MyMediasActionForm(forms.ModelForm):
    TAXA_CHOICES = (
        ('maintain', _('Manter táxons')),
        ('overwrite', _('Sobrescrever táxons')),
    )

    taxa_action = forms.ChoiceField(label=_('Táxons'), choices=TAXA_CHOICES, initial='maintain')

    class Meta:
        model = Media
        fields = ('taxa_action', 'taxa',)
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"})
        }

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
    specialist = forms.ModelMultipleChoiceField(required=False,
                                                queryset=Person.objects.all(),
                                                widget=forms.SelectMultiple(
                                                    attrs={"class": "select2-options",
                                                           "multiple": "multiple"}),
                                                label=_('Especialistas'),)
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
