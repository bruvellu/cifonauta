# -*- coding: utf-8 -*-
import os
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
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

ONE_HOUR = 60 * 60
#24h = 60 * 60 * 24

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = patterns('',
        (r'^$', cache_page(main_page, ONE_HOUR)),
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
        #(r'^feedback/$', feedback_page),
        (r'^fixtaxa/$', fixtaxa_page),
        (r'^fixmedia/$', fixmedia_page),
        # Menu
        (r'^blog/', include('articles.urls')),
        url(r'^search/$', search_page, name='search_url'),
        url(r'^organization/$', cache_page(org_page, ONE_HOUR), 
            name='org_url'),
        url(r'^tags/$', cache_page(tags_page, ONE_HOUR), name='tags_url'),
        url(r'^taxa/$', cache_page(taxa_page, ONE_HOUR), name='taxa_url'),
        url(r'^places/$', cache_page(places_page, ONE_HOUR), 
            name='places_url'),
        url(r'^authors/$', cache_page(authors_page, ONE_HOUR), 
            name='authors_url'),
        url(r'^literature/$', cache_page(refs_page, ONE_HOUR), 
            name='refs_url'),
        url(r'^tours/$', cache_page(tours_page, ONE_HOUR), name='tours_url'),
        # Tests
        (r'^test/empty/$', empty_page),
        (r'^test/static/$', static_page),
        (r'^test/dynamic/$', dynamic_page),

        # XXX Padronizar syntax de passar argumentos para views?
        url(r'^tag/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Tag, 'tag'), name='tag_url'),
        url(r'^author/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Author, 'author'), name='author_url'),
        url(r'^source/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Source, 'source'), name='source_url'),
        url(r'^taxon/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Taxon, 'taxon'), name='taxon_url'),
        url(r'^size/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Size, 'size'), name='size_url'),
        url(r'^place/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Sublocation, 'sublocation'), name='sublocation_url'),
        url(r'^city/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(City, 'city'), name='city_url'),
        url(r'^state/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(State, 'state'), name='state_url'),
        url(r'^country/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Country, 'country'), name='country_url'),
        url(r'^reference/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_HOUR),
            extra(Reference, 'reference'), name='reference_url'),

        url(r'^tour/(?P<slug>[^\d]+)/$', cache_page(tour_page, ONE_HOUR), 
                name='tour_url'),
        url(r'^photo/(\d+)/$', cache_page(photo_page, ONE_HOUR), 
                name='image_url'),
        url(r'^video/(\d+)/$', cache_page(video_page, ONE_HOUR), name='video_url'),
        url(r'^embed/(\d+)/$', cache_page(embed_page, ONE_HOUR), name='embed_url'),

        # Admin
        (r'^admin/', include(admin.site.urls)),
        # Site media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': site_media}),
)
