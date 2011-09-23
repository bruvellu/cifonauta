# -*- coding: utf-8 -*-
import os
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from meta.views import *
from meta.feeds import *
from meta.models import *

from django.conf import settings

from django import template
template.add_to_builtins('weblarvae.meta.templatetags.extra_tags')

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Dajaxice requirement.
from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

site_media = os.path.join(
        os.path.dirname(__file__), 'site_media'
        )

ONE_HOUR = 60 * 60 #3600
HALF_DAY = 60 * 60 * 12 #43200
ONE_DAY = 60 * 60 * 24 #86400
ONE_WEEK = 60 * 60 * 24 * 7 #604800
HALF_MONTH = 60 * 60 * 24 * 15 #1296000
ONE_MONTH = 60 * 60 * 24 * 30 #2592000
HALF_YEAR = 60 * 60 * 24 * 30 * 6 #15552000
ONE_YEAR = 60 * 60 * 24 * 30 * 12 #31104000

def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = patterns('',
        (r'^$', cache_page(main_page, ONE_WEEK)),
        (r'^i18n/', include('django.conf.urls.i18n')),
        #(r'^comments/', include('django.contrib.comments.urls')),
        (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),

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
        url(r'^organization/$', cache_page(org_page, ONE_WEEK), 
            name='org_url'),
        url(r'^tags/$', cache_page(tags_page, ONE_WEEK), name='tags_url'),
        url(r'^taxa/$', cache_page(taxa_page, ONE_WEEK), name='taxa_url'),
        url(r'^places/$', cache_page(places_page, ONE_WEEK), 
            name='places_url'),
        url(r'^authors/$', cache_page(authors_page, ONE_WEEK), 
            name='authors_url'),
        url(r'^literature/$', cache_page(refs_page, ONE_WEEK), 
            name='refs_url'),
        url(r'^tours/$', cache_page(tours_page, ONE_WEEK), name='tours_url'),
        url(r'^press/$', press_page, name='press_url'),

        # Tests
        (r'^test/empty/$', empty_page),
        (r'^test/static/$', static_page),
        (r'^test/dynamic/$', dynamic_page),

        # XXX Padronizar syntax de passar argumentos para views?
        url(r'^tag/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Tag, 'tag'), name='tag_url'),
        url(r'^author/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Author, 'author'), name='author_url'),
        url(r'^source/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Source, 'source'), name='source_url'),
        url(r'^taxon/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Taxon, 'taxon'), name='taxon_url'),
        url(r'^size/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Size, 'size'), name='size_url'),
        url(r'^place/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Sublocation, 'sublocation'), name='sublocation_url'),
        url(r'^city/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(City, 'city'), name='city_url'),
        url(r'^state/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(State, 'state'), name='state_url'),
        url(r'^country/(?P<slug>[^\d]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Country, 'country'), name='country_url'),
        url(r'^reference/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_WEEK),
            extra(Reference, 'reference'), name='reference_url'),

        url(r'^tour/(?P<slug>[^\d]+)/$', cache_page(tour_page, ONE_WEEK), 
                name='tour_url'),
        url(r'^photo/(\d+)/$', cache_page(photo_page, ONE_WEEK), 
                name='image_url'),
        url(r'^video/(\d+)/$', cache_page(video_page, ONE_WEEK), name='video_url'),
        url(r'^embed/(\d+)/$', cache_page(embed_page, ONE_WEEK), name='embed_url'),

        # Admin
        (r'^admin/', include(admin.site.urls)),
        # Site media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': site_media}),
)
