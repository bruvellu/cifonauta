# -*- coding: utf-8 -*-
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
        (r'^feed/$', LatestMedia()),

        (r'^buscar/$', search_page),
        (r'^tags/$', tags_page),
        (r'^taxa/$', taxa_page),
        (r'^locais/$', places_page),
        (r'^blog/', include('articles.urls')),
        (r'^sobre/organizacao/$', org_page),

        url(r'^tag/$', meta_list_page,
            {'model': Tag, 'plural': u'Marcadores'}),
        url(r'^tag/(?P<slug>[\w\-]+)/$', tag_page,
            name='tag_url'),

        url(r'^autor/$', meta_list_page,
            {'model': Author, 'plural': u'Autores'}),
        url(r'^autor/(?P<slug>[^\d]+)/$', meta_page,
            extra(Author, 'author'), name='author_url'),

        url(r'^taxon/$', meta_list_page,
            {'model': Taxon, 'plural': u'Táxons'}),
        url(r'^taxon/(?P<slug>[^\d]+)/$', meta_page,
            extra(Taxon, 'taxon'), name='taxon_url'),

        url(r'^genero/$', meta_list_page,
            {'model': Genus, 'plural': u'Gêneros'}),
        url(r'^genero/(?P<slug>[^\d]+)/$', meta_page,
            extra(Genus, 'genus'), name='genus_url'),

        url(r'^especie/$', meta_list_page,
            {'model': Species, 'plural': u'Espécies'}),
        url(r'^especie/(?P<genus>[^\d]+)-(?P<slug>[^\d]+)/$', meta_page,
            extra(Species, 'species'), name='species_url'),

        url(r'^tamanho/$', meta_list_page,
            {'model': Size, 'plural': u'Tamanhos'}),
        url(r'^tamanho/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Size, 'size'), name='size_url'),

        url(r'^local/$', meta_list_page,
            {'model': Sublocation, 'plural': u'Locais'}),
        url(r'^local/(?P<slug>[^\d]+)/$', meta_page,
            extra(Sublocation, 'sublocation'), name='sublocation_url'),

        url(r'^cidade/$', meta_list_page,
            {'model': City, 'plural': u'Cidades'}),
        url(r'^cidade/(?P<slug>[^\d]+)/$', meta_page,
            extra(City, 'city'), name='city_url'),

        url(r'^estado/$', meta_list_page,
            {'model': State, 'plural': u'Estados'}),
        url(r'^estado/(?P<slug>[^\d]+)/$', meta_page,
            extra(State, 'state'), name='state_url'),

        url(r'^pais/$', meta_list_page,
            {'model': Country, 'plural': u'Países'}),
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
