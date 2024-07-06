from modeltranslation.translator import register, TranslationOptions
from meta.models import Media, Taxon, Tag, Category, City, State, Country, Tour, ModifiedMedia
from django.contrib.flatpages.models import FlatPage


@register(FlatPage)
class FlatPageTranslation(TranslationOptions):
    fields = ('title', 'content',)

@register(Media)
class MediaTranslation(TranslationOptions):
    fields = ('title', 'caption', 'acknowledgments')

@register(ModifiedMedia)
class ModifiedMedia2Translation(TranslationOptions):
    fields = ()

@register(Taxon)
class TaxonTranslation(TranslationOptions):
    fields = ('rank', 'status')

@register(Tag)
class TagTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(Category)
class CatTranslation(TranslationOptions):
    fields = ('name', 'description',)

@register(City)
class CityTranslation(TranslationOptions):
    fields = ()
    # fields = ('name',)

@register(State)
class StateTranslation(TranslationOptions):
    fields = ()
    # fields = ('name',)

@register(Country)
class CountryTranslation(TranslationOptions):
    fields = ()
    # fields = ('name',)

@register(Tour)
class TourTranslation(TranslationOptions):
    fields = ('name', 'description',)

