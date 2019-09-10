from meta.models import *
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.contrib.flatpages.models import FlatPage

# Translation admin.
class FlatPageAdmin(TranslationAdmin):
    pass


class ImageAdmin(TranslationAdmin):
    pass


class VideoAdmin(TranslationAdmin):
    pass


class TagAdmin(TranslationAdmin):
    pass


class TagCatAdmin(TranslationAdmin):
    pass


class TaxonAdmin(TranslationAdmin):
    pass


class CityAdmin(TranslationAdmin):
    pass


class StateAdmin(TranslationAdmin):
    pass


class CountryAdmin(TranslationAdmin):
    pass


class TourAdmin(TranslationAdmin):
    pass


class SizeAdmin(TranslationAdmin):
    pass


# Regular models.
admin.site.register(Author)
admin.site.register(Source)
admin.site.register(Sublocation)
admin.site.register(Reference)
admin.site.register(TourPosition)

# Translation models.
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagCategory, TagAdmin)
admin.site.register(Taxon, TaxonAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Size, SizeAdmin)
