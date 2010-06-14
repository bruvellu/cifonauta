import os
from django.conf.urls.defaults import *
from meta.views import *
from meta.models import Image

info_dict = {
        'queryset': Image.objects.all(),
        }

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

site_media = os.path.join(
        os.path.dirname(__file__), 'site_media'
        )

urlpatterns = patterns('',
        (r'^$', main_page),
        (r'^comentarios/', include('django.contrib.comments.urls')),

        (r'^buscar/$', search_page),

        (r'^tags/$', tags_page),

        (r'^tag/$', tag_list_page),
        (r'^tag/([^\d]+)/$', tag_page),

        (r'^autor/$', author_list_page),
        (r'^autor/([^\d]+)/$', author_page),

        (r'^taxa/$', taxa_page),

        (r'^taxon/$', taxon_list_page),
        (r'^taxon/([^\d]+)/$', taxon_page),

        (r'^genero/$', genus_list_page),
        (r'^genero/([^\d]+)/$', genus_page),

        (r'^especie/$', species_list_page),
        (r'^especie/([^\d]+)/$', species_page),

        (r'^tamanho/$', size_list_page),
        (r'^tamanho/([^\d]+)/$', size_page),

        (r'^locais/$', places_page),

        (r'^local/$', sublocation_list_page),
        (r'^local/([^\d]+)/$', sublocation_page),

        (r'^cidade/$', city_list_page),
        (r'^cidade/([^\d]+)/$', city_page),

        (r'^estado/$', state_list_page),
        (r'^estado/([^\d]+)/$', state_page),

        (r'^pais/$', country_list_page),
        (r'^pais/([^\d]+)/$', country_page),

        (r'^imagem/([0-9]+)/$', image_page),
        (r'^video/([0-9]+)/$', video_page),
        # Admin
        (r'^admin/', include(admin.site.urls)),
        # Site media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': site_media}),

    # Example:
    # (r'^weblarvae/', include('weblarvae.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)