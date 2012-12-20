# -*- coding: utf-8 -*-
import os
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from meta.views import *
from meta.feeds import *
from meta.models import *
from articles.models import Article

from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap

from django.conf import settings

from django import template
template.add_to_builtins('meta.templatetags.extra_tags')

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Dajaxice requirement.
from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

site_media = os.path.join(
        os.path.dirname(__file__), 'site_media'
        )

ONE_HOUR = 60 * 60                  # 3600
HALF_DAY = 60 * 60 * 12             # 43200
ONE_DAY = 60 * 60 * 24              # 86400
ONE_WEEK = 60 * 60 * 24 * 7         # 604800
HALF_MONTH = 60 * 60 * 24 * 15      # 1296000
ONE_MONTH = 60 * 60 * 24 * 30       # 2592000
HALF_YEAR = 60 * 60 * 24 * 30 * 6   # 15552000
ONE_YEAR = 60 * 60 * 24 * 30 * 12   # 31104000

# Sitemaps
blog_dict = {'queryset': Article.objects.all(), 'date_field': 'publish_date'}
photo_dict = {'queryset': Image.objects.filter(is_public=True), 'date_field': 'timestamp'}
video_dict = {'queryset': Video.objects.filter(is_public=True), 'date_field': 'timestamp'}
tour_dict = {'queryset': Tour.objects.filter(is_public=True), 'date_field': 'timestamp'}
taxon_dict = {'queryset': Taxon.objects.all()}
tag_dict = {'queryset': Tag.objects.all()}
place_dict = {'queryset': Sublocation.objects.all()}
city_dict = {'queryset': City.objects.all()}
state_dict = {'queryset': State.objects.all()}
country_dict = {'queryset': Country.objects.all()}
author_dict = {'queryset': Author.objects.all()}
source_dict = {'queryset': Source.objects.all()}
reference_dict = {'queryset': Reference.objects.all()}

sitemaps = {
    'flatpages': FlatPageSitemap,
    'blog': GenericSitemap(blog_dict, priority=0.4, changefreq='monthly'),
    'photos': GenericSitemap(photo_dict, priority=0.7, changefreq='weekly'),
    'videos': GenericSitemap(video_dict, priority=0.7, changefreq='weekly'),
    'tours': GenericSitemap(tour_dict, priority=0.8, changefreq='monthly'),
    'taxa': GenericSitemap(taxon_dict, priority=1.0, changefreq='weekly'),
    'tags': GenericSitemap(tag_dict, priority=0.8, changefreq='weekly'),
    'places': GenericSitemap(place_dict, priority=0.8, changefreq='weekly'),
    'cities': GenericSitemap(city_dict, priority=0.6, changefreq='monthly'),
    'states': GenericSitemap(state_dict, priority=0.4, changefreq='monthly'),
    'countries': GenericSitemap(country_dict, priority=0.4, changefreq='monthly'),
    'authors': GenericSitemap(author_dict, priority=0.8, changefreq='weekly'),
    'sources': GenericSitemap(source_dict, priority=0.7, changefreq='weekly'),
    'references': GenericSitemap(reference_dict, priority=0.5, changefreq='monthly'),
}


def extra(model, field):
    return {'model_name': model, 'field': field}

urlpatterns = patterns('',
        (r'^$', cache_page(main_page, ONE_WEEK)),
        (r'^i18n/', include('django.conf.urls.i18n')),

        # Sitemaps
        (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

        # Dajax
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
        url(r'^press/$', cache_page(press_page, ONE_WEEK), name='press_url'),

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
        url(r'^place/(?P<slug>[\w\-]+)/$', cache_page(meta_page, ONE_WEEK),
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

        # AJAX Search suggestions
        (r'^ajax_search/', ajax_autocomplete),

        # Admin
        (r'^admin/', include(admin.site.urls)),
        # Site media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': site_media}),
)
