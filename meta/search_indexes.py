from haystack import indexes
from django.utils.translation import get_language
from models import Image, Video

import unicodedata


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


class MediaIndex(indexes.SearchIndex):

    is_public = indexes.BooleanField(default=True)
    datatype = indexes.CharField(model_attr='datatype')

    author = indexes.MultiValueField(faceted=True)
    source = indexes.MultiValueField(faceted=True)
    tag = indexes.MultiValueField(faceted=True)
    taxon = indexes.MultiValueField(faceted=True)
    tour = indexes.MultiValueField()
    reference = indexes.MultiValueField()

    size = indexes.IntegerField(model_attr='size__id', default=0, faceted=True)
    sublocation = indexes.CharField(model_attr='sublocation__id', default=0, faceted=True)
    city = indexes.CharField(model_attr='city__id', default=0, faceted=True)
    state = indexes.CharField(model_attr='state__id', default=0, faceted=True)
    country = indexes.CharField(model_attr='country__id', default=0, faceted=True)

    stats__pageviews = indexes.IntegerField(model_attr='stats__pageviews', default=0)
    timestamp = indexes.DateField(model_attr='timestamp', null=True)
    date = indexes.DateField(model_attr='date', null=True)
    pub_date = indexes.DateField(model_attr='pub_date', null=True)
    id = indexes.IntegerField(model_attr='id')

    highlight = indexes.BooleanField(model_attr='highlight', default=False)

    title_en = indexes.CharField(model_attr='title_en', default='')
    title = indexes.CharField(model_attr='title_pt')

    thumb = indexes.CharField(model_attr='thumb_filepath')
    url = indexes.CharField(model_attr='get_absolute_url')

    def prepare_author(self, media):
        return [author.id for author in media.author_set.all()]
        # "%s##%s" % (author.slug, author.name,) for author in media.author_set.all()]
        # Author.objects.filter(images__pk = object.pk)]

    def prepare_source(self, media):
        return [source.id for source in media.source_set.all()]
        # "%s##%s" % (source.slug, source.name,) for source in media.source_set.all()]
        # Source.objects.filter(images__pk = object.pk)]

    def prepare_tag(self, media):
        return [tag.id for tag in media.tag_set.all()]
        #Tag.objects.filter(images__pk = object.pk)]

    def prepare_taxon(self, media):
        return [taxon.id for taxon in media.taxon_set.all()]
        #Taxon.objects.filter(images__pk = object.pk)]

    def prepare_tour(self, media):
        return [tour.id for tour in media.tour_set.all()]
        #Taxon.objects.filter(images__pk = object.pk)]

    def prepare_reference(self, media):
        return [reference.id for reference in media.reference_set.all()]
        #Taxon.objects.filter(images__pk = object.pk)]

    def index_queryset(self):
        '''Used when the entire index for model is updated.'''
        return self.get_model().objects.filter(is_public=True)
        #select_related('author', 'tag', 'taxon', 'size', 'sublocation', 'city', 'state', 'country', 'rights')

    def prepare(self, obj):
        '''Fetches and adds/alters data before indexing.'''
        self.prepared_data = super(MediaIndex, self).prepare(obj)
        u = type(unicode())
        for key, data in self.prepared_data.items():
            if type(data) == u:
                self.prepared_data[key] = strip_accents(data)
        return self.prepared_data


class ImageIndex(MediaIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/image_text.txt')
    rendered = indexes.CharField(use_template=True, template_name='search/image_rendered.txt')
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='search/image_text.txt')

    text_en = indexes.CharField(use_template=True, template_name='search/image_text_en.txt')
    rendered_en = indexes.CharField(use_template=True, template_name='search/image_rendered_en.txt')
    content_auto_en = indexes.EdgeNgramField(use_template=True, template_name='search/image_text_en.txt')

    is_image = indexes.BooleanField(default=True)
    is_video = indexes.BooleanField(default=False)

    def get_model(self):
        return Image


class VideoIndex(MediaIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/video_text.txt')
    rendered = indexes.CharField(use_template=True, template_name='search/video_rendered.txt')
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='search/video_text.txt')

    text_en = indexes.CharField(use_template=True, template_name='search/video_text_en.txt')
    rendered_en = indexes.CharField(use_template=True, template_name='search/video_rendered_en.txt')
    content_auto_en = indexes.EdgeNgramField(use_template=True, template_name='search/video_text_en.txt')

    is_image = indexes.BooleanField(default=False)
    is_video = indexes.BooleanField(default=True)

    def get_model(self):
        return Video


from haystack.query import SearchQuerySet


class MlSearchQuerySet(SearchQuerySet):
    def get_language_suffix(self):
        lang = str(get_language()[:2])
        if lang != 'pt':
            key = '_' + lang
        else:
            key = ''
        return key

    def filter(self, *args, **kwargs):
        '''Narrows to current language.'''
        if 'content' in kwargs:
            kwd = kwargs.pop('content')
            kwdkey = 'text%s' % self.get_language_suffix()
            kwargs[kwdkey] = strip_accents(unicode(kwd))
        return super(MlSearchQuerySet, self).filter(*args, **kwargs)

    def autocomplete(self, **kwargs):
        '''Narrows to current language.'''
        if 'content_auto' in kwargs:
            kwd = kwargs.pop('content_auto')
            kwdkey = 'content_auto%s' % self.get_language_suffix()
            kwargs[kwdkey] = strip_accents(kwd)
        return super(MlSearchQuerySet, self).autocomplete(**kwargs)

    def values(self, *args, **kwargs):
        '''Narrows to current language.'''
        if 'title' in args:
            args = list(args)
            args.remove('title')
            kwd = 'title%s' % self.get_language_suffix()
            args.append(unicode(kwd))
        if 'text' in args:
            args = list(args)
            args.remove('text')
            kwd = 'text%s' % self.get_language_suffix()
            args.append(unicode(kwd))
        if 'rendered' in args:
            args = list(args)
            args.remove('rendered')
            kwd = 'rendered%s' % self.get_language_suffix()
            args.append(unicode(kwd))
        return super(MlSearchQuerySet, self).values(*args, **kwargs)
