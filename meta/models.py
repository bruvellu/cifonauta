# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import signals
from django.db.models import permalink
from django.template.defaultfilters import slugify

from external.mendeley import mendeley


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
    review = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    # IPTC
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    #NOTA null e blank devem ser True
    # null está se referindo ao NULL do banco de dados e
    # blank está se referindo à interface de admin.
    size = models.ForeignKey('Size', null=True, blank=True)
    source = models.ForeignKey('Source', null=True, blank=True)
    rights = models.ForeignKey('Rights', null=True, blank=True)
    sublocation = models.ForeignKey('Sublocation', null=True, blank=True)
    city = models.ForeignKey('City', null=True, blank=True)
    state = models.ForeignKey('State', null=True, blank=True)
    country = models.ForeignKey('Country', null=True, blank=True)

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
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('author_url', [self.slug])


class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)
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
        return ('species_url', [self.slug])


class Size(models.Model):
    SIZES = (
            ('<0,1 mm', '<0,1 mm'),
            ('0,1 - 1,0 mm', '0,1 - 1,0 mm'),
            ('1,0 - 10 mm', '1,0 - 10 mm'),
            ('10 - 100 mm', '10 - 100 mm'),
            ('>100 mm', '>100 mm')
            )
    name = models.CharField(max_length=32, unique=True, choices=SIZES)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    position = models.PositiveIntegerField(default=0)
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('size_url', [self.slug])


class Rights(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name


class Sublocation(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('sublocation_url', [self.slug])


class City(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('city_url', [self.slug])


class State(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('state_url', [self.slug])


class Country(models.Model):
    name = models.CharField(max_length=64, unique=True)
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

def get_html(ref):
    '''Retorna citação formatada em HTML.'''
    #TODO E se não tiver issue ou url ou doi?
    keys = ['year', 'title', 'publication_outlet', 'volume', 'issue', 'pages',
            'url', 'authors']
    # Fix
    for key in keys:
        if not key in ref:
            ref[key] = ''
    # DOI fix
    if 'identifiers' in ref:
        if not 'doi' in ref['identifiers']:
            doi = ''
        else:
            doi = ', doi:<a href="http://dx.doi.org/%s">%s</a>' % (ref['identifiers']['doi'], ref['identifiers']['doi'])
    else:
        doi = ''
    authors = []

    for author in ref['authors']:
        names = author.split()
        last = names.pop()
        initials = [name[:1] for name in names]
        initials = ''.join(initials)
        final = u'%s %s' % (last, initials)
        authors.append(final)
    authors = ', '.join(authors)

    if ref['issue']:
        issue = '(%s)' % ref['issue']
    else:
        issue = ''

    if ref['url']:
        url = '<br><a href="%s">%s</a>' % (ref['url'], ref['url'])
    else:
        url = ''

    citation = u'<strong>%s</strong> %s. %s %s, %s%s: %s%s%s' % (
            ref['year'], authors, ref['title'],
            ref['publication_outlet'], ref['volume'], issue,
            ref['pages'], doi, url
            )
    return citation

def citation_pre_save(signal, instance, sender, **kwargs):
    '''Cria citação em HTML a partir da bibkey.'''
    ref_id = instance.name
    ref = mendeley.document_details(ref_id)
    citation = get_html(ref)
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
