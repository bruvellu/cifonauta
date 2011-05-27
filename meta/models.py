# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import permalink
from django.db.models import signals
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel
from meta.signals import *

from datatrans.utils import register


class File(models.Model):
    '''Define campos comuns para arquivos de mídia.'''
    #XXX Ideal seria ele não ser abstrato para poder chamar todos os tipos
    # de mídia chamando o File, mas acho que trocar agora vai dar trabalho.
    # File
    source_filepath = models.CharField(_('arquivo fonte local'), 
            max_length=200, blank=True, help_text=_('Arquivo fonte na pasta local.'))
    thumb_filepath = models.ImageField(_('thumbnail web'), 
            upload_to='site_media/images/thumbs', help_text=_('Pasta que guarda thumbnails.'))
    old_filepath = models.CharField(_('arquivo fonte original'), 
            max_length=200, blank=True, help_text=_('Caminho para o arquivo original.'))
    timestamp = models.DateTimeField(_('data de modificação'),
            help_text=_('Data da última modificação do arquivo.'))

    # Website
    highlight = models.BooleanField(_('destaque'), default=False, help_text=_('Imagem que merece destaque.'))
    cover = models.BooleanField(_('imagem de capa'), default=False, help_text=_('Imagem esteticamente bela, para usar na página principal.'))
    stats = models.OneToOneField('Stats', null=True, editable=False, 
            verbose_name=_('estatísticas'),
            help_text=_('Reúne estatísticas sobre a imagem.'))
    is_public = models.BooleanField(_('público'), default=False, help_text=_('Informa se imagem está visível para visitantes anônimos do site.'))
    review = models.BooleanField(_('sob revisão'), default=False, help_text=_('Informa se imagem deve ser revisada.'))
    notes = models.TextField(_('anotações'), blank=True, help_text=_('Campo de anotações extras sobre a imagem.'))
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True, help_text=_('Data de publicação da imagem no Cifonauta.'))

    # IPTC
    title = models.CharField(_('título'), max_length=200, blank=True, help_text=_('Título da imagem.'))
    caption = models.TextField(_('legenda'), blank=True, help_text=_('Legenda da imagem.'))
    #NOTA null e blank devem ser True
    # null está se referindo ao NULL do banco de dados e
    # blank está se referindo à interface de admin.
    size = models.ForeignKey('Size', null=True, blank=True, 
            verbose_name=_('tamanho'), help_text=_('Classe de tamanho do organismo na imagem.'))
    rights = models.ForeignKey('Rights', null=True, blank=True, 
            verbose_name=_('direitos'), help_text=_('Detentor dos direitos autorais da imagem.'))
    sublocation = models.ForeignKey('Sublocation', null=True, blank=True, 
            verbose_name=_('local'), help_text=_('Localidade mostrada na imagem (ou local de coleta).'))
    city = models.ForeignKey('City', null=True, blank=True, 
            verbose_name=('cidade'), help_text=_('Cidade mostrada na imagem (ou cidade de coleta).'))
    state = models.ForeignKey('State', null=True, blank=True, 
            verbose_name=_('estado'), help_text=_('Estado mostrado na imagem (ou estado de coleta).'))
    country = models.ForeignKey('Country', null=True, blank=True, 
            verbose_name=_('país'), help_text=_('País mostrado na imagem (ou país de coleta).'))

    # EXIF
    date = models.DateTimeField(_('data'), blank=True, help_text=_('Data em que a imagem foi criada.'))
    geolocation = models.CharField(_('geolocalização'), max_length=25, 
            blank=True, help_text=_('Geolocalização da imagem no formato decimal.'))
    latitude = models.CharField(_('latitude'), max_length=12, blank=True, help_text=_('Latitude onde foi criada a imagem.'))
    longitude = models.CharField(_('longitude'), max_length=12, blank=True, help_text=_('Longitude onde foi criada a imagem.'))

    class Meta:
        abstract = True
        verbose_name = _('arquivo')
        verbose_name_plural = _('arquivos')


class Image(File):
    web_filepath = models.ImageField(_('arquivo web'), 
            upload_to='site_media/images/', help_text=_('Caminho para o arquivo web.'))
    datatype = models.CharField(_('tipo de mídia'), max_length=10, 
            default='photo', help_text=_('Tipo de mídia.'))

    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('image_url', [str(self.id)])

    class Meta:
        verbose_name = _('foto')
        verbose_name_plural = _('fotos')


