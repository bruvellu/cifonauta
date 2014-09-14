from modeltranslation.translator import translator, TranslationOptions
from meta.models import Image, Video, Tag, TagCategory, Taxon, City, State, Country, Tour

class ImageTranslation(TranslationOptions):
    fields = ('title', 'caption',)

class VideoTranslation(TranslationOptions):
    fields = ('title', 'caption',)

class TagTranslation(TranslationOptions):
    fields = ('name', 'description',)

class TagCatTranslation(TranslationOptions):
    fields = ('name', 'description',)

class TaxonTranslation(TranslationOptions):
    fields = ('common', 'rank')

class CityTranslation(TranslationOptions):
    fields = ('name',)

class StateTranslation(TranslationOptions):
    fields = ('name',)

class CountryTranslation(TranslationOptions):
    fields = ('name',)

class TourTranslation(TranslationOptions):
    fields = ('name', 'description')

translator.register(Image, ImageTranslation)
translator.register(Video, VideoTranslation)
translator.register(Tag, TagTranslation)
translator.register(TagCategory, TagCatTranslation)
translator.register(Taxon, TaxonTranslation)
translator.register(City, CityTranslation)
translator.register(State, StateTranslation)
translator.register(Country, CountryTranslation)
translator.register(Tour, TourTranslation)
