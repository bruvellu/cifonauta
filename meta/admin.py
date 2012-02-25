from meta import models
from django.contrib import admin

admin.site.register(models.Image)
admin.site.register(models.Video)
admin.site.register(models.Author)
admin.site.register(models.Tag)
admin.site.register(models.TagCategory)
admin.site.register(models.Taxon)
admin.site.register(models.Size)
admin.site.register(models.Source)
admin.site.register(models.Rights)
admin.site.register(models.Sublocation)
admin.site.register(models.City)
admin.site.register(models.State)
admin.site.register(models.Country)
admin.site.register(models.Reference)
admin.site.register(models.Tour)
admin.site.register(models.TourPosition)




#class ImageProxy(models.Image):
#    class Meta:
#        proxy = True
#
#
#class ImageAdmin(admin.ModelAdmin):
#    list_display = ('title', 'caption', 'caption_en', 'notes')
#    #ordering = ('title',)
#    #search_fields = ('caption',)
#    #list_filter = ('caption',)
#    
#admin.site.register(ImageProxy, ImageAdmin)
#
#import inspect, transmeta
#for name, M in inspect.getmembers(models):
#    if inspect.isclass(M):
#        continue
#        fields = transmeta.get_all_translatable_fields(M)
#        if fields:
#            pass