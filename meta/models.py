# -*- coding: utf-8 -*-

import random
import re
import string
import uuid

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Q, Value
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from utils.media import Metadata, resize_image, resize_video, extract_video_cover


class Curation(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(_('slug'), max_length=64, default='', blank=True,
            help_text=_('Slug do nome da curadoria.'))
    description = models.TextField(_('descrição'), default='', blank=True,
            help_text=_('Descrição da curadoria.'))
    taxa = models.ManyToManyField(
            'Taxon',
            related_name='curations',
            blank=True,
            verbose_name=_('táxons'),
            help_text=_('Táxons nesta curadoria.'))
    specialists = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='curations_as_specialist',
            blank=True,
            verbose_name=_('especialistas'),
            help_text=_('Especialistas nesta curadoria.'))
    curators = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='curations_as_curator',
            blank=True,
            verbose_name=_('curadores'),
            help_text=_('Curadores desta curadoria.'))

    def __str__(self):
        return f'{self.name} [id={self.id}]'


# Function that defines path for user upload directory
# See: https://docs.djangoproject.com/en/4.2/ref/models/fields/#django.db.models.FileField.upload_to
def user_upload_directory(instance, filename):
    return f'{settings.UPLOAD_ROOT}/{instance.user.id}/{filename}'


#TODO: Remove after the official migration
def save_file(instance, filename):
    return f'{settings.UPLOAD_ROOT}/{instance.user.username}/{filename}'


#TODO: Remove after the official migration
def save_cover(instance, filename):
    return f'{instance.user.username}/{filename}'


