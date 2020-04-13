from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from meta.models import *
from modeltranslation.admin import TranslationAdmin

# Translation admin.
class FlatPageAdmin(TranslationAdmin):
    pass


class MediaAdmin(TranslationAdmin):
    pass


class TagAdmin(TranslationAdmin):
    pass

class CatAdmin(TranslationAdmin):
    pass


class CityAdmin(TranslationAdmin):
    pass


class StateAdmin(TranslationAdmin):
    pass


class CountryAdmin(TranslationAdmin):
    pass


class TourAdmin(TranslationAdmin):
    pass


# Regular models.
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(Reference)
admin.site.register(Taxon)
admin.site.register(Stats)

# Translation models.
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CatAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Tour, TourAdmin)
