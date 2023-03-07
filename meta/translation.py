from modeltranslation.translator import register, TranslationOptions
from meta.models import Media, Taxon, Tag, Category, City, State, Country, Tour
from django.contrib.flatpages.models import FlatPage


@register(FlatPage)
class FlatPageTranslation(TranslationOptions):
    fields = ('title', 'content',)

@register(Media)
class MediaTranslation(TranslationOptions):
    fields = ('title', 'caption',)

@register(Taxon)
class TaxonTranslation(TranslationOptions):
    fields = ('rank', 'status')

@register(Tag)
class TagTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(Category)
class CatTranslation(TranslationOptions):
    fields = ('name', 'description',)

# TODO: Translate locations as well.

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
