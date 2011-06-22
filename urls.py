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
        #(r'^comments/', include('django.contrib.comments.urls')),
        # Feeds
        (r'^feed/latest/$', LatestMedia()),
        (r'^feed/latest/(?P<type>[^\d]+)/$', LatestMedia()),
        (r'^(?P<field>[^\d]+)/(?P<slug>[\w\-]+)/feed/$', MetaMedia()),
        (r'^(?P<field>[^\d]+)/(?P<slug>[\w\-]+)/feed/(?P<type>[^\d]+)/$', MetaMedia()),
        (r'^tours/feed/$', LatestTours()),

        # Auth
        (r'^login/$', 'django.contrib.auth.views.login'),
        (r'^logout/$', 'django.contrib.auth.views.logout'),
        # Translate
        (r'^translate/$', translate_page),
        (r'^translate/apps/', include('rosetta.urls')),
        (r'^translate/models/', include('datatrans.urls')),
        # Manage
        (r'^private/$', hidden_page),
        (r'^feedback/$', feedback_page),
        (r'^fixtaxa/$', fixtaxa_page),
        (r'^fixmedia/$', fixmedia_page),
        # Menu
        (r'^organization/$', org_page),
        (r'^search/$', search_page),
        (r'^blog/', include('articles.urls')),
        (r'^tags/$', tags_page),
        (r'^taxa/$', taxa_page),
        (r'^places/$', places_page),
        (r'^authors/$', authors_page),
        (r'^literature/$', refs_page),
        (r'^tours/$', tours_page),
        # Tests
        (r'^test/empty/$', empty_page),
        (r'^test/static/$', static_page),
        (r'^test/dynamic/$', dynamic_page),

        # XXX Padronizar syntax de passar argumentos para views?
        url(r'^tag/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Tag, 'tag'), name='tag_url'),
        url(r'^author/(?P<slug>[^\d]+)/$', meta_page,
            extra(Author, 'author'), name='author_url'),
        url(r'^source/(?P<slug>[^\d]+)/$', meta_page,
            extra(Source, 'source'), name='source_url'),
        url(r'^taxon/(?P<slug>[^\d]+)/$', meta_page,
            extra(Taxon, 'taxon'), name='taxon_url'),
        url(r'^size/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Size, 'size'), name='size_url'),
        url(r'^place/(?P<slug>[^\d]+)/$', meta_page,
            extra(Sublocation, 'sublocation'), name='sublocation_url'),
        url(r'^city/(?P<slug>[^\d]+)/$', meta_page,
            extra(City, 'city'), name='city_url'),
        url(r'^state/(?P<slug>[^\d]+)/$', meta_page,
            extra(State, 'state'), name='state_url'),
        url(r'^country/(?P<slug>[^\d]+)/$', meta_page,
            extra(Country, 'country'), name='country_url'),
        url(r'^reference/(?P<slug>[\w\-]+)/$', meta_page,
            extra(Reference, 'reference'), name='reference_url'),
        url(r'^tour/(?P<slug>[^\d]+)/$', tour_page, name='tour_url'),

        url(r'^photo/(\d+)/$', photo_page, name='image_url'),
        url(r'^video/(\d+)/$', video_page, name='video_url'),
        url(r'^embed/(\d+)/$', embed_page, name='embed_url'),

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