class Media(models.Model):
    '''Table with metadata for photo and video files.'''

    # Pre-defined choices
    STATUS_CHOICES = (('loaded', _('Carregado')),
                      ('draft', _('Rascunho')),
                      ('submitted', _('Submetido')),
                      ('published', _('Publicado')))

    LICENSE_CHOICES = (('cc0', _('CC0 (Domínio Público)')),
                       ('cc_by', _('CC BY (Atribuição)')),
                       ('cc_by_sa', _('CC BY-SA (Atribuição-CompartilhaIgual)')),
                       ('cc_by_nd', _('CC BY-ND (Atribuição-SemDerivações)')),
                       ('cc_by_nc', _('CC BY-NC (Atribuição-NãoComercial)')),
                       ('cc_by_nc_sa', _('CC BY-NC-SA (AtribuiçãoNãoComercial-CompartilhaIgual)')),
                       ('cc_by_nc_nd', _('CC BY-NC-ND (Atribuição-SemDerivações-SemDerivados)')))

    DATATYPE_CHOICES = (('photo', _('photo')),
                        ('video', _('video')))

    SCALE_CHOICES = (('micro', _('<0,1 mm')),
                     ('tiny', _('0,1–1,0 mm')),
                     ('visible', _('1,0–10 mm')),
                     ('large', _('10–100 mm')),
                     ('huge', _('>100 mm')))

    # Fields related to file handling
    uuid = models.UUIDField(_('identificador'),
                            default=uuid.uuid4,
                            help_text=_('Identificador único universal do arquivo.'))

    file = models.FileField(upload_to=user_upload_directory,
                            default=None,
                            null=True,
                            help_text=_('Arquivo original carregado pelo usuário.'))

    # TODO: Remove max_length after migrations
    file_large = models.FileField(upload_to=user_upload_directory,
                                  default=None,
                                  null=True,
                                  max_length=200,
                                  help_text=_('Arquivo processado tamanho grande.'))

    file_medium = models.FileField(upload_to=user_upload_directory,
                                  default=None,
                                  null=True,
                                  help_text=_('Arquivo processado tamanho médio.'))

    file_small = models.FileField(upload_to=user_upload_directory,
                                  default=None,
                                  null=True,
                                  help_text=_('Arquivo processado tamanho pequeno.'))

    file_cover = models.FileField(upload_to=user_upload_directory,
                                  default=None,
                                  null=True,
                                  help_text=_('Imagem de capa do arquivo.'))

    datatype = models.CharField(_('tipo de mídia'),
                                max_length=15,
                                choices=DATATYPE_CHOICES,
                                help_text=_('Foto ou vídeo.'))

    #TODO: Field to be deprecated
    sitepath = models.FileField(_('arquivo web'),
                                default=None,
                                help_text=_('Arquivo processado para a web.'))

    #TODO: Field to be deprecated
    coverpath = models.ImageField(_('imagem de capa'),
                                  default=None,
                                  help_text=_('Imagem de capa para o arquivo processado.'))

    #TODO: Field to be deprecated
    filepath = models.CharField(_('arquivo original'),
                                max_length=200,
                                blank=True,
                                help_text=_('Caminho único para o arquivo original.'))


    # Fields related to authorship
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True,
                             on_delete=models.SET_NULL,
                             verbose_name=_('usuário do arquivo'),
                             help_text=_('Usuário que fez o upload do arquivo.'),
                             related_name='uploaded_media')

    authors = models.ManyToManyField('Person',
                                     blank=True,
                                     verbose_name=_('autores do arquivo'),
                                     help_text=_('Autores associados a este arquivo.'),
                                     related_name='media_as_author')

    specialists = models.ManyToManyField('Person',
                                         blank=True,
                                         verbose_name=_('especialistas associados'),
                                         help_text=_('Especialistas associados a este arquivo.'),
                                         related_name='media_as_specialist')

    curators = models.ManyToManyField('Person',
                                  blank=True,
                                  verbose_name=_('curadores do arquivo'),
                                  help_text=_('Curadores associados a este arquivo.'),
                                  related_name='media_as_curator')

    terms = models.BooleanField(_('termos'),
                                default=False,
                                help_text=_('Flag indicando que termos foram aceitos.'))

    license = models.CharField(_('Licença'),
                               max_length=60,
                               choices=LICENSE_CHOICES,
                               null=True,
                               blank=True,
                               help_text=_('Tipo de licença da mídia.'))

    # Fields related to media status
    metadata_error = models.BooleanField(_('Erro nos metadados'),
                                         default=False,
                                         help_text=_('Flag indicando problema nos metadados.'))

    status = models.CharField(_('status'),
                              blank=True,
                              max_length=13,
                              choices=STATUS_CHOICES,
                              default='loaded',
                              help_text=_('Status da mídia.'))

    is_public = models.BooleanField(_('público'),
                                    default=False,
                                    help_text=_('Visível para visitantes.'))

    highlight = models.BooleanField(_('destaque'),
                                    default=False,
                                    help_text=_('Imagem que merece destaque.'))

    # Date the image was created (when the photo taken or the video recorded)
    # Imported from the file metadata or manually set
    date_created = models.DateTimeField(_('data de criação'),
                                        blank=True,
                                        null=True,
                                        help_text=_('Data de criação do arquivo.'))

    # Date the image was uploaded to the website
    # Automatically set when Media instance is created
    date_uploaded = models.DateTimeField(_('data do upload'),
                                         auto_now_add=True,
                                         blank=True,
                                         null=True, #TODO: eventually remove
                                         help_text=_('Data do upload do arquivo.'))

    # Date the image was last modified
    # Automatically updated every time Media.save() is called
    date_modified = models.DateTimeField(_('data de modificação'),
                                         auto_now=True,
                                         blank=True,
                                         null=True, #TODO: eventually remove
                                         help_text=_('Data da última modificação do arquivo.'))

    # Date the image was made public in the website
    # Set manually by logic in the publishing pipeline
    date_published = models.DateTimeField(_('data de publicação'),
                                          blank=True,
                                          null=True,
                                          help_text=_('Data da publicação do arquivo.'))

    # Fields containing plain media metadata
    title = models.CharField(_('título'),
                             max_length=200,
                             default='',
                             blank=True,
                             help_text=_('Título da imagem.'))

    caption = models.TextField(_('legenda'),
                               default='',
                               blank=True,
                               help_text=_('Legenda da imagem.'))

    acknowledgments = models.TextField(_('agradecimentos'),
                               default='',
                               blank=True,
                               help_text=_('Agradecimentos da imagem.'))

    scale = models.CharField(_('escala da imagem'),
                             max_length=12,
                             blank=True,
                             choices=SCALE_CHOICES,
                             help_text=_('Classes de escala.'))

    duration = models.CharField(_('duração'),
                                max_length=20,
                                default='00:00:00',
                                blank=True,
                                help_text=_('Duração do vídeo no formato HH:MM:SS.'))

    dimensions = models.CharField(_('dimensões'),
                                  max_length=20,
                                  default='0x0',
                                  blank=True,
                                  help_text=_('Dimensões do vídeo original.'))

    geolocation = models.CharField(_('geolocalização'),
                                   default='',
                                   max_length=25,
                                   blank=True,
                                   help_text=_('Geolocalização no formato sexagesimal (S 23°48\'45" W 45°24\'27").'))

    latitude = models.CharField(_('latitude'),
                                default='',
                                max_length=25,
                                blank=True,
                                help_text=_('Latitude onde a imagem foi criada no formato decimal.'))

    longitude = models.CharField(_('longitude'),
                                 default='',
                                 max_length=25,
                                 blank=True,
                                 help_text=_('Longitude onde a imagem foi criada no formato decimal.'))

    # Fields associated with other models using Many2Many
    taxa = models.ManyToManyField('Taxon',
                                  blank=True,
                                  verbose_name=_('táxons da mídia'),
                                  help_text=_('Grupos taxonômicos associados com esta mídia.'),
                                  related_name='media')

    tags = models.ManyToManyField('Tag',
                                  blank=True,
                                  verbose_name=_('marcadores da mídia'),
                                  help_text=_('Marcadores associados com esta mídia.'),
                                  related_name='media')

    references = models.ManyToManyField('Reference',
                                        blank=True,
                                        verbose_name=_('referências da mídia'),
                                        help_text=_('Referências bibliográficas associadas com esta mídia.'),
                                        related_name='media')

    # Fields associated with other models using ForeignKey
    location = models.ForeignKey('Location',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 verbose_name=_('local'),
                                 help_text=_('Localidade mostrada na imagem ou local de coleta.'))

    city = models.ForeignKey('City',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name=_('cidade'),
                             help_text=_('Cidade mostrada na imagem ou cidade de coleta.'))

    state = models.ForeignKey('State',
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              verbose_name=_('estado'),
                              help_text=_('Estado mostrado na imagem ou estado de coleta.'))

    country = models.ForeignKey('Country',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                verbose_name=_('país'),
                                help_text=_('País mostrado na imagem (ou país de coleta).'))

    # Fields associated with full text search
    search_vector = SearchVectorField(_('vetor de busca'),
                                      null=True,
                                      help_text=_('Campo que guarda o vetor de busca.'))

    # Fields required for historical reasons
    old_image = models.PositiveIntegerField(default=0,
                                            blank=True,
                                            help_text=_('ID da imagem no antigo modelo.'))

    old_video = models.PositiveIntegerField(default=0,
                                            blank=True,
                                            help_text=_('ID do vídeo no antigo modelo.'))

    def __str__(self):
        return 'ID={} {} ({}) {}'.format(self.id, self.title, self.datatype, self.status)

    def get_absolute_url(self):
        return reverse('media_url', args=[str(self.id)])

    def normalize_title(self, title):
        '''Capitalize first letter, remove full stop from the end.'''
        #TODO: Move function to utils
        # Avoid None types in titles (shouldn't exist...)
        if title is None:
            return ''
        # Strip extra white spaces
        stripped_title = title.strip()
        # In case len(title) < 2 or fails for some other reason
        try:
            # Capitalize first, remove full stop
            return stripped_title[0].upper() + stripped_title[1:].rstrip('.')
        except:
            # Return the original title, but stripped
            return stripped_title

    def normalize_caption(self, caption):
        '''Capitalize first letter, ensure full stop at the end.'''
        #TODO: Move function to utils
        # Avoid None types in captions (shouldn't exist...)
        if caption is None:
            return ''
        # Strip extra white spaces
        stripped_caption = caption.strip()
        # In case len(caption) < 2 or fails for some other reason
        try:
            # Capitalize first, add full stop
            return stripped_caption[0].upper() + stripped_caption[1:].rstrip('.') + '.'
        except:
            return stripped_caption

    def resize_files(self):
        '''Calls for the resizing of media files.'''
        self.create_resized_files('cover')
        self.create_resized_files('large')
        self.create_resized_files('medium')
        self.create_resized_files('small')

    def create_resized_files(self, size):
        '''Resize media files to a pre-defined dimension.

        Options: large, medium, small, cover.

        See MEDIA_DEFAULTS for details.
        '''

        # Delete file from resized field
        field = getattr(self, f'file_{size}')
        field.delete()

        # Get dimension and quality values
        dimension = settings.MEDIA_DEFAULTS[self.datatype][size]['dimension']
        quality = settings.MEDIA_DEFAULTS[self.datatype][size]['quality']
        extension = settings.MEDIA_DEFAULTS[self.datatype]['extension']

        # Force photo extension for video cover image
        if size == 'cover':
            extension = settings.MEDIA_DEFAULTS['photo']['extension']

        # Save original file to resized field using new name
        field.save(content=self.file, name=f'{self.uuid}_{size}.{extension}')

        # Resize media
        if self.datatype == 'photo':
            resized = resize_image(field.path, dimension, quality)
        elif self.datatype == 'video':
            if size == 'cover':
                resized = extract_video_cover(self.file.path, dimension,
                                              field.path)
            else:
                resized = resize_video(self.file.path, dimension,
                                       quality, field.path)

        # Return True/False for convenience
        return resized

    def get_ancestors_vector(self):
        taxa = self.taxa.all()
        if not taxa:
            return ''
        ancestors = taxa[0].get_ancestors()
        for taxon in taxa:
            ancestors = ancestors | taxa.get_ancestors()
        return ' '.join(ancestors.values_list('name', flat=True))

    def get_field_name_or_empty_string(self, field):
        if field:
            name = field.name
        else:
            name = ''
        return name

    def update_search_vector(self):
        '''Collect metadata and update the search vector field.'''

        # Fetch associated authors, taxa, tags, curators, etc
        authors = ' '.join(self.authors.values_list('name', flat=True))
        curators = ' '.join(self.curators.values_list('name', flat=True))
        specialists = ' '.join(self.specialists.values_list('name', flat=True))
        taxa = ' '.join(self.taxa.values_list('name', flat=True))
        tags_pt_br = ' '.join(self.tags.values_list('name_pt_br', flat=True))
        tags_en = ' '.join(self.tags.values_list('name_en', flat=True))

        location = self.get_field_name_or_empty_string(self.location)
        city = self.get_field_name_or_empty_string(self.city)
        state = self.get_field_name_or_empty_string(self.state)
        country = self.get_field_name_or_empty_string(self.country)

        ancestors = self.get_ancestors_vector()

        # Build SearchVectorField using Value (StringAgg or other approaches don't work)
        self.search_vector = (
                SearchVector('title_pt_br', weight='A', config='portuguese_unaccent') +
                SearchVector('title_en', weight='A', config='english') +
                SearchVector('caption_pt_br', weight='A', config='portuguese_unaccent') +
                SearchVector('caption_en', weight='A', config='english') +
                SearchVector('acknowledgments_pt_br', weight='D', config='portuguese_unaccent') +
                SearchVector('acknowledgments_en', weight='D', config='english') +
                SearchVector(Value(authors), weight='B', config='portuguese_unaccent') +
                SearchVector(Value(authors), weight='B', config='english') +
                SearchVector(Value(curators), weight='C', config='portuguese_unaccent') +
                SearchVector(Value(curators), weight='C', config='english') +
                SearchVector(Value(specialists), weight='D', config='portuguese_unaccent') +
                SearchVector(Value(specialists), weight='D', config='english') +
                SearchVector(Value(taxa), weight='B', config='portuguese_unaccent') +
                SearchVector(Value(taxa), weight='B', config='english') +
                SearchVector(Value(ancestors), weight='C', config='portuguese_unaccent') +
                SearchVector(Value(ancestors), weight='C', config='english') +
                SearchVector(Value(tags_pt_br), weight='B', config='portuguese_unaccent') +
                SearchVector(Value(tags_en), weight='B', config='english') +
                SearchVector(Value(location), weight='C', config='portuguese_unaccent') +
                SearchVector(Value(location), weight='C', config='english') +
                SearchVector(Value(city), weight='C', config='portuguese_unaccent') +
                SearchVector(Value(city), weight='C', config='english') +
                SearchVector(Value(state), weight='D', config='portuguese_unaccent') +
                SearchVector(Value(state), weight='D', config='english') +
                SearchVector(Value(country), weight='D', config='portuguese_unaccent') +
                SearchVector(Value(country), weight='D', config='english')
                )


        return self.search_vector

    def latlng_to_geo(self):
        # Blank fields if partial missing data
        # Avoids convert string to float error
        if not self.latitude or not self.longitude:
            self.latitude = ''
            self.longitude = ''
            self.geolocation = ''
        else:
            # Convert values to float
            latitude_dec = float(self.latitude)
            longitude_dec = float(self.longitude)

            # Set default references
            latitude_ref = 'N'
            longitude_ref = 'E'
            if latitude_dec < 0:
                latitude_ref = 'S'
            if longitude_dec < 0:
                longitude_ref = 'W'

            # Get absolute latitude and longitude values
            latitude_dec = abs(latitude_dec)
            longitude_dec = abs(longitude_dec)

            # Define latitude degrees, minutes, and seconds
            lat_deg = int(latitude_dec)
            lat_min_dec = (latitude_dec - lat_deg) * 60
            lat_min = int(lat_min_dec)
            lat_sec = int((lat_min_dec - lat_min) * 60)
            latitude_str = f'{latitude_ref} {lat_deg:02}°{lat_min:02}\'{lat_sec:02}"'

            # Define longitude degrees, minutes, and seconds
            lon_deg = int(longitude_dec)
            lon_min_dec = (longitude_dec - lon_deg) * 60
            lon_min = int(lon_min_dec)
            lon_sec = int((lon_min_dec - lon_min) * 60)
            longitude_str = f'{longitude_ref} {lon_deg:02}°{lon_min:02}\'{lon_sec:02}"'

            self.geolocation = f'{latitude_str} {longitude_str}'

    def update_metadata(self):

        self.latlng_to_geo()

        tags = []
        for tag in self.tags.all():
            tags.append(tag.name)

        sources = []
        for source in self.specialists.all():
            sources.append(source.name)

        authors = []
        for author in self.authors.all():
            authors.append(author.name)

        headlines = []
        for headline in self.taxa.all():
            headlines.append(headline.name)

        credits = []
        for credit in self.references.all():
            credits.append(credit.name)

        city = self.city
        if city != None:
            city = city.name
        
        state = self.state
        if state != None:
            state = state.name
        
        country = self.country
        if country != None:
            country = country.name

        metadata = {
            'headline': ', '.join(headlines),
            'instructions': self.scale,
            'source': ', '.join(sources),
            'credit': ', '.join(credits),
            'license': self.license,
            'authors': ', '.join(authors),
            'keywords': tags,
            'description_pt': self.caption_pt_br,
            'description_en': self.caption_en,
            'title_pt': self.title_pt_br,
            'title_en': self.title_en,
            'city': city,
            'state': state,
            'country': country,
            'gps': self.geolocation

        }

        #TODO: Fix writing the metadata to videos
        # Workaround logic to prevent errors on publishing videos
        if self.datatype == 'photo':
            to_write = [self.file_large, self.file_medium, self.file_small,
                        self.file_cover, self.sitepath, self.coverpath]
            for file in to_write:
                meta_instance = Metadata(file.path)
                meta_instance.insert_metadata(metadata)
        elif self.datatype == 'video':
            to_write = [self.file_cover, self.coverpath]
            for file in to_write:
                meta_instance = Metadata(file.path)
                meta_instance.insert_metadata(metadata)

    class Meta:
        verbose_name = _('arquivo')
        verbose_name_plural = _('arquivos')
        ordering = ['id']
        indexes = (GinIndex(fields=['search_vector']),)


