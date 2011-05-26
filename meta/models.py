# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import permalink
from django.db.models import signals
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel
from meta.signals import *

from datatrans.utils import register


#TODO Incluir help_text='' nos fields!


class File(models.Model):
    # File
    source_filepath = models.CharField(_('arquivo fonte local'), 
            max_length=200, blank=True)
    thumb_filepath = models.ImageField(_('thumbnail web'), 
            upload_to='site_media/images/thumbs')
    old_filepath = models.CharField(_('arquivo fonte original'), 
            max_length=200, blank=True)
    timestamp = models.DateTimeField(_('data de modificação'))

    # Website
    highlight = models.BooleanField(_('destaque'), default=False)
    cover = models.BooleanField(_('imagem de capa'), default=False)
    stats = models.OneToOneField('Stats', null=True, 
            verbose_name=_('estatísticas'))
    is_public = models.BooleanField(_('público'), default=False)
    review = models.BooleanField(_('sob revisão'), default=False)
    notes = models.TextField(_('anotações'), blank=True)
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True)

    # IPTC
    title = models.CharField(_('título'), max_length=200, blank=True)
    caption = models.TextField(_('legenda'), blank=True)
    #NOTA null e blank devem ser True
    # null está se referindo ao NULL do banco de dados e
    # blank está se referindo à interface de admin.
    size = models.ForeignKey('Size', null=True, blank=True, 
            verbose_name=_('tamanho'))
    rights = models.ForeignKey('Rights', null=True, blank=True, 
            verbose_name=_('direitos'))
    sublocation = models.ForeignKey('Sublocation', null=True, blank=True, 
            verbose_name=_('local'))
    city = models.ForeignKey('City', null=True, blank=True, 
            verbose_name=('cidade'))
    state = models.ForeignKey('State', null=True, blank=True, 
            verbose_name=_('estado'))
    country = models.ForeignKey('Country', null=True, blank=True, 
            verbose_name=_('país'))

    # EXIF
    date = models.DateTimeField(_('data'), blank=True)
    geolocation = models.CharField(_('geolocalização'), max_length=25, 
            blank=True)
    latitude = models.CharField(_('latitude'), max_length=12, blank=True)
    longitude = models.CharField(_('longitude'), max_length=12, blank=True)

    class Meta:
        abstract = True
        verbose_name = _('arquivo')
        verbose_name_plural = _('arquivos')


class Image(File):
    web_filepath = models.ImageField(_('arquivo web'), 
            upload_to='site_media/images/')
    datatype = models.CharField(_('tipo de mídia'), max_length=10, 
            default='photo')

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
            upload_to='site_media/videos/', blank=True)
    ogg_filepath = models.FileField(_('arquivo ogg'), 
            upload_to='site_media/videos/', blank=True)
    mp4_filepath = models.FileField(_('arquivo mp4'), 
            upload_to='site_media/videos/', blank=True)
    #flv_filepath = models.FileField(upload_to='site_media/videos/', blank=True)
    datatype = models.CharField(_('tipo de mídia'), max_length=10, 
            default='video')
    large_thumb = models.ImageField(_('thumbnail grande'), 
            upload_to='site_media/images/thumbs')
    duration = models.CharField(_('duração'), max_length=20, 
            default='00:00:00')
    dimensions = models.CharField(_('dimensões'), max_length=20, default='0x0')
    codec = models.CharField(_('codec'), max_length=20, default='')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('video_url', [str(self.id)])

    class Meta:
        verbose_name = _('vídeo')
        verbose_name_plural = _('vídeos')


class Author(models.Model):
    name = models.CharField(_('nome'), max_length=200, unique=True)
    slug = models.SlugField(_('slug'), max_length=200, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False)
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=200, unique=True)
    slug = models.SlugField(_('slug'), max_length=200, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False)
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    description = models.TextField(_('descrição'), blank=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    parent = models.ForeignKey('TagCategory', blank=True, null=True,
            related_name='tags', verbose_name=_('pai'))
    position = models.PositiveIntegerField(_('posição'), default=0)
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    description = models.TextField(_('descrição'), blank=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='tagcat_children', verbose_name=_('pai'))
    #TODO? Toda vez que uma tag é salva, atualizar a contagem das imagens e 
    # vídeos das categorias. Seria a soma dos marcadores, só?

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('categoria de marcadores')
        verbose_name_plural = _('categorias de marcadores')
        ordering = ['name']


class Taxon(MPTTModel):
    name = models.CharField(_('nome'), max_length=256, unique=True)
    slug = models.SlugField(_('slug'), max_length=256, blank=True)
    common = models.CharField(_('nome popular'), max_length=256, blank=True)
    rank = models.CharField(_('rank'), max_length=256, blank=True)
    tsn = models.PositiveIntegerField(null=True, blank=True)
    aphia = models.PositiveIntegerField(null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='children', verbose_name=_('pai'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    image_count = models.PositiveIntegerField(_('número de fotos'), default=0, 
            editable=False)
    video_count = models.PositiveIntegerField(_('número de vídeos'), default=0, editable=False)

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
            choices=SIZES)
    description = models.TextField(_('descrição'), blank=True)
    slug = models.SlugField(_('slug'), max_length=32, blank=True)
    position = models.PositiveIntegerField(_('posição'), default=0)
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('detentor dos direitos')
        verbose_name_plural = _('detentores dos direitos')
        ordering = ['name']


class Sublocation(models.Model):
    name = models.CharField(_('nome'), max_length=64, unique=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=64, unique=True)
    slug = models.SlugField(_('slug'), max_length=64, blank=True)
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, blank=True)
    citation = models.TextField(_('citação'), blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)

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
    name = models.CharField(_('nome'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, blank=True)
    description = models.TextField(_('descrição'), blank=True)
    is_public = models.BooleanField(_('público'), default=False)
    pub_date = models.DateTimeField(_('data de publicação'), auto_now_add=True)
    timestamp = models.DateTimeField(_('data de modificação'), auto_now=True)
    stats = models.OneToOneField('Stats', null=True, 
            verbose_name=_('estatísticas'))
    images = models.ManyToManyField(Image, null=True, blank=True, 
            verbose_name=_('fotos'))
    videos = models.ManyToManyField(Video, null=True, blank=True, 
            verbose_name=_('vídeos'))
    image_count = models.PositiveIntegerField(
            _('número de fotos'), default=0, editable=False)
    video_count = models.PositiveIntegerField(
            _('número de vídeos'), default=0, editable=False)
    references = models.ManyToManyField(Reference, null=True, blank=True, 
            verbose_name=_('referências'))

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
            editable=False)

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
