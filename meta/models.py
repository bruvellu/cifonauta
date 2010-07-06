from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify


class File(models.Model):
    # File
    source_filepath = models.CharField(max_length=100, blank=True)
    thumb_filepath = models.ImageField(upload_to='site_media/images/thumbs')
    timestamp = models.DateTimeField()

    # Website
    highlight = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    is_public = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    # IPTC
    title = models.CharField(max_length=64, blank=True)
    caption = models.TextField(blank=True)
    author = models.ForeignKey('Author')
    taxon = models.ForeignKey('Taxon')
    genus = models.ForeignKey('Genus')
    species = models.ForeignKey('Species')
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


class Video(File):
    web_filepath = models.FileField(upload_to='site_media/videos/')
    datatype = models.CharField(max_length=10, default='video')
    def __unicode__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    videos = models.ManyToManyField(Video, null=True, blank=True)
    parent = models.ForeignKey('TagCategory', blank=True, null=True,
            related_name='tags')
    def __unicode__(self):
        return self.name


class TagCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, blank=True)
    def __unicode__(self):
        return self.name


class Taxon(models.Model):
    name = models.CharField(max_length=256, unique=True, blank=True)
    slug = models.SlugField(max_length=256, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    def __unicode__(self):
        return self.name


class Genus(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    parent = models.ForeignKey('Taxon', blank=True, null=True, related_name='genera')
    def __unicode__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    parent = models.ForeignKey('Genus', blank=True, null=True, related_name='spp')
    def __unicode__(self):
        return self.name


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
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class Rights(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class Sublocation(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=True)
    slug = models.SlugField(max_length=32, blank=True)
    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=True)
    slug = models.SlugField(max_length=64, blank=True)
    def __unicode__(self):
        return self.name


def slug_pre_save(signal, instance, sender, **kwargs):
    if not instance.slug:
        slug = slugify(instance.name)
        instance.slug = slug

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
