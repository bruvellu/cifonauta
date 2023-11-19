# -*- coding: utf-8 -*-

import os
import shutil
import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Q, Value
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from mptt.models import MPTTModel


class Curadoria(models.Model):
    name = models.CharField(max_length=50)
    taxons = models.ManyToManyField('Taxon', blank=True)
    specialists = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='curatorship_specialist', 
            blank=True, verbose_name=_('especialistas'), help_text=_('Especialistas da curadoria.'))
    curators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='curatorship_curator',
            blank=True, verbose_name=_('curadores'), help_text=_('Curadores da curadoria.'))

    def __str__(self):
        return self.name

class ModifiedMedia(models.Model):
    LICENSE_CHOICES = (('cc0', _('CC0 (Domínio Público)')),
                       ('cc_by', _('CC BY (Atribuição)')),
                       ('cc_by_sa', _('CC BY-SA (Atribuição-CompartilhaIgual)')),
                       ('cc_by_nd', _('CC BY-ND (Atribuição-SemDerivações)')),
                       ('cc_by_nc', _('CC BY-NC (Atribuição-NãoComercial)')),
                       ('cc_by_nc_sa', _('CC BY-NC-SA (AtribuiçãoNãoComercial-CompartilhaIgual)')),
                       ('cc_by_nc_nd', _('CC BY-NC-ND (Atribuição-SemDerivações-SemDerivados)')),)
    
    title = models.CharField(_('título'), max_length=200, default='',
            blank=True, help_text=_('Título da imagem.'))
    caption = models.TextField(_('legenda'), default='', blank=True,
            help_text=_('Legenda da imagem.'))
    media = models.OneToOneField('Media', on_delete=models.CASCADE, related_name='modified_media',
            verbose_name=_('mídia modificada'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            on_delete=models.SET_NULL, verbose_name=_('usuário do arquivo'),
            help_text=_('Usuário que fez o upload do arquivo.'),
            related_name='modified_media')
    authors = models.ManyToManyField('Person', blank=True,
            verbose_name=_('autores'), help_text=_('Coautor(es) da mídia'), related_name='modified_media_authors')
    taxa = models.ManyToManyField('Taxon', related_name="modified_media_taxons", verbose_name=_('táxons'), help_text=_('Táxons pertencentes à mídia.'), blank=True)
    date = models.DateTimeField(_('data'), null=True,
            help_text=_('Data de criação da imagem.'))
    location = models.ForeignKey('Location', on_delete=models.SET_NULL,
            null=True, blank=True, verbose_name=_('local'),
            help_text=_('Localidade mostrada na imagem (ou local de coleta).'))
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, verbose_name=_('cidade'),
            help_text=_('Cidade mostrada na imagem (ou cidade de coleta).'))
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, verbose_name=_('estado'),
            help_text=_('Estado mostrado na imagem (ou estado de coleta).'))
    country = models.ForeignKey('Country', on_delete=models.SET_NULL,
            null=True, verbose_name=_('país'),
            help_text=_('País mostrado na imagem (ou país de coleta).'))
    geolocation = models.CharField(_('geolocalização'), default='',
            max_length=25, blank=True,
        help_text=_('Geolocalização da imagem no formato decimal.'))
    license = models.CharField(_('Licença'),
                               max_length=60,
                               choices=LICENSE_CHOICES,
                               default='cc0',
                               help_text=_('Tipo de licença da mídia.'))
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('mídia modificada')
        verbose_name_plural = _('mídias modificadas')
    
def save_file(instance, filename):
    return os.path.join(f'uploads/{instance.user.username}', filename)

def save_cover(instance, filename):
    return os.path.join(f'{instance.user.username}', filename)

