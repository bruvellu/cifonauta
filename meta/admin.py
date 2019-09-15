from meta.models import *
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.contrib.flatpages.models import FlatPage

# Translation admin.
class FlatPageAdmin(TranslationAdmin):
    pass


class MediaAdmin(TranslationAdmin):
    pass


class TagAdmin(TranslationAdmin):
    pass


class TagCatAdmin(TranslationAdmin):
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
admin.site.register(Person)
admin.site.register(Sublocation)
admin.site.register(Reference)
admin.site.register(Taxon)

# Translation models.
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagCategory, TagAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Size, SizeAdmin)
