# -*- coding: utf-8 -*-

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel
from meta.signals import *

from django.db.models import Q
from django.contrib.auth.models import Group
import uuid
import os
from django.conf import settings
from django.utils import timezone
import shutil


class UserPreRegistration(models.Model):
    first_name = models.CharField('Primeiro Nome', null=True, max_length=50)
    last_name = models.CharField('Último Nome', null=True, max_length=50)
    orcid = models.CharField('Orcid', null=True, max_length=16)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Curadoria(models.Model):
    name = models.CharField(max_length=50)
    taxons = models.ManyToManyField('Taxon', blank=True)
    specialists = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='curatorship_specialist', 
            blank=True, verbose_name=_('especialistas'), help_text=_('Especialistas da curadoria.'))
    curators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='curatorship_curator',
            blank=True, verbose_name=_('curadores'), help_text=_('Curadores da curadoria.'))

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    print("UPLOAD")
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    
    return os.path.join('uploads', random_filename)


class Media(models.Model):
    '''Table containing both image and video files.'''

    id = models.AutoField(primary_key=True)

    # New fields
    file = models.FileField(upload_to=upload_to, default=None, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
            verbose_name=_('autor'), help_text=_('Autor da mídia.'), related_name='author')
    co_author = models.CharField(max_length=256, blank=True, verbose_name=_('coautor'), help_text=_('Coautor(es) da mídia separados por ";"'))
    """ co_author = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, 
            verbose_name=_('coautor'), help_text=_('Coautor(es) da mídia'), related_name='co_author') """
    STATUS_CHOICES = (
        ('not_edited', 'Não Editado'),
        ('to_review', 'Para Revisão'),
        ('published', 'Publicado'),
    )
    status = models.CharField(_('status'), blank=True, max_length=13, choices=STATUS_CHOICES, 
            default='not_edited', help_text=_('Status da mídia.'))
    has_taxons = models.CharField(_('tem táxons'), help_text=_('Mídia tem táxons.'),
            choices=(('True', 'Sim'), ('False', 'Não')), default='False')
    taxons = models.ManyToManyField('Taxon', related_name="taxons", verbose_name=_('táxons'), blank=True)
    
    #License
    LICENSE_CHOICES = (
        ('cc0', 'CC0 (Domínio Público)'),
        ('cc_by', 'CC BY (Atribuição)'),
        ('cc_by_sa', 'CC BY-SA (Atribuição-CompartilhaIgual)'),
        ('cc_by_nd', 'CC BY-ND (Atribuição-SemDerivações)'),
        ('cc_by_nc', 'CC BY-NC (Atribuição-NãoComercial)'),
        ('cc_by_nc_sa', 'CC BY-NC-SA (AtribuiçãoNãoComercial-CompartilhaIgual)'),
        ('cc_by_nc_nd', ' CC BY-NC-ND (Atribuição-SemDerivações-SemDerivados)')
    )
    license = models.CharField(_('Licença'), max_length=60, choices=LICENSE_CHOICES, default='cc0',
        help_text=_('Tipo de licença que a mídia terá'))
    
    credit = models.CharField(_('Referências Bibliográficas'), blank=True, help_text=_('Referências bibliográficas relacionadas com a imagem.'))

    # File
    filepath = models.CharField(_('arquivo original.'), max_length=200, help_text=_('Caminho único para arquivo original.'))
    sitepath = models.FileField(_('arquivo web.'),
            help_text=_('Arquivo processado para a web.'))
    coverpath = models.ImageField(_('amostra do arquivo.'),
            help_text=_('Imagem de amostra do arquivo processado.'))
    datatype = models.CharField(_('tipo de mídia'), max_length=15,
            help_text=_('Tipo de mídia.'))
    timestamp = models.DateTimeField(_('data de modificação'), blank=True, default=timezone.now,
            help_text=_('Data da última modificação do arquivo.'))

    # Website
    old_image = models.PositiveIntegerField(default=0, blank=True,
            help_text=_('ID da imagem no antigo modelo.'))
    old_video = models.PositiveIntegerField(default=0, blank=True,
            help_text=_('ID do vídeo no antigo modelo.'))
    highlight = models.BooleanField(_('destaque'), default=False,
            help_text=_('Imagem que merece destaque.'))
    is_public = models.BooleanField(_('público'), default=False,
            help_text=_('Visível para visitantes.'))
    pub_date = models.DateTimeField(_('data de publicação'), blank=True, default=timezone.now,
            help_text=_('Data de publicação da imagem no Cifonauta.'))

    # Metadata
    title = models.CharField(_('título'), max_length=200, default='',
            blank=True, help_text=_('Título da imagem.'))
    caption = models.TextField(_('legenda'), default='', blank=True,
            help_text=_('Legenda da imagem.'))
    date = models.DateTimeField(_('data'), null=True, blank=True,
            help_text=_('Data de criação da imagem.'))
    duration = models.CharField(_('duração'), max_length=20,
            default='00:00:00', blank=True,
            help_text=_('Duração do vídeo no formato HH:MM:SS.'))
    dimensions = models.CharField(_('dimensões'), max_length=20, default='0x0',
            blank=True, help_text=_('Dimensões do vídeo original.'))
    size = models.CharField(_('tamanho'), max_length=10, default='none',
            blank=True, help_text=_('Classe de tamanho.'))
    geolocation = models.CharField(_('geolocalização'), default='',
            max_length=25, blank=True,
        help_text=_('Geolocalização da imagem no formato decimal.'))
    latitude = models.CharField(_('latitude'), default='', max_length=25,
            blank=True, help_text=_('Latitude onde a imagem foi criada.'))
    longitude = models.CharField(_('longitude'), default='', max_length=25,
            blank=True, help_text=_('Longitude onde a imagem foi criada.'))


    tag_life_stage = models.CharField(_('Estágio de Vida'), default='',
        blank=True, help_text=_('Estágio de Vida'))
    tag_habitat = models.CharField(_('Habitat'), default='', blank=True, help_text=_('Habitat da imagem'))
    tag_microscopy = models.CharField(_('Microscopia'), default='', blank=True, help_text=_('Microscópio utilizado'))
    tag_lifestyle = models.CharField(_('Estilo de Vida'), default='', blank=True, help_text=_('Estilo de vida'))
    tag_photographic_technique = models.CharField(_('Técnica de fotografia'), default='', blank=True, help_text=_('Técnica de fotografia utilizada'))
    tag_several = models.CharField(_('Diversos'), default='', blank=True, help_text=_('Informações diversas'))

    software = models.CharField(_('Software'), default='', blank=True, help_text=_('Software utilizado na Imagem'))

    specialist = models.ManyToManyField('Person',  related_name="pessoas", verbose_name=_('Especialista'), blank=True)
    # Foreign metadata
    location = models.ForeignKey('Location', on_delete=models.SET_NULL,
            null=True, blank=True, verbose_name=_('local'),
            help_text=_('Localidade mostrada na imagem (ou local de coleta).'))
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True,
            blank=True, verbose_name=_('cidade'),
            help_text=_('Cidade mostrada na imagem (ou cidade de coleta).'))
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True,
            blank=True, verbose_name=_('estado'),
            help_text=_('Estado mostrado na imagem (ou estado de coleta).'))
    country = models.ForeignKey('Country', on_delete=models.SET_NULL,
            null=True, blank=True, verbose_name=_('país'),
            help_text=_('País mostrado na imagem (ou país de coleta).'))
    

