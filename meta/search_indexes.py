from haystack import indexes
from django.utils.translation import get_language
from models import Image, Author, Tag, Taxon, Video

class MediaIndex(indexes.SearchIndex):
    is_public = indexes.BooleanField(default=True)
    datatype = indexes.CharField(model_attr='datatype')   
    
    authors = indexes.MultiValueField() 
    tags = indexes.MultiValueField()
    taxons = indexes.MultiValueField()
    size = indexes.IntegerField(model_attr='size__id', default=0)
    sublocation = indexes.CharField(model_attr='sublocation__slug', default='')
    city = indexes.CharField(model_attr='city__slug', default='')
    state = indexes.CharField(model_attr='state__slug', default='')
    country = indexes.CharField(model_attr='country__slug', default='')
    
    
    stats__pageviews = indexes.IntegerField(model_attr='stats__pageviews', default=0)
    timestamp = indexes.DateField(model_attr='timestamp', null=True)
    date = indexes.DateField(model_attr='date', null=True)
    pub_date = indexes.DateField(model_attr='pub_date', null=True)
    id = indexes.IntegerField(model_attr='id')
    
    highlight = indexes.BooleanField(model_attr='highlight', default=False)
    
    def prepare_authors(self, object):
        return [author.slug for author in Author.objects.filter(images__pk = object.pk)]
    
    def prepare_tags(self, object):
        return [tag.slug for tag in Tag.objects.filter(images__pk = object.pk)]
    
    def prepare_taxons(self, object):
        return [taxon.slug for taxon in Taxon.objects.filter(images__pk = object.pk)]

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(is_public=True) #select_related('author', 'tag', 'taxon', 'size', 'sublocation', 'city', 'state', 'country', 'rights')
     

class ImageIndex(MediaIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/image_text.txt')
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='search/image_text.txt')
    
    text_en = indexes.CharField(use_template=True, template_name='search/image_text_en.txt')
    content_auto_en = indexes.EdgeNgramField(use_template=True, template_name='search/image_text_en.txt')
 
    is_image = indexes.BooleanField(default=True)

    def get_model(self):
        return Image


class VideoIndex(MediaIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/video_text.txt')
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='search/video_text.txt')
    
    text_en = indexes.CharField(use_template=True, template_name='search/video_text_en.txt')
    content_auto_en = indexes.EdgeNgramField(use_template=True, template_name='search/video_text_en.txt')
    
    is_video = indexes.BooleanField(default=True)

    def get_model(self):
        return Video


from django.conf import settings

from haystack.query import SearchQuerySet, DEFAULT_OPERATOR

class MlSearchQuerySet(SearchQuerySet):
    def get_language_suffix(self):
        lang = str(get_language()[:2])
        if lang != 'pt':
            key = "_" + lang
        else:
            key = ""
        return key
    
    def filter(self, *args, **kwargs):
        """ narrows to current language """
        if 'content' in kwargs:
            kwd = kwargs.pop('content')
            kwdkey = "text%s" % self.get_language_suffix()
            kwargs[kwdkey] = kwd
        return super(MlSearchQuerySet, self).filter(*args, **kwargs)

    def autocomplete(self, **kwargs):
        """ narrows to current language """
        if 'content_auto' in kwargs:
            kwd = kwargs.pop('content_auto')
            kwdkey = "content_auto%s" % self.get_language_suffix()
            kwargs[kwdkey] = kwd
        return super(MlSearchQuerySet, self).autocomplete(**kwargs)
        