class ModifiedMedia(Media):
    media = models.ForeignKey('Media', on_delete=models.CASCADE, related_name='modified_media',
            verbose_name=_('mídia original'), help_text=_('Mídia original com metadados antes das modificações.'))
    altered_by_author = models.BooleanField(_('alterada pelo autor'),
            default=True,
            help_text=_('Flag indicando quem fez a alteração na mídia.'))
    modification_person = models.ForeignKey('Person', null=True, on_delete=models.CASCADE, related_name='modified_medias',
            verbose_name=_('Pessoa da mídia modificada'), help_text=_('Pessoa que realizou alterações na mídia publicada'))

    class Meta:
        verbose_name = _("mídia modificada")
        verbose_name_plural = _("mídias modificadas")

class Person(models.Model):
    name = models.CharField(_('nome'), max_length=200, blank=True,
            help_text=_('Nome do autor.'))
    slug = models.SlugField(_('slug'), max_length=200, unique=True, blank=True,
            help_text=_('Slug do nome do autor.'))
    orcid = models.CharField('Orcid', blank=True, null=True, max_length=16)
    idlattes = models.CharField('IDLattes', blank=True, null=True, max_length=16)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    user_cifonauta = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
            verbose_name=_('Usuário relacionado'))

    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Person.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_url', args=[self.slug])

    def get_absolute_url_author(self):
        return reverse('author_url', args=[self.slug])

    def get_absolute_url_specialist(self):
        return reverse('specialist_url', args=[self.slug])

    def get_absolute_url_curator(self):
        return reverse('curator_url', args=[self.slug])

    class Meta:
        verbose_name = _('pessoa')
        verbose_name_plural = _('pessoas')
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True,
            help_text=_('Nome do marcador.'))
    slug = models.SlugField(_('slug'), max_length=64, default='', blank=True,
            help_text=_('Slug do nome do marcador.'))
    description = models.TextField(_('descrição'), default='', blank=True,
            help_text=_('Descrição do marcador.'))
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
            null=True, blank=True, related_name='tags',
            verbose_name=_('categorias'),
            help_text=_('Categoria associada a este marcador.'))

    def __str__(self):
        return f'{self.category}: {self.name}'

    def get_absolute_url(self):
        return reverse('tag_url', args=[self.slug])

    class Meta:
        verbose_name = _('marcador')
        verbose_name_plural = _('marcadores')
        ordering = ['category', 'name']