class Media(models.Model):
    '''Table with metadata for photo and video files.'''

    # Pre-defined choices
    STATUS_CHOICES = (('loaded', _('Carregada')),
                      ('not_edited', _('Não Editado')),
                      ('to_review', _('Para Revisão')),
                      ('published', _('Publicado')),)

    LICENSE_CHOICES = (('cc0', _('CC0 (Domínio Público)')),
                       ('cc_by', _('CC BY (Atribuição)')),
                       ('cc_by_sa', _('CC BY-SA (Atribuição-CompartilhaIgual)')),
                       ('cc_by_nd', _('CC BY-ND (Atribuição-SemDerivações)')),
                       ('cc_by_nc', _('CC BY-NC (Atribuição-NãoComercial)')),
                       ('cc_by_nc_sa', _('CC BY-NC-SA (AtribuiçãoNãoComercial-CompartilhaIgual)')),
                       ('cc_by_nc_nd', _('CC BY-NC-ND (Atribuição-SemDerivações-SemDerivados)')),)

    # Fields related to file handling
    file = models.FileField(upload_to=save_file,
                            default=None,
                            null=True,
                            help_text=_('Arquivo carregado pelo usuário.'))

    filepath = models.CharField(_('arquivo original'),
                                max_length=200,
                                help_text=_('Caminho único para o arquivo original.'))

    sitepath = models.FileField(_('arquivo web'),
                                upload_to=save_cover,
                                default=None,
                                help_text=_('Arquivo processado para a web.'))

    coverpath = models.ImageField(_('imagem de capa'),
                                  upload_to=save_cover,
                                  default=None,
                                  help_text=_('Imagem de capa para o arquivo processado.'))

    datatype = models.CharField(_('tipo de mídia'),
                                max_length=15,
                                help_text=_('Tipo de mídia.'))

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
                               default='cc0',
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
    # date_uploaded = models.DateTimeField(_('data do upload'),
                                         # auto_now_add=True,
                                         # blank=True,
                                         # null=True,
                                         # help_text=_('Data do upload do arquivo.'))
    # Date the image was last modified
    # Automatically updated every time Media.save() is called
    # date_modified = models.DateTimeField(_('data de modificação'),
                                         # auto_now=True,
                                         # blank=True,
                                         # null=True,
                                         # help_text=_('Data da última modificação do arquivo.'))
    # Date the image was made public in the website
    # Set manually by logic in the publishing pipeline
    date_published = models.DateTimeField(_('data de publicação'),
                                          blank=True,
                                          null=True,
                                          help_text=_('Data da publicação do arquivo.'))

    # Date fields to be deprecated
    date = models.DateTimeField(_('data'),
                                null=True,
                                help_text=_('Data de criação da imagem.'))

    pub_date = models.DateTimeField(_('data de publicação'),
                                    blank=True,
                                    default=timezone.now,
                                    help_text=_('Data de publicação da imagem no Cifonauta.'))

    timestamp = models.DateTimeField(_('data de modificação'),
                                     blank=True,
                                     default=timezone.now,
                                     help_text=_('Data da última modificação do arquivo.'))

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
                                   help_text=_('Geolocalização da imagem no formato decimal.'))
    latitude = models.CharField(_('latitude'),
                                default='',
                                max_length=25,
                                blank=True,
                                help_text=_('Latitude onde a imagem foi criada.'))
    longitude = models.CharField(_('longitude'),
                                 default='',
                                 max_length=25,
                                 blank=True,
                                 help_text=_('Longitude onde a imagem foi criada.'))

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

    def is_video(self):
        _, extension = os.path.splitext(self.file.name)
        return True if extension in settings.VIDEO_EXTENSIONS else False

    def update_search_vector(self):
        '''Collect metadata and update the search vector field.'''

        # Update search vector field on save
        #TODO: Make a function to save values to a dictionary, take care of Empty/None/Null values
        #TODO: Make a function to populate the search_vector with these saved values
        #TODO: Replace here just with the calls for the functions above
        self.search_vector = SearchVector('title_pt_br', weight='A', config='portuguese_unaccent') + \
                             SearchVector('title_en', weight='A', config='english') + \
                             SearchVector('caption_pt_br', weight='B', config='portuguese_unaccent') + \
                             SearchVector('caption_en', weight='B', config='english')

        return self.search_vector

        # self.search_vector = SearchVector('title_pt_br', weight='A', config='portuguese_unaccent') + \
                             # SearchVector('title_en', weight='A', config='english') + \
                             # SearchVector('caption_pt_br', weight='B', config='portuguese_unaccent') + \
                             # SearchVector('caption_en', weight='B', config='english')
                             # SearchVector(StringAgg('taxon__name', delimiter=' '), weight='B') + \
                             # SearchVector(StringAgg('person__name', delimiter=' '), weight='B') + \
                             # SearchVector(StringAgg('tag__name_pt_br', delimiter=' '), weight='C', config='portuguese_unaccent') + \
                             # SearchVector(StringAgg('tag__name_en', delimiter=' '), weight='C', config='english') + \
                             # SearchVector('location__name', weight='D') + \
                             # SearchVector('city__name', weight='D') + \
                             # SearchVector('state__name', weight='D') + \
                             # SearchVector('country__name', weight='D')


    def get_size(self):
        '''Returns tag from size category, if any.'''
        size_query = self.tags.filter(category__slug='tamanho')
        if size_query:
            size = size_query[0]
        else:
            size = ''
        return size

    class Meta:
        verbose_name = _('arquivo')
        verbose_name_plural = _('arquivos')
        ordering = ['id']
        indexes = (GinIndex(fields=['search_vector']),)


