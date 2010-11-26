# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import signals
from django.db.models import permalink
from django.template.defaultfilters import slugify


class File(models.Model):
    # File
    source_filepath = models.CharField(max_length=200, blank=True)
    thumb_filepath = models.ImageField(upload_to='site_media/images/thumbs')
    old_filepath = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField()

    # Website
    highlight = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    is_public = models.BooleanField(default=False)
    #FIXME Tirar esse review?
    review = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    # IPTC
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    size = models.ForeignKey('Size')
    source = models.ForeignKey('Source')
    rights = models.ForeignKey('Rights')
    sublocation = models.ForeignKey('Sublocation')
    city = models.ForeignKey('City')
    state = models.ForeignKey('State')
    country = models.ForeignKey('Country')

    # EXIF
    date = models.DateTimeField(blank=True)
    geolocation = models.CharField(max_length=25, blank=True)
    latitude = models.CharField(max_length=12, blank=True)
    longitude = models.CharField(max_length=12, blank=True)

    class Meta:
        abstract = True


class Image(File):
    web_filepath = models.ImageField(upload_to='site_media/images/')
    datatype = models.CharField(max_length=10, default='photo')

    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('image_url', [str(self.id)])


class Video(File):
    webm_filepath = models.FileField(upload_to='site_media/videos/', blank=True)
    ogg_filepath = models.FileField(upload_to='site_media/videos/', blank=True)
    mp4_filepath = models.FileField(upload_to='site_media/videos/', blank=True)
    #flv_filepath = models.FileField(upload_to='site_media/videos/', blank=True)
    datatype = models.CharField(max_length=10, default='video')
    large_thumb = models.ImageField(upload_to='site_media/images/thumbs')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('video_url', [str(self.id)])


class Author(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=True)
    slug = models.SlugField(max_length=200, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('author_url', [self.slug])


class Source(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=True)
    slug = models.SlugField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=64, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)
    parent = models.ForeignKey('TagCategory', blank=True, null=True,
            related_name='tags')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('tag_url', [self.slug])


class TagCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=64, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='tagcat_children')
    def __unicode__(self):
        return self.name


class Taxon(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256, blank=True)
    common = models.CharField(max_length=256, blank=True)
    rank = models.CharField(max_length=256, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('taxon_url', [self.slug])


class Genus(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)
    common = models.CharField(max_length=256, blank=True)
    parent = models.ForeignKey('Taxon', blank=True, null=True, related_name='genera')
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('genus_url', [self.slug])


class Species(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)
    common = models.CharField(max_length=256, blank=True)
    parent = models.ForeignKey('Genus', blank=True, null=True, related_name='spp')
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('species_url', [self.parent.slug, self.slug])


class Size(models.Model):
    SIZES = (
            ('', ''),
            ('<0,1 mm', '<0,1 mm'),
            ('0,1 - 1,0 mm', '0,1 - 1,0 mm'),
            ('1,0 - 10 mm', '1,0 - 10 mm'),
            ('10 - 100 mm', '10 - 100 mm'),
            ('>100 mm', '>100 mm')
            )
    name = models.CharField(max_length=32, unique=True, choices=SIZES,
            blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    position = models.PositiveIntegerField(default=0)
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('size_url', [self.slug])


class Rights(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name


class Sublocation(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('sublocation_url', [self.slug])


class City(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('city_url', [self.slug])


class State(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('state_url', [self.slug])


class Country(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('country_url', [self.slug])


class Reference(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, blank=True)
    citation = models.TextField(blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('reference_url', [self.slug])

def citation_pre_save(signal, instance, sender, **kwargs):
    '''Cria citação em HTML a partir da bibkey.'''
    citation = u'Nelas, BC. 2010. As Bolachas. Certo'
    instance.citation = citation

def slug_pre_save(signal, instance, sender, **kwargs):
    '''Cria slug antes de salvar.'''
    if not instance.slug:
        slug = slugify(instance.name)
        instance.slug = slug

# Slugify before saving.
signals.pre_save.connect(slug_pre_save, sender=Author)
signals.pre_save.connect(slug_pre_save, sender=Tag)
signals.pre_save.connect(slug_pre_save, sender=TagCategory)
signals.pre_save.connect(slug_pre_save, sender=Taxon)
signals.pre_save.connect(slug_pre_save, sender=Genus)
signals.pre_save.connect(slug_pre_save, sender=Species)
signals.pre_save.connect(slug_pre_save, sender=Size)
signals.pre_save.connect(slug_pre_save, sender=Source)
signals.pre_save.connect(slug_pre_save, sender=Rights)
signals.pre_save.connect(slug_pre_save, sender=Sublocation)
signals.pre_save.connect(slug_pre_save, sender=City)
signals.pre_save.connect(slug_pre_save, sender=State)
signals.pre_save.connect(slug_pre_save, sender=Country)
signals.pre_save.connect(slug_pre_save, sender=Reference)
# Create citation with bibkey.
signals.pre_save.connect(citation_pre_save, sender=Reference)