class Video(File):
    webm_filepath = models.FileField(_('arquivo webm'), 
            upload_to='site_media/videos/', blank=True, help_text=_('Caminho para o arquivo WEBM.'))
    ogg_filepath = models.FileField(_('arquivo ogg'), 
            upload_to='site_media/videos/', blank=True, help_text=_('Caminho para o arquivo OGG.'))
    mp4_filepath = models.FileField(_('arquivo mp4'), 
            upload_to='site_media/videos/', blank=True, help_text=_('Caminho para o arquivo MP4.'))
    datatype = models.CharField(_('tipo de mídia'), max_length=10, 
            default='video', help_text=_('Tipo de mídia.'))
    large_thumb = models.ImageField(_('thumbnail grande'), 
            upload_to='site_media/images/thumbs', help_text=_('Caminho para o thumbnail grande do vídeo.'))
    duration = models.CharField(_('duração'), max_length=20, 
            default='00:00:00', help_text=_('Duração do vídeo no formato HH:MM:SS.'))
    dimensions = models.CharField(_('dimensões'), max_length=20, default='0x0', help_text=_('Dimensões do vídeo original.'))
    codec = models.CharField(_('codec'), max_length=20, default='', help_text=_('Codec do vídeo original.'))

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('video_url', [str(self.id)])

    class Meta:
        verbose_name = _('vídeo')
        verbose_name_plural = _('vídeos')


