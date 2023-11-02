from django.contrib import admin, messages
from django.contrib.flatpages.models import FlatPage
from meta.models import *
from modeltranslation.admin import TranslationAdmin
from .forms import CuradoriaAdminForm

class CuradoriaAdmin(admin.ModelAdmin):
    form = CuradoriaAdminForm
    autocomplete_fields = ('specialists', 'curators', 'taxons')

# Translation admin.
class FlatPageAdmin(TranslationAdmin):
    pass


class MediaAdmin(TranslationAdmin):
    list_display = ('title', 'status', 'highlight', 'file', 'user', 'pub_date')
    list_filter = ('is_public', 'highlight', 'timestamp', 'authors', 'tags', 'taxon', 'specialists')

class ModifiedMediaAdmin(admin.ModelAdmin):
    list_display = ('title',)

class TagAdmin(TranslationAdmin):
    list_display = ('name', 'description', 'category')
    list_filter = ('category',)
    filter_horizontal = ('media_files',)
    search_fields = ['name', 'description']


class CatAdmin(TranslationAdmin):
    pass


class CityAdmin(TranslationAdmin):
    pass


class StateAdmin(TranslationAdmin):
    pass


class CountryAdmin(TranslationAdmin):
    pass


class PersonAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    search_fields = ('name', 'email')

    def delete_queryset(self, request, queryset):
        for person in queryset:
            if Media.objects.filter(co_author=person).exists():
                message = f"Não foi possível efetuar a exclusão porque a pessoa {person} está relacionada a uma mídia."
                messages.error(request, message)
                return 
        
        super().delete_queryset(request, queryset)


    def delete_model(self, request, obj):
        if Media.objects.filter(co_author=obj).exists():
            message = "Não foi possível efetuar a exclusão porque esta pessoa está relacionada a uma mídia."
            self.message_user(request, message, messages.ERROR)
            return 
        
        obj.delete()


class TaxonAdmin(TranslationAdmin):
    list_display = ('name', 'aphia', 'rank', 'authority', 'status', 'is_valid', 'valid_taxon', 'parent', 'timestamp')
    list_filter = ('is_valid', 'timestamp', 'rank')
    filter_horizontal = ('media',)
    search_fields = ['name', 'authority']


class ReferenceAdmin(admin.ModelAdmin):
    filter_horizontal = ('media',)


class TourAdmin(TranslationAdmin):
    filter_horizontal = ('media', 'references',)


# Regular models.
admin.site.register(Location)
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
admin.site.register(Person, PersonAdmin)
admin.site.register(Taxon, TaxonAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Curadoria, CuradoriaAdmin)
admin.site.register(ModifiedMedia, ModifiedMediaAdmin)
admin.site.register(LoadedMedia)