class Person(models.Model):
    name = models.CharField(_('nome'), max_length=200, unique=True, blank=True,
            help_text=_('Nome do autor.'))
    slug = models.SlugField(_('slug'), max_length=200, unique=True, blank=True,
            help_text=_('Slug do nome do autor.'))
    orcid = models.CharField('Orcid', blank=True, null=True, max_length=16)
    idlattes = models.CharField('IDLattes', blank=True, null=True, max_length=16)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    user_cifonauta = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
            verbose_name=_('Usuário relacionado'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_url', args=[self.slug])

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
        return self.name

    def get_absolute_url(self):
        return reverse('tag_url', args=[self.slug])

    class Meta:
        verbose_name = _('marcador')
        verbose_name_plural = _('marcadores')
        ordering = ['name']


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
    status = models.CharField(_('status'), max_length=256, blank=True, null=True,
            help_text=_('Status do táxon.'))
    is_valid = models.BooleanField(_('válido'), default=False,
            help_text=_('Status do táxon.'))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
            null=True, related_name='children', verbose_name=_('pai'),
            help_text=_('Táxon pai deste táxon.'))
    valid_taxon = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
            null=True, related_name='synonyms', verbose_name=_('táxon válido'),
            help_text=_('Sinônimo válido deste táxon.'))
    timestamp = models.DateTimeField(_('data de modificação'), auto_now=True,
            blank=True, null=True, help_text=_('Data da última modificação do arquivo.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('taxon_url', args=[self.slug])

    @staticmethod
    def get_taxon_and_parents(qs):
        '''Returns all parents and current taxon from a QuerySet of taxons.'''
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
    name = models.CharField(_('nome'), max_length=64, unique=True,
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
    name = models.CharField(_('nome'), max_length=64, unique=True,
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
    name = models.CharField(_('nome'), max_length=64, unique=True,
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
    name = models.CharField(_('nome'), max_length=64, unique=True,
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
            help_text=_('Identificador da referência (Mendeley ID).'))
    slug = models.SlugField(_('slug'), max_length=100, blank=True,
            help_text=_('Slug do identificar da referência.'))
    citation = models.TextField(_('citação'), blank=True,
            help_text=_('Citação formatada da referência.'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reference_url', args=[self.slug])

    class Meta:
        verbose_name = _('referência')
        verbose_name_plural = _('referências')
        ordering = ['-citation']


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


# # Create citation with bibkey
# models.signals.pre_save.connect(citation_pre_save, sender=Reference)

# # Delete file from folder when the media is deleted on website
# models.signals.pre_delete.connect(delete_file_from_folder, sender=Media)

# # Get taxons descendents when creating a curatorship
# models.signals.m2m_changed.connect(get_taxons_descendants, sender=Curadoria.taxons.through)
