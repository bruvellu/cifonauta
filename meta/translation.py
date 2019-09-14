from modeltranslation.translator import register, TranslationOptions
from meta.models import Image, Video, Tag, TagCategory, Taxon, City, State, Country, Tour, Size
from django.contrib.flatpages.models import FlatPage


@register(FlatPage)
class FlatPageTranslation(TranslationOptions):
    fields = ('title', 'content',)

@register(Image)
class ImageTranslation(TranslationOptions):
    fields = ('title', 'caption',)

@register(Video)
class VideoTranslation(TranslationOptions):
    fields = ('title', 'caption',)

@register(Tag)
class TagTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(TagCategory)
class TagCatTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(Taxon)
class TaxonTranslation(TranslationOptions):
    fields = ('rank',)

@register(City)
class CityTranslation(TranslationOptions):
    fields = ('name',)

@register(State)
class StateTranslation(TranslationOptions):
    fields = ('name',)

@register(Country)
class CountryTranslation(TranslationOptions):
    fields = ('name',)

@register(Tour)
class TourTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(Size)
class SizeTranslation(TranslationOptions):
    fields = ('description',)

