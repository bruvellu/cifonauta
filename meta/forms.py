# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .models import Media, Curadoria, ModifiedMedia, Person, Taxon, Tour
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
        ('date_created', _('data de criação')),
        ('date_published', _('data de publicação')),
        ('date_modified', _('data de modificação')),
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
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'authors', 'date_created', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license', 'terms')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'date_created': forms.DateInput(attrs={'type': 'date'}),
            'terms': forms.CheckboxInput(attrs={'class': 'dashboard-input'})
        }
        help_texts = {
            'date_created': 'Data em que a mídia foi produzida. Caso a data seja desconhecida, preencher com "01/01/0001"',
        }

    def __init__(self, *args, **kwargs):
        self.media_author = kwargs.pop('media_author', None)
        super().__init__(*args, **kwargs)

        self.fields['license'].required = True
        self.fields['date_created'].required = True
        self.fields['taxa'].queryset = self.fields['taxa'].queryset.exclude(name='Sem táxon')

    def clean_authors(self):
        authors = self.cleaned_data['authors']

        if self.media_author and self.media_author not in authors:
            
            self.add_error('authors', forms.ValidationError(
                _(f"Você ({self.media_author}) deve ser incluído como autor"), 
                code="required"
            ))

        return authors 

    def clean_terms(self):
        terms = self.cleaned_data['terms']

        if not terms:
            self.add_error('terms', forms.ValidationError(
                _("Você precisa aceitar os termos"), 
                code="required"
            ))

        return terms

    def clean_taxa(self):
        taxa = self.cleaned_data['taxa']

        if taxa:
            taxa.exclude(name='Sem táxon')
        if not taxa:
            taxa = Taxon.objects.filter(name='Sem táxon')

        return taxa

class UpdateMyMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'authors', 'date_created', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license')
        widgets = {
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'date_created': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }
        help_texts = {
            'date_created': 'Data em que a mídia foi produzida. Caso a data seja desconhecida, preencher com "01/01/0001"',
        }
    
    def __init__(self, *args, **kwargs):
        self.media_author = kwargs.pop('media_author', None)
        media_status = kwargs.pop('media_status', None)
        super().__init__(*args, **kwargs)

        if media_status and media_status != 'draft':
            self.fields['title_pt_br'].required = True
            self.fields['title_en'].required = True
        self.fields['taxa'].queryset = self.fields['taxa'].queryset.exclude(name='Sem táxon')
        self.fields['license'].required = True
        self.fields['date_created'].required = True
    
    def clean_authors(self):
        authors = self.cleaned_data['authors']

        if self.media_author and self.media_author not in authors:
            
            self.add_error('authors', forms.ValidationError(
                _(f"Você ({self.media_author}) deve ser incluído como autor"), 
                code="required"
            ))

        return authors 
    
    def clean_taxa(self):
        taxa = self.cleaned_data['taxa']

        if taxa:
            taxa.exclude(name='Sem táxon')
        if not taxa:
            taxa = Taxon.objects.filter(name='Sem táxon')

        return taxa
        

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
                "timestamp": medias[0].date_modified,
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
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'date_created', 'taxa', 'tags', 'scale', 'country', 'state', 'city', 'location', 'latitude', 'longitude')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'tags': forms.SelectMultiple(attrs={"class": "select2-tags", "multiple": "multiple"}),
            'specialists': forms.SelectMultiple(attrs={"class": "select2-specialists", "multiple": "multiple"}),
            'date_created': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date', 'readonly': 'readonly'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title_pt_br'].required = True
        self.fields['title_en'].required = True
        self.fields['date_created'].required = True
        self.fields['tags'].queryset = self.fields['tags'].queryset.order_by('category')
        self.fields['taxa'].queryset = self.fields['taxa'].queryset.exclude(name='Sem táxon')

    def clean_taxa(self):
        taxa = self.cleaned_data['taxa']

        if taxa:
            taxa.exclude(name='Sem táxon')
        if not taxa:
            taxa = Taxon.objects.filter(name='Sem táxon')

        return taxa

class CoauthorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name',)

class ModifiedMediaForm(forms.ModelForm):
    class Meta:
        model = ModifiedMedia
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'tags', 'scale', 'authors', 'date_created', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license')
        widgets = {
            'date_created': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        author_form = kwargs.pop('author_form', None)
        super().__init__(*args, **kwargs)

        if author_form:
            self.fields.pop('tags')
            self.fields.pop('scale')
            self.fields['license'].required = True
        else:
            self.fields.pop('authors')
            self.fields.pop('license')

        self.fields['title_pt_br'].required = True
        self.fields['title_en'].required = True
        self.fields['date_created'].required = True
        self.fields['taxa'].queryset = self.fields['taxa'].queryset.exclude(name='Sem táxon')
    
    def clean_taxa(self):
        taxa = self.cleaned_data['taxa']

        if taxa:
            taxa.exclude(name='Sem táxon')
        if not taxa:
            taxa = Taxon.objects.filter(name='Sem táxon')

        return taxa

class MyMediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('title', 'coverpath', 'file', 'status')
        widgets = {
            'taxons': forms.CheckboxSelectMultiple()
        }

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'
        widgets = {
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
            'is_public': forms.CheckboxInput(attrs={'class': 'dashboard-input is-public-checkbox'})
        }
    
    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)
        
        self.fields['media'].label_from_instance = lambda obj: obj.title


class SpecialistActionForm(forms.ModelForm, SendEmailForm):
    STATUS_CHOICES = [
        ('maintain', _('Manter status')),
        ('submitted', _('Enviar para revisão')),
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


class DashboardFilterForm(forms.Form):
    Curadoria = apps.get_model('meta', 'Curadoria')
    
    search = forms.CharField(required=False,
                             label=_('Buscar por'),
                             widget=forms.TextInput(attrs={'placeholder': _('Digite o título da mídia')}))
    curations = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Curadoria.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "select2-curations", "multiple": "multiple"}),
        label=_('Curadorias')
    )
    alphabetical_order = forms.BooleanField(required=False,
                                   initial=False,
                                   label=_('Ordem alfabética'),
                                   widget=forms.CheckboxInput(attrs={'class': 'dashboard-input'}))

    def __init__(self, *args, **kwargs):
        user_curations = kwargs.pop('user_curations', None)
        super().__init__(*args, **kwargs)

        if user_curations:
            if not user_curations.filter(name='Sem táxon').exists():
                self.fields['curations'].queryset = self.fields['curations'].queryset.exclude(name='Sem táxon')
            

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
