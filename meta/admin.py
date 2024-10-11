from django.contrib import admin, messages
from django.contrib.flatpages.models import FlatPage
from modeltranslation.admin import TranslationAdmin

from meta.models import *
from .forms import CurationAdminForm


class CurationAdmin(admin.ModelAdmin):
    form = CurationAdminForm
    autocomplete_fields = ['specialists', 'curators', 'taxa']
    list_display = ['name', 'description', 'slug', 'id']


# Translation admin.
class FlatPageAdmin(TranslationAdmin):
    pass


class MediaAdmin(TranslationAdmin):
    list_display = ['id', 'datatype', 'title', 'user', 'date_created', 'is_public',
                    'highlight', 'date_modified']
    list_select_related = True
    search_fields = ['title', 'caption', 'taxa__name', 'tags__name', 'authors__name', 'curators__name',
                     'specialists__name', 'location__name', 'city__name', 'state__name', 'country__name',
                     'references__citation']
    list_filter = ['status', 'datatype', 'highlight', 'date_modified', 'scale',
                   'authors', 'tags', 'license', 'terms']
    autocomplete_fields = ['user', 'location', 'city', 'state', 'country']
    filter_horizontal = ['authors', 'curators', 'specialists', 'taxa', 'tags', 'references']
    readonly_fields = ['uuid', 'date_uploaded', 'date_modified', 'search_vector']


class TagAdmin(TranslationAdmin):
    list_display = ['name', 'description', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']


class CatAdmin(TranslationAdmin):
    pass


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']


class CityAdmin(TranslationAdmin):
    search_fields = ['name']


class StateAdmin(TranslationAdmin):
    search_fields = ['name']


class CountryAdmin(TranslationAdmin):
    search_fields = ['name']


class PersonAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']

    def delete_queryset(self, request, queryset):
        for person in queryset:
            if Media.objects.filter(authors=person).exists():
                message = f'Não foi possível efetuar a exclusão porque a pessoa {person} está relacionada a uma mídia.'
                messages.error(request, message)
                return 
        
        super().delete_queryset(request, queryset)


    def delete_model(self, request, obj):
        if Media.objects.filter(authors=obj).exists():
            message = 'Não foi possível efetuar a exclusão porque esta pessoa está relacionada a uma mídia.'
            self.message_user(request, message, messages.ERROR)
            return 
        
        obj.delete()


class TaxonAdmin(TranslationAdmin):
    list_display = ['name', 'aphia', 'rank', 'authority', 'status', 'is_valid',
                    'valid_taxon', 'parent', 'timestamp']
    list_filter = ['is_valid', 'timestamp', 'rank']
    search_fields = ['name', 'authority']
    readonly_fields = ['timestamp']


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'doi', 'citation']
    search_fields = ['name', 'citation']


class TourAdmin(TranslationAdmin):
    list_display = ['id', 'name', 'is_public', 'pub_date', 'timestamp']
    filter_horizontal = ['media', 'references']
    readonly_fields = ['pub_date', 'timestamp']


# Regular models.
admin.site.register(Stats)
admin.site.register(ModifiedMedia)

# Translation models.
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CatAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Taxon, TaxonAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Curation, CurationAdmin)

admin.site.empty_value_display = ' --- '