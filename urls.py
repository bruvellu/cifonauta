import os
from django.conf.urls.defaults import *
from meta.views import *
from meta.feeds import *
from meta.models import *

info_dict = {
        'queryset': Image.objects.all(),
        }

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

site_media = os.path.join(
        os.path.dirname(__file__), 'site_media'
        )

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = patterns('',
        (r'^$', main_page),
        (r'^comentarios/', include('django.contrib.comments.urls')),
        #(r'^feed/$', LatestMedia()),

        (r'^buscar/$', search_page),
        (r'^tags/$', tags_page),
        (r'^taxa/$', taxa_page),
        (r'^locais/$', places_page),
        (r'^blog/', include('articles.urls')),

        (r'^tag/$', tag_list_page),
        (r'^tag/(?P<slug>[\w\-]+)/$', tag_page),

        (r'^autor/$', author_list_page),
        url(r'^autor/(?P<slug>[^\d]+)/$', meta_page,
            extra(Author, 'author'), name='author_url'),

        (r'^taxon/$', taxon_list_page),
        url(r'^taxon/(?P<slug>[^\d]+)/$', meta_page,
            extra(Taxon, 'taxon'), name='taxon_url'),

        (r'^genero/$', genus_list_page),
        url(r'^genero/(?P<slug>[^\d]+)/$', meta_page,
            extra(Genus, 'genus'), name='genus_url'),

        (r'^especie/$', species_list_page),
        url(r'^especie/(?P<slug>[^\d]+)/$', meta_page,
            extra(Species, 'species'), name='species_url'),

        (r'^tamanho/$', size_list_page),
        url(r'^tamanho/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Size, 'size'), name='size_url'),

        (r'^local/$', sublocation_list_page),
        url(r'^local/(?P<slug>[^\d]+)/$', meta_page,
            extra(Sublocation, 'sublocation'), name='sublocation_url'),

        (r'^cidade/$', city_list_page),
        url(r'^cidade/(?P<slug>[^\d]+)/$', meta_page,
            extra(City, 'city'), name='city_url'),

        (r'^estado/$', state_list_page),
        url(r'^estado/(?P<slug>[^\d]+)/$', meta_page,
            extra(State, 'state'), name='state_url'),

        (r'^pais/$', country_list_page),
        url(r'^pais/(?P<slug>[^\d]+)/$', meta_page,
            extra(Country, 'country'), name='country_url'),

        url(r'^imagem/(\d+)/$', image_page, name='image_url'),
        url(r'^video/(\d+)/$', video_page, name='video_url'),
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
