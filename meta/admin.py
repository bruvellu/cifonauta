from meta import models
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

# Disable translatable models.
#admin.site.register(models.Image)
#admin.site.register(models.Video)
#admin.site.register(models.Tag)
#admin.site.register(models.TagCategory)
#admin.site.register(models.Taxon)
#admin.site.register(models.Size)
#admin.site.register(models.City)
#admin.site.register(models.State)
#admin.site.register(models.Country)
#admin.site.register(models.Tour)

admin.site.register(models.Author)
admin.site.register(models.Source)
admin.site.register(models.Rights)
admin.site.register(models.Sublocation)
admin.site.register(models.Reference)
admin.site.register(models.TourPosition)

# Translation admin.
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
admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.TagCategory, TagAdmin)
admin.site.register(models.Taxon, TaxonAdmin)
admin.site.register(models.City, CityAdmin)
admin.site.register(models.State, StateAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.Tour, TourAdmin)