class Author(models.Model):
    name = models.CharField(_('nome'), max_length=200, unique=True, help_text=_('Nome do autor.'))
    slug = models.SlugField(_('slug'), max_length=200, blank=True, help_text=_('Slug do nome do autor.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas a este autor.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados a este autor.'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False, help_text=_('Número de fotos associadas a este autor.'))
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este autor.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('author_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.images.count()
        self.video_count = self.videos.count()
        self.save()

    class Meta:
        verbose_name = _('autor')
        verbose_name_plural = _('autores')
        ordering = ['name']


class Source(models.Model):
    name = models.CharField(_('nome'), max_length=200, unique=True, help_text=_('Nome do especialista.'))
    slug = models.SlugField(_('slug'), max_length=200, blank=True, help_text=_('Slug do nome do especialista.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas a este especialista.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados a este especialista.'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False, help_text=_('Número de fotos associadas a este especialista.'))
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este especialista.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('source_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.images.count()
        self.video_count = self.videos.count()
        self.save()

    class Meta:
        verbose_name = _('especialista')
        verbose_name_plural = _('especialistas')
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome do marcador.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome do marcador.'))
    description = models.TextField(_('descrição'), blank=True, help_text=_('Descrição do marcador.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas a este marcador.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados a este marcador.'))
    parent = models.ForeignKey('TagCategory', blank=True, null=True,
            related_name='tags', verbose_name=_('pai'), help_text=_('Categoria a que este marcador pertence.'))
    position = models.PositiveIntegerField(_('posição'), default=0, help_text=_('Definem a ordem dos marcadores em um queryset.'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas a este marcador.'))
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associadas a este marcador.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('tag_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à M2M.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.images.count()
        self.video_count = self.videos.count()
        self.save()

    class Meta:
        verbose_name = _('marcador')
        verbose_name_plural = _('marcadores')
        ordering = ['position', 'name']


class TagCategory(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome da categoria de marcadores.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome da categoria de marcadores.'))
    description = models.TextField(_('descrição'), blank=True, help_text=_('Descrição da categoria de marcadores.'))
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='tagcat_children', verbose_name=_('pai'), help_text=_('Categoria pai desta categoria de marcadores.'))
    #TODO? Toda vez que uma tag é salva, atualizar a contagem das imagens e 
    # vídeos das categorias. Seria a soma dos marcadores, só?

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('categoria de marcadores')
        verbose_name_plural = _('categorias de marcadores')
        ordering = ['name']


class Taxon(MPTTModel):
    name = models.CharField(_('nome'), max_length=256, unique=True, help_text=_('Nome do táxon.'))
    slug = models.SlugField(_('slug'), max_length=256, blank=True, help_text=_('Slug do nome do táxon.'))
    common = models.CharField(_('nome popular'), max_length=256, blank=True, help_text=_('Nome popular do táxon.'))
    rank = models.CharField(_('rank'), max_length=256, blank=True, help_text=_('Ranking taxonômico do táxon.'))
    tsn = models.PositiveIntegerField(null=True, blank=True, help_text=_('TSN, o identificador do táxon no ITIS.'))
    aphia = models.PositiveIntegerField(null=True, blank=True, help_text=_('APHIA, o identificador do táxon no WoRMS.'))
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='children', verbose_name=_('pai'), help_text=_('Táxon pai deste táxon.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas a este táxon.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados a este táxon.'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False, help_text=_('Número de fotos associadas a este táxon.'))
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este táxon.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('taxon_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.images.count()
        self.video_count = self.videos.count()
        self.save()

    class Meta:
        verbose_name = _('táxon')
        verbose_name_plural = _('táxons')
        ordering = ['name']


class Size(models.Model):
    SIZES = (
            ('<0,1 mm', '<0,1 mm'),
            ('0,1 - 1,0 mm', '0,1 - 1,0 mm'),
            ('1,0 - 10 mm', '1,0 - 10 mm'),
            ('10 - 100 mm', '10 - 100 mm'),
            ('>100 mm', '>100 mm')
            )
    name = models.CharField(_('nome'), max_length=32, unique=True, 
            choices=SIZES, help_text=_('Nome da classe de tamanho.'))
    slug = models.SlugField(_('slug'), max_length=32, blank=True, help_text=_('Slug do nome da classe de tamanho.'))
    description = models.TextField(_('descrição'), blank=True, help_text=_('Descrição da classe de tamanho.'))
    position = models.PositiveIntegerField(_('posição'), default=0, help_text=_('Define ordem das classes de tamanho em um queryset.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas à esta classe de tamanho.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados à esta classe de tamanho.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('size_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à ForeignKey.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.image_set.count()
        self.video_count = self.video_set.count()
        self.save()

    class Meta:
        verbose_name = _('tamanho')
        verbose_name_plural = _('tamanhos')
        ordering = ['position']


class Rights(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome do detentor dos direitos autorais.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome do detentor dos direitos autorais.'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('detentor dos direitos')
        verbose_name_plural = _('detentores dos direitos')
        ordering = ['name']


class Sublocation(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome da localidade.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome da localidade.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas à esta localidade.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados à esta localidade.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('sublocation_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à ForeignKey.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.image_set.count()
        self.video_count = self.video_set.count()
        self.save()

    class Meta:
        verbose_name = _('local')
        verbose_name_plural = _('locais')
        ordering = ['name']


class City(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome da cidade.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome da cidade.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associados à esta cidade.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados à esta cidade.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('city_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à ForeignKey.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.image_set.count()
        self.video_count = self.video_set.count()
        self.save()

    class Meta:
        verbose_name = _('cidade')
        verbose_name_plural = _('cidades')
        ordering = ['name']


class State(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome do estado.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome do estado.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas a este estado.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este estado.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('state_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à ForeignKey.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.image_set.count()
        self.video_count = self.video_set.count()
        self.save()

    class Meta:
        verbose_name = _('estado')
        verbose_name_plural = _('estados')
        ordering = ['name']


class Country(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True, help_text=_('Nome do país.'))
    slug = models.SlugField(_('slug'), max_length=64, blank=True, help_text=_('Slug do nome do país.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas a este país.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este país.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('country_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à ForeignKey.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.image_set.count()
        self.video_count = self.video_set.count()
        self.save()

    class Meta:
        verbose_name = _('país')
        verbose_name_plural = _('país')
        ordering = ['name']


class Reference(models.Model):
    name = models.CharField(_('nome'), max_length=100, unique=True, help_text=_('Identificador da referência (Mendeley ID).'))
    slug = models.SlugField(_('slug'), max_length=100, blank=True, help_text=_('Slug do identificar da referência.'))
    citation = models.TextField(_('citação'), blank=True, help_text=_('Citação formatada da referência.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas à esta referência.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados à esta referência.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas à esta referência.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados à esta referência.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('reference_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à M2M.

        Atualiza os respectivos campos image_count e video_count.
        '''
        #XXX Fiz desse jeito para não chamar o save(), já que ele se conecta ao 
        # Mendeley no signal pre_save (deixando o save() lento...).
        Reference.objects.filter(id=self.id).update(image_count=self.images.count())
        Reference.objects.filter(id=self.id).update(video_count=self.videos.count())

    class Meta:
        verbose_name = _('referência')
        verbose_name_plural = _('referências')
        ordering = ['-citation']


class Tour(models.Model):
    name = models.CharField(_('nome'), max_length=100, unique=True, help_text=_('Nome do tour.'))
    slug = models.SlugField(_('slug'), max_length=100, blank=True, help_text=_('Slug do nome do tour.'))
    description = models.TextField(_('descrição'), blank=True, help_text=_('Descrição do tour.'))
    is_public = models.BooleanField(_('público'), default=False, help_text=_('Informa se o tour está visível para visitantes anônimos.'))
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True, help_text=_('Data de publicação do tour no Cifonauta.'))
    timestamp = models.DateTimeField(_('data de modificação'), auto_now=True, help_text=_('Data da última modificação do tour.'))
    stats = models.OneToOneField('Stats', null=True, editable=False,
            verbose_name=_('estatísticas'),
            help_text=_('Guarda estatísticas de acesso ao tour.'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'), help_text=_('Fotos associadas a este tour.'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'), help_text=_('Vídeos associados a este tour.'))
    references = models.ManyToManyField(Reference, null=True, blank=True, 
            verbose_name=_('referências'), help_text=_('Referências associadas a este tour.'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False, help_text=_('Número de fotos associadas a este tour.'))
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False, help_text=_('Número de vídeos associados a este tour.'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('tour_url', [self.slug])

    def counter(self):
        '''Conta o número de imagens+vídeos associados à M2M.

        Atualiza os respectivos campos image_count e video_count.
        '''
        self.image_count = self.images.count()
        self.video_count = self.videos.count()
        self.save()

    class Meta:
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        ordering = ['name']


class Stats(models.Model):
    '''Modelo para abrigar estatísticas sobre modelos.'''
    pageviews = models.PositiveIntegerField(_('visitas'), default=0, 
            editable=False, help_text=_('Número de impressões de página de uma imagem.'))

    def __unicode__(self):
        try:
            related = self.image
        except:
            try:
                related = self.video
            except:
                related = self.tour
        return '%s visitas (%s, id=%d)' % (self.pageviews, related, related.id)
    
    class Meta:
        verbose_name = _('estatísticas')
        verbose_name_plural = _('estatísticas')


# Registrando modelos para tradução.
class ImageTranslation(object):
    fields = ('title', 'caption', 'notes',)
register(Image, ImageTranslation)

class VideoTranslation(object):
    fields = ('title', 'caption', 'notes',)
register(Video, VideoTranslation)

class TagTranslation(object):
    fields = ('name', 'description',)
register(Tag, TagTranslation)

class TagCatTranslation(object):
    fields = ('name', 'description',)
register(TagCategory, TagCatTranslation)

class TaxonTranslation(object):
    fields = ('common', 'rank',)
register(Taxon, TaxonTranslation)

class SizeTranslation(object):
    fields = ('description',)
register(Size, SizeTranslation)

class CountryTranslation(object):
    fields = ('name',)
register(Country, CountryTranslation)

class TourTranslation(object):
    fields = ('name','description',)
register(Tour, TourTranslation)

class FlatPageTranslation(object):
    fields = ('title', 'content',)
register(FlatPage, FlatPageTranslation)

# Slugify before saving.
signals.pre_save.connect(slug_pre_save, sender=Author)
signals.pre_save.connect(slug_pre_save, sender=Tag)
signals.pre_save.connect(slug_pre_save, sender=TagCategory)
signals.pre_save.connect(slug_pre_save, sender=Taxon)
signals.pre_save.connect(slug_pre_save, sender=Size)
signals.pre_save.connect(slug_pre_save, sender=Source)
signals.pre_save.connect(slug_pre_save, sender=Rights)
signals.pre_save.connect(slug_pre_save, sender=Sublocation)
signals.pre_save.connect(slug_pre_save, sender=City)
signals.pre_save.connect(slug_pre_save, sender=State)
signals.pre_save.connect(slug_pre_save, sender=Country)
signals.pre_save.connect(slug_pre_save, sender=Reference)
signals.pre_save.connect(slug_pre_save, sender=Tour)
# Create citation with bibkey.
signals.pre_save.connect(citation_pre_save, sender=Reference)
# Update models autocount field.
signals.post_save.connect(update_count, sender=Image)
signals.post_delete.connect(update_count, sender=Image)
signals.post_save.connect(update_count, sender=Video)
signals.post_delete.connect(update_count, sender=Video)
# Create stats object before object creation
signals.pre_save.connect(makestats, sender=Image)
signals.pre_save.connect(makestats, sender=Video)
signals.pre_save.connect(makestats, sender=Tour)
