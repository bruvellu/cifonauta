# -*- coding: utf-8 -*-

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel
from meta.signals import *

from django.db.models import Q


class Media(models.Model):
    '''Table containing both image and video files.'''

    # File
    filepath = models.CharField(_('arquivo original.'), max_length=200,
            unique=True, help_text=_('Caminho único para arquivo original.'))
    sitepath = models.FileField(_('arquivo web.'), unique=True,
            help_text=_('Arquivo processado para a web.'))
    coverpath = models.ImageField(_('amostra do arquivo.'), unique=True,
            help_text=_('Imagem de amostra do arquivo processado.'))
    datatype = models.CharField(_('tipo de mídia'), max_length=15,
            help_text=_('Tipo de mídia.'))
    timestamp = models.DateTimeField(_('data de modificação'),
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
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True,
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

    def __str__(self):
        return 'ID={} {} ({})'.format(self.id, self.title, self.datatype)

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
    rank = models.CharField(_(u'rank'), max_length=256, blank=True, help_text=_(u'Ranking taxonômico do táxon.'))
    aphia = models.PositiveIntegerField(null=True, blank=True,
            help_text=_('APHIA, o identificador do táxon no WoRMS.'))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True,
            null=True, related_name='children', verbose_name=_('pai'),
            help_text=_('Táxon pai deste táxon.'))
    media = models.ManyToManyField( 'Media', blank=True,
            verbose_name=_('arquivos'),
            help_text=_('Arquivos associados a este táxon.'))
    timestamp = models.DateTimeField( _('data de modificação'), blank=True,
            null=True, help_text=_('Data da última modificação do arquivo.'))

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
            help_text=_('Arquivos associados à esta referência.'))

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