class Category(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True,
            help_text=_('Nome da categoria de marcadores.'))
    slug = models.SlugField(_('slug'), max_length=64, default='', blank=True,
            help_text=_('Slug do nome da categoria de marcadores.'))
    description = models.TextField(_('descrição'), default='', blank=True,
            help_text=_('Descrição da categoria de marcadores.'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('categoria')
        verbose_name_plural = _('categorias')
        ordering = ['name']


class Taxon(MPTTModel):
    name = models.CharField(_('nome'), max_length=256, unique=True,
            help_text=_('Nome do táxon.'))
    slug = models.SlugField(_('slug'), max_length=256, blank=True,
            help_text=_('Slug do nome do táxon.'))
    rank = models.CharField(_('rank'), max_length=256, blank=True,
            help_text=_('Ranking taxonômico do táxon.'))
    aphia = models.PositiveIntegerField(null=True, blank=True,
            help_text=_('AphiaID, o identificador do táxon no WoRMS.'))
    authority = models.CharField(_('autoridade'), max_length=256, blank=True, null=True,
            help_text=_('Autoridade do táxon.'))
    citation = models.TextField(_('citação'), default='', blank=True, help_text=_('Citação do táxon.'))
    status = models.CharField(_('status'), max_length=256, blank=True, null=True,
            help_text=_('Status do táxon.'))
    is_valid = models.BooleanField(_('válido'), default=False,
            help_text=_('Status do táxon.'))
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, blank=True,
            null=True, related_name='children', verbose_name=_('pai'),
            help_text=_('Táxon pai deste táxon.'))
    valid_taxon = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
            null=True, related_name='synonyms', verbose_name=_('táxon válido'),
            help_text=_('Sinônimo válido deste táxon.'))
    timestamp = models.DateTimeField(_('data de modificação'), auto_now=True,
            blank=True, null=True, help_text=_('Data da última modificação do arquivo.'))

    def __str__(self):
        return f'{self.name} [id={self.id}]'

    def get_absolute_url(self):
        return reverse('taxon_url', args=[self.slug])

    def get_total_media_count(self):
        '''Get the total media count the taxon and its descendants.'''
        #TODO: Too costly to call every time, save as a field?
        taxon_and_descendants = self.get_descendants(include_self=True)
        media_count = Media.objects.filter(taxa__in=taxon_and_descendants).distinct().count()
        return media_count

    def get_curations(self):
        '''Retrieve set of curations associated with ancestors.'''
        ancestors = self.get_ancestors(include_self=True)
        curations = Curation.objects.filter(taxa__in=ancestors).distinct()
        return curations

    def fetch_worms_data(self):
        '''Fetch WoRMS metadata and apply for current taxon.'''
        #TODO: Can't do that... circular import. Keep this in the view for now.
        #taxon_updater = TaxonUpdater(self.name)

    def update_curations(self):
        '''Add taxon to standard curations.

        These are:
            - id=1, 'Cifonauta'
            - id=2, 'Sem táxons',
            - id=3, 'Presente no WoRMS'
            - id=4, 'Ausente do WoRMS',
        '''

        # Add every taxon to the "all taxa" curation Cifonauta
        self.curations.add(1)

        # Add or remove from "not in WoRMS" curation
        if self.aphia:
            self.curations.add(3)
            self.curations.remove(4)
        else:
            self.curations.add(4)
            self.curations.remove(3)

    def synchronize_media(self):
        '''Synchronize media between valid and invalid taxa.'''
        pass

    @staticmethod
    def get_taxon_and_parents(qs):
        '''Returns all parents and current taxon from a QuerySet of taxa.'''
        tree_list = {}
        query = Q()

        for node in qs.all():
            if node.tree_id not in tree_list:
                tree_list[node.tree_id] = []

            parent = node.parent.pk if node.parent is not None else None,

            if parent not in tree_list[node.tree_id]:
                tree_list[node.tree_id].append(parent)

                query |= Q(lft__lt=node.lft, rght__gt=node.rght, tree_id=node.tree_id)
            query |= Q(id=node.id)
        return Taxon.objects.filter(query)
    
    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('táxon')
        verbose_name_plural = _('táxons')
        ordering = ['name']


