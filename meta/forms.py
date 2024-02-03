# -*- coding: utf-8 -*-

from django import forms
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .models import Media, Curadoria, ModifiedMedia, Person, Taxon, Tour, Location
from user.models import UserCifonauta
from django.template import loader 
from django.core.mail import EmailMultiAlternatives
from django.db.models.query import QuerySet
from django.db import models
from utils.media import format_name
from django.utils import timezone
from django.forms import ValidationError


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


class SendEmailForm(forms.Form):
    def send_mail(
            self,
            sender,
            receivers,
            medias,
            subject_template_name,
            email_template_name,
            modification_accepted=False,
            modified_media_specialists_message=False,
            from_email=None,
            html_email_template_name=None,
        ):
            # TODO: Improve it
            if isinstance(receivers, models.Model):
                receivers = [receivers]
            elif isinstance(receivers, QuerySet):
                receivers = list(receivers)
            elif isinstance(receivers, (list, set)):
                receivers = list(receivers)
            else:
                print('Não foi possível converter receivers')
                return

            if isinstance(medias, models.Model):
                medias = [medias]
            elif isinstance(medias, QuerySet):
                medias = list(medias)
            elif isinstance(medias, (list, set)):
                medias = list(medias)
            else:
                print('Não foi possível converter medias')
                return

            email = [receiver.email for receiver in receivers]

            context = {
                "single_media": True if len(medias) == 1 else False,
                "media_names": [media.title_pt_br for media in medias],
                "sender_name": sender.get_full_name(),
                "timestamp": medias[0].date_modified,
                "modified_media": medias[0].modified_media.first(),
                "modification_accepted": modification_accepted,
                "modified_media_specialists_message": modified_media_specialists_message
            }

            subject = subject_template_name
            # Email subject must not contain newlines
            subject = "".join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)

            email_message = EmailMultiAlternatives(subject, body, from_email, email)
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)
                email_message.attach_alternative(html_email, "text/html")
            email_message.send()

class UploadMediaForm(forms.ModelForm,  SendEmailForm):
    class Meta:
        model = Media
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'authors', 'date_created', 'references', 'scale', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license', 'terms')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
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
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'authors', 'date_created', 'references', 'scale', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license')
        widgets = {
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
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

class EditMetadataForm(forms.ModelForm, SendEmailForm):
    class Meta:
        model = Media
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'references', 'tags', 'scale', 'country', 'state', 'city', 'location', 'latitude', 'longitude')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
            'tags': forms.SelectMultiple(attrs={"class": "select2-tags", "multiple": "multiple"}),
            'specialists': forms.SelectMultiple(attrs={"class": "select2-specialists", "multiple": "multiple"}),
            'date_created': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date', 'readonly': 'readonly'})
        }
    
    def __init__(self, *args, **kwargs):
        editing_media_details = kwargs.pop('editing_media_details', None)
        super().__init__(*args, **kwargs)

        if not editing_media_details:
            self.fields['title_pt_br'].required = True
            self.fields['title_en'].required = True
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True

    def clean_name(self):
        name = self.cleaned_data['name']
        name = format_name(name)
        
        return name

class AddLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('name',)
    
    def clean_name(self):
        name = self.cleaned_data['name']
        name = format_name(name)
        
        return name

class AddTaxaForm(forms.ModelForm):
    class Meta:
        model = Taxon
        fields = ('name',)

    def clean_name(self):
        name = self.cleaned_data['name']
        name = format_name(name)
        
        return name

class ModifiedMediaForm(forms.ModelForm, SendEmailForm):
    class Meta:
        model = ModifiedMedia
        fields = ('title_pt_br', 'title_en', 'caption_pt_br', 'caption_en', 'taxa', 'tags', 'scale', 'authors', 'date_created', 'references', 'country', 'state', 'city', 'location', 'latitude', 'longitude', 'license')
        widgets = {
            'date_created': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
        }

    def __init__(self, *args, **kwargs):
        author_form = kwargs.pop('author_form', None)
        super().__init__(*args, **kwargs)

        if author_form:
            self.fields.pop('tags')
            self.fields['license'].required = True
            self.fields['date_created'].required = True
        else:
            self.fields.pop('authors')
            self.fields.pop('license')
            self.fields.pop('date_created')

        self.fields['title_pt_br'].required = True
        self.fields['title_en'].required = True
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

    TAXA_CHOICES = [
        ('maintain', _('Manter táxons')),
        ('overwrite', _('Sobrescrever táxons')),
    ]

    status_action = forms.ChoiceField(label=_('Status'), choices=STATUS_CHOICES, initial='maintain')
    # Added data-field-action so javascript can find it
    taxa_action = forms.ChoiceField(label=_('Táxons'), choices=TAXA_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "taxa_action"}))

    class Meta:
        model = Media
        fields = ('status_action', 'taxa_action', 'taxa',)
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"})
        }


        
        
