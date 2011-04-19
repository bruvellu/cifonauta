# -*- coding: utf-8 -*-
import os
from django.conf.urls.defaults import *
from meta.views import *
from meta.feeds import *
from meta.models import *

from django import template
template.add_to_builtins('weblarvae.meta.templatetags.extra_tags')

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
        (r'^i18n/', include('django.conf.urls.i18n')),
        (r'^comentarios/', include('django.contrib.comments.urls')),
        # Feeds
        (r'^feed/latest/$', LatestMedia()),
        (r'^feed/latest/(?P<type>[^\d]+)/$', LatestMedia()),
        # Auth
        (r'^login/$', 'django.contrib.auth.views.login'),
        (r'^logout/$', 'django.contrib.auth.views.logout'),
        # Translate
        (r'^traduzir/$', translate_page),
        (r'^traduzir/apps/', include('rosetta.urls')),
        (r'^traduzir/models/', include('datatrans.urls')),
        # Manage
        (r'^privadas/$', hidden_page),
        (r'^feedback/$', feedback_page),
        (r'^fixtaxa/$', fixtaxa_page),
        # Menu
        (r'^organizacao/$', org_page),
        (r'^buscar/$', search_page),
        (r'^blog/', include('articles.urls')),
        (r'^tags/$', tags_page),
        (r'^taxa/$', taxa_page),
        (r'^locais/$', places_page),
        (r'^autores/$', authors_page),
        (r'^literatura/$', refs_page),
        (r'^tours/$', tours_page),
        # Tests
        (r'^teste/vazio/$', empty_page),
        (r'^teste/estatico/$', static_page),
        (r'^teste/dinamico/$', dynamic_page),

        # XXX Padronizar syntax de passar argumentos para views?
        url(r'^tag/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Tag, 'tag'), name='tag_url'),
        url(r'^autor/(?P<slug>[^\d]+)/$', meta_page,
            extra(Author, 'author'), name='author_url'),
        url(r'^especialista/(?P<slug>[^\d]+)/$', meta_page,
            extra(Source, 'source'), name='source_url'),
        url(r'^taxon/(?P<slug>[^\d]+)/$', meta_page,
            extra(Taxon, 'taxon'), name='taxon_url'),
        url(r'^tamanho/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Size, 'size'), name='size_url'),
        url(r'^local/(?P<slug>[^\d]+)/$', meta_page,
            extra(Sublocation, 'sublocation'), name='sublocation_url'),
        url(r'^cidade/(?P<slug>[^\d]+)/$', meta_page,
            extra(City, 'city'), name='city_url'),
        url(r'^estado/(?P<slug>[^\d]+)/$', meta_page,
            extra(State, 'state'), name='state_url'),
        url(r'^pais/(?P<slug>[^\d]+)/$', meta_page,
            extra(Country, 'country'), name='country_url'),
        url(r'^referencia/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Reference, 'reference'), name='reference_url'),
        url(r'^tour/(?P<slug>[^\d]+)/$', tour_page, name='tour_url'),

        url(r'^foto/(\d+)/$', photo_page, name='image_url'),
        url(r'^video/(\d+)/$', video_page, name='video_url'),
        url(r'^embed/(\d+)/$', embed_page, name='embed_url'),

        # Admin
        (r'^admin/', include(admin.site.urls)),
        # Site media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': site_media}),

        # XXX Lista com metadados, não utilizado. Será útil algum dia?
        url(r'^tag/$', meta_list_page,
            {'model': Tag, 'plural': u'Marcadores'}),
        url(r'^autor/$', meta_list_page,
            {'model': Author, 'plural': u'Autores'}),
        url(r'^especialista/$', meta_list_page,
            {'model': Source, 'plural': u'Especialista'}),
        url(r'^taxon/$', meta_list_page,
            {'model': Taxon, 'plural': u'Táxons'}),
        url(r'^tamanho/$', meta_list_page,
            {'model': Size, 'plural': u'Tamanhos'}),
        url(r'^local/$', meta_list_page,
            {'model': Sublocation, 'plural': u'Locais'}),
        url(r'^cidade/$', meta_list_page,
            {'model': City, 'plural': u'Cidades'}),
        url(r'^estado/$', meta_list_page,
            {'model': State, 'plural': u'Estados'}),
        url(r'^pais/$', meta_list_page,
            {'model': Country, 'plural': u'Países'}),

    # Example:
    # (r'^weblarvae/', include('weblarvae.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