#     def rename_and_move_file(self):
#         if self.file and self.status == 'published':
#             current_file_path = self.file.path
#             new_filename = f"{self.title_pt_br}.{self.file.name.split('.')[-1]}"
#             new_file_path = os.path.join('site_media', new_filename)

#             shutil.move(current_file_path, new_file_path)

#             # Refresh the field "file" to be updated in the database
#             self.file.name = new_filename

#         elif self.file and self.status != 'published':
#             current_file_path = self.file.path
#             new_filename = f"uploads/{uuid.uuid4()}.{self.file.name.split('.')[-1]}"
#             new_file_path = os.path.join('site_media', new_filename)

#             shutil.move(current_file_path, new_file_path)

#             # Refresh the field "file" to be updated in the database
#             self.file.name = new_filename


    def save(self, *args, **kwargs):
        if self.pk:
        #     original = Media.objects.get(pk=self.pk)
        #     if self.status != original.status and ("published" in [self.status, original.status]):
        #         self.rename_and_move_file()
            
            if not self.taxons.exists():
                self.has_taxons = 'True'
            else:
                self.has_taxons = 'False'
        
        self.timestamp = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return 'ID={} {} ({}) {}'.format(self.id, self.title, self.datatype, self.status)

    def get_absolute_url(self):
        return reverse('media_url', args=[str(self.id)])

    class Meta:
        verbose_name = _('arquivo')
        verbose_name_plural = _('arquivos')
        ordering = ['id']


class Person(models.Model):
    name = models.CharField(_('nome'), max_length=200, unique=True, blank=True,
            help_text=_('Nome do autor.'))
    slug = models.SlugField(_('slug'), max_length=200, unique=True, blank=True,
            help_text=_('Slug do nome do autor.'))
    is_author = models.BooleanField(_('author'), default=False,
            help_text=_('Informa se a pessoa é autora.'))
    media = models.ManyToManyField('Media', blank=True,
            verbose_name=_('arquivos'),
            help_text=_('Arquivos associados a este autor.'))

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
    media = models.ManyToManyField('Media', blank=True,
            verbose_name=_('arquivos'),
            help_text=_('Arquivos associados a este marcador.'))
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
    media = models.ManyToManyField('Media', blank=True,
            verbose_name=_('arquivos'),
            help_text=_('Arquivos associados a este táxon.'))
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
    media = models.ManyToManyField('Media', blank=True,
            verbose_name=_('arquivos'),
            help_text=_('Arquivos associados a esta referência.'))

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


# Slugify before saving.
models.signals.pre_save.connect(slug_pre_save, sender=Person)
models.signals.pre_save.connect(slug_pre_save, sender=Tag)
models.signals.pre_save.connect(slug_pre_save, sender=Category)
models.signals.pre_save.connect(slug_pre_save, sender=Taxon)
models.signals.pre_save.connect(slug_pre_save, sender=Location)
models.signals.pre_save.connect(slug_pre_save, sender=City)
models.signals.pre_save.connect(slug_pre_save, sender=State)
models.signals.pre_save.connect(slug_pre_save, sender=Country)
models.signals.pre_save.connect(slug_pre_save, sender=Reference)
models.signals.pre_save.connect(slug_pre_save, sender=Tour)

# Create citation with bibkey.
models.signals.pre_save.connect(citation_pre_save, sender=Reference)

# Create copy of the media
models.signals.post_save.connect(create_site_media_copy, sender=Media)
# Delete file from folder when the media is deleted on website
models.signals.pre_delete.connect(delete_file_from_folder, sender=Media)
# Update the user's curatorships as specialist
models.signals.m2m_changed.connect(update_specialist_of, sender=Curadoria.specialists.through)
# Update the user's curatorships as curator
models.signals.m2m_changed.connect(update_curator_of, sender=Curadoria.curators.through)