class Location(models.Model):
    name = models.CharField(_('nome'), max_length=64,
            help_text=_('Nome da localidade.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True,
            help_text=_('Slug do nome da localidade.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('location_url', args=[self.slug])

    class Meta:
        verbose_name = _('local')
        verbose_name_plural = _('locais')
        ordering = ['name']


class City(models.Model):
    name = models.CharField(_('nome'), max_length=64,
            help_text=_('Nome da cidade.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True,
            help_text=_('Slug do nome da cidade.'))
    state = models.ForeignKey('State', on_delete=models.CASCADE, 
            blank=True, null=True, 
            verbose_name=_('estado'), help_text=_('Estado na qual a cidade pertence.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('city_url', args=[self.slug])

    class Meta:
        verbose_name = _('cidade')
        verbose_name_plural = _('cidades')
        ordering = ['name']


class State(models.Model):
    name = models.CharField(_('nome'), max_length=64,
            help_text=_('Nome do estado.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True,
            help_text=_('Slug do nome do estado.'))
    country = models.ForeignKey('Country', on_delete=models.CASCADE, 
            blank=True, null=True, 
            verbose_name=_('país'), help_text=_('Pais na qual o estado pertence.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('state_url', args=[self.slug])

    class Meta:
        verbose_name = _('estado')
        verbose_name_plural = _('estados')
        ordering = ['name']


class Country(models.Model):
    name = models.CharField(_('nome'), max_length=64,
            help_text=_('Nome do país.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True,
            help_text=_('Slug do nome do país.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('country_url', args=[self.slug])

    class Meta:
        verbose_name = _('país')
        verbose_name_plural = _('países')
        ordering = ['name']


class Reference(models.Model):
    name = models.CharField(_('nome'), max_length=100, unique=True,
            help_text=_('Nome chave no estilo bibkey (e.g., Vieira2012-nt).'))
    slug = models.SlugField(_('slug'), max_length=100, blank=True,
            help_text=_('Slug do nome chave da referência.'))
    citation = models.TextField(_('citação'), blank=True,
            help_text=_('Citação formatada da referência.'))
    doi = models.CharField('doi', max_length=40, blank=True, help_text=_('DOI da referência'))

    def __str__(self):
        if self.doi:
            return f'{self.name} [DOI:{self.doi}]'
        else:
            return f'{self.name} [sem DOI]'

    def generate_name(self):
        '''Generate name from APA-style citation.'''
        if not self.citation:
            return ''

        # Extract the last name of the first author
        # last_name_match = re.match(r'^([^,]+)', self.citation)
        # last_name_match = re.match(r'^([A-Za-z]+(?:[-\s][A-Za-z]+)*)', self.citation)
        last_name_match = re.match(r'^([\wÀ-ÖØ-öø-ÿ]+(?:[-\s][\wÀ-ÖØ-öø-ÿ]+)*)', self.citation)
        last_name = last_name_match.group(1) if last_name_match else ''

        # Extract the publication year
        publication_year_match = re.search(r'\((\d{4})\)', self.citation)
        publication_year = publication_year_match.group(1) if publication_year_match else ''
        # Stop if empty
        if not last_name or not publication_year:
            return ''

        # Generate a two-letter random suffix
        suffix = ''.join(random.choice(string.ascii_lowercase) for n in range(2))

        # Construct the bibkey-like name
        bibkey = f'{last_name}{publication_year}-{suffix}'
        bibkey = bibkey.replace(' ', '-')
        return bibkey

    def get_absolute_url(self):
        return reverse('reference_url', args=[self.slug])

    class Meta:
        verbose_name = _('referência')
        verbose_name_plural = _('referências')
        ordering = ['name']


class Tour(models.Model):
    name = models.CharField(_('nome'), max_length=100, unique=True,
            help_text=_('Nome do tour.'))
    slug = models.SlugField(_('slug'), max_length=100, blank=True,
            help_text=_('Slug do nome do tour.'))
    description = models.TextField(_('descrição'), blank=True,
            help_text=_('Descrição do tour.'))
    is_public = models.BooleanField(_('público'), default=False,
            help_text=_('Informa se o tour está visível para visitantes anônimos.'))
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True,
            help_text=_('Data de publicação do tour no Cifonauta.'))
    timestamp = models.DateTimeField(_('data de modificação'), auto_now=True,
            help_text=_('Data da última modificação do tour.'))
    media = models.ManyToManyField('Media', blank=True,
            verbose_name=_('arquivos'), help_text=_('Arquivos associados a este tour.'))
    references = models.ManyToManyField('Reference', blank=True,
            verbose_name=_('referências'), help_text=_('Referências associadas a este tour.'))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
            verbose_name=_('criador'), help_text=_('Usuário criador do tour.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tour_url', args=[self.slug])

    class Meta:
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        ordering = ['name']


class Stats(models.Model):
    '''Gather database statistics.'''
    site = models.CharField(_('website'), max_length=100, unique=True,
            help_text=_('Nome do sítio.'))
    photos = models.PositiveIntegerField(default=0,
            help_text=_('Número total de fotos públicas.'))
    videos = models.PositiveIntegerField(default=0,
            help_text=_('Número total de vídeos públicos.'))
    tags = models.PositiveIntegerField(default=0,
            help_text=_('Número total de marcadores.'))
    species = models.PositiveIntegerField(default=0,
            help_text=_('Número total de espécies.'))
    locations = models.PositiveIntegerField(default=0,
            help_text=_('Número total de localidades.'))

    def __str__(self):
        return '{}: {} fotos / {} vídeos / {} marcadores / {} espécies / {} locais'.format(
                self.site, self.photos, self.videos, self.tags, self.species, self.locations)

    class Meta:
        verbose_name = _('estatísticas')
        verbose_name_plural = _('estatísticas')