class BashActionsForm(forms.ModelForm, SendEmailForm):
    STATUS_CHOICES = [
        ('maintain', _('Manter status')),
        ('submitted', _('Enviar para revisão')),
        ('publish', _('Publicar')),
    ]
    ACTION_CHOICES = [('maintain', _('Manter')), ('override', _('Sobrescrever'))]

    status_action = forms.ChoiceField(label=_('Status'), choices=STATUS_CHOICES, initial='maintain')
    title_pt_br_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "title_pt_br_action"}))
    title_en_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "title_en_action"}))
    caption_pt_br_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "caption_pt_br_action"}))
    caption_en_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "caption_en_action"}))
    authors_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "authors_action"}))
    date_created_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "date_created_action"}))
    taxa_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "taxa_action"}))
    tags_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "tags_action"}))
    scale_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "scale_action"}))
    references_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "references_action"}))
    location_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "location_action"}))
    latitude_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "latitude_action"}))
    longitude_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "longitude_action"}))
    license_action = forms.ChoiceField(choices=ACTION_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "license_action"}))

    # Missing country, state and city fields
    class Meta:
        model = Media
        fields = ('status_action', 'title_pt_br_action', 'title_en_action', 'caption_pt_br_action', 'caption_en_action', 'taxa_action', 'authors_action', 'date_created_action', 'tags_action', 'scale_action', 'references_action', 'location_action', 'latitude_action', 'longitude_action', 'license_action', 'title_pt_br', 'title_en',  'caption_pt_br', 'caption_en', 'taxa', 'authors', 'date_created', 'tags', 'scale', 'references', 'location', 'latitude', 'longitude', 'license')
        widgets = {
            'taxa': forms.SelectMultiple(attrs={"class": "select2-taxons", "multiple": "multiple"}),
            'authors': forms.SelectMultiple(attrs={"class": "select2-authors", "multiple": "multiple"}),
            'tags': forms.SelectMultiple(attrs={"class": "select2-tags", "multiple": "multiple"}),
            'references': forms.SelectMultiple(attrs={"class": "select2-references", "multiple": "multiple"}),
            'date_created': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_person = kwargs.pop('user_person', None)
        self.view_name = kwargs.pop('view_name', None)
        super().__init__(*args, **kwargs)

        # If there is a required field and I delete it from cleaned_data in the clean method, it doesn't work, this is why I make all of the fields not required
        for field_name in self.fields:
            self.fields[field_name].required = False

            if field_name[-7:] == '_action': 
                if field_name[:-7] in self.fields:
                    # Addind the actual field's label to <field>_action so I don't have to rewrite the labels
                    self.fields[field_name].label = self.fields[field_name[:-7]].label

        # If there is a field that is required, add the required in the <field>_action
        self.fields['title_pt_br_action'].required = True
        self.fields['title_en_action'].required = True


        # To remove a field, remove also its <field>_action
        if self.view_name == 'my_media_list':
            self.fields.pop('status_action', None)
            self.fields.pop('status', None)
            self.fields.pop('scale_action', None)
            self.fields.pop('scale', None)
            self.fields.pop('tags_action', None)
            self.fields.pop('tags', None)
            self.fields['date_created_action'].required = True
            self.fields['license_action'].required = True
            self.fields['authors_action'].required = True
            self.fields['authors'].initial = self.user_person
        elif self.view_name == 'editing_media_list' or self.view_name == 'revision_media_list' or self.view_name == 'my_curations_media_list':
            self.fields.pop('date_created_action', None)
            self.fields.pop('date_created', None)
            self.fields.pop('license_action', None)
            self.fields.pop('license', None)
            self.fields.pop('authors_action', None)
            self.fields.pop('authors', None)

            if self.view_name == 'editing_media_list':
                self.fields['status_action'].choices = (self.STATUS_CHOICES[0], self.STATUS_CHOICES[1])
            elif self.view_name == 'revision_media_list':
                self.fields['status_action'].choices = (self.STATUS_CHOICES[0], self.STATUS_CHOICES[2])
            else:
                self.fields.pop('status_action', None)
                self.fields.pop('status', None)
                
                
        self.fields['taxa'].queryset = self.fields['taxa'].queryset.exclude(name='Sem táxon')
        if 'tags' in self.fields:
            self.fields['tags'].queryset = self.fields['tags'].queryset.order_by('category')

    
    def clean(self):
        cleaned_data = super().clean()
        
        fields_to_remove = []
        # Removing field from cleaned_data so it will not save the data to the entry
        for field_name in cleaned_data:
            if field_name[-7:] == '_action':
                if field_name[:-7] in cleaned_data:
                    if cleaned_data.get(field_name) == 'maintain':
                        fields_to_remove.append(field_name)
                        fields_to_remove.append(field_name[:-7])
        for field in fields_to_remove:
            cleaned_data.pop(field, None)


        return cleaned_data

    def save(self, commit=True):
        media_instance = super().save()

        # Using save method to make custom changes to media fields before saving
        if 'status_action' in self.cleaned_data:
            if self.cleaned_data['status_action'] != 'maintain':
                if self.view_name == 'revision_media_list':
                    media_instance.status = 'published'
                    media_instance.date_published = timezone.now()
                    media_instance.is_public = True
                elif self.view_name == 'my_media_list':
                    media_instance.status = 'draft'
                elif self.view_name == 'editing_media_list':
                    media_instance.status = 'submitted'

        if 'title_pt_br_action' in self.cleaned_data:
            if self.cleaned_data['title_pt_br_action'] != 'maintain':
                if not self.cleaned_data['title_pt_br']:
                    raise ValidationError(f'O campo {self.fields["title_pt_br"].label} é obrigatório')

        if 'title_en_action' in self.cleaned_data:
            if self.cleaned_data['title_en_action'] != 'maintain':
                if not self.cleaned_data['title_en']:
                    raise ValidationError(f'O campo {self.fields["title_en"].label} é obrigatório')

        if 'taxa_action' in self.cleaned_data:
            if self.cleaned_data['taxa_action'] != 'maintain':
                if self.cleaned_data['taxa']:
                    media_instance.taxa.set(self.cleaned_data['taxa'])
                else: 
                    media_instance.taxa.set(Taxon.objects.filter(name='Sem táxon'))
        
        if 'license_action' in self.cleaned_data:
            if self.cleaned_data['license_action'] != 'maintain':
                if not self.cleaned_data['license']:
                    raise ValidationError(f'O campo {self.fields["license"].label} é obrigatório')

        if 'date_created_action' in self.cleaned_data:
            if self.cleaned_data['date_created_action'] != 'maintain':
                if not self.cleaned_data['date_created']:
                    raise ValidationError(f'O campo {self.fields["date_created"].label} é obrigatório')
        
        author_person = Person.objects.filter(user_cifonauta=media_instance.user).first()
        if 'authors_action' in self.cleaned_data:
            if self.cleaned_data['authors'] != 'maintain':
                if author_person not in self.cleaned_data['authors']:
                    raise ValidationError(f"Você ({media_instance.user}) deve ser incluído como autor")


        if self.view_name != 'my_media_list':
            if self.view_name == 'editing_media_list':
                media_instance.specialists.add(self.user_person.id)
            elif self.view_name == 'my_curations_media_list' or self.view_name == 'revision_media_list':
                media_instance.curators.add(self.user_person.id)
        
        if commit:
            media_instance.save()

        return media_instance
            

        


class MyMediasActionForm(forms.ModelForm):
    TAXA_CHOICES = (
        ('maintain', _('Manter táxons')),
        ('overwrite', _('Sobrescrever táxons')),
    )

    taxa_action = forms.ChoiceField(label=_('Táxons'), choices=TAXA_CHOICES, initial='maintain', widget=forms.Select(attrs={"data-field-action": "taxa_action"}))

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

    status = forms.MultipleChoiceField(
        required=False,
        label=_('Status'),
        choices=Media.STATUS_CHOICES[1:],
        widget=forms.SelectMultiple(attrs={"class": "select2-status", "multiple": "multiple"})
    )

    alphabetical_order = forms.BooleanField(required=False,
                                   initial=False,
                                   label=_('Ordem alfabética'),
                                   widget=forms.CheckboxInput(attrs={'class': 'dashboard-input'}))

    def __init__(self, *args, **kwargs):
        user_curations = kwargs.pop('user_curations', None)
        is_editing_media_list = kwargs.pop('is_editing_media_list', None)
        super().__init__(*args, **kwargs)

        if user_curations:
            if not user_curations.filter(name='Sem táxon').exists():
                self.fields['curations'].queryset = self.fields['curations'].queryset.exclude(name='Sem táxon')
        if is_editing_media_list:
            del self.fields['status']
            

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
