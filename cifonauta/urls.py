import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from django.urls import include, path
from meta.models import Media
import debug_toolbar

#admin.autodiscover()

#ONE_HOUR = 60 * 60                  # 3600
#HALF_DAY = 60 * 60 * 12             # 43200
#ONE_DAY = 60 * 60 * 24              # 86400
#ONE_WEEK = 60 * 60 * 24 * 7         # 604800
#HALF_MONTH = 60 * 60 * 24 * 15      # 1296000
#ONE_MONTH = 60 * 60 * 24 * 30       # 2592000
#HALF_YEAR = 60 * 60 * 24 * 30 * 6   # 15552000
#ONE_YEAR = 60 * 60 * 24 * 30 * 12   # 31104000

# Sitemaps
media_dict = {'queryset': Media.objects.filter(is_public=True), 'date_field': 'timestamp'}
# photo_dict = {'queryset': Image.objects.filter(is_public=True), 'date_field': 'timestamp'}
# video_dict = {'queryset': Video.objects.filter(is_public=True), 'date_field': 'timestamp'}
# tour_dict = {'queryset': Tour.objects.filter(is_public=True), 'date_field': 'timestamp'}
# taxon_dict = {'queryset': Taxon.objects.all()}
# tag_dict = {'queryset': Tag.objects.all()}
# place_dict = {'queryset': Sublocation.objects.all()}
# city_dict = {'queryset': City.objects.all()}
# state_dict = {'queryset': State.objects.all()}
# country_dict = {'queryset': Country.objects.all()}
# author_dict = {'queryset': Author.objects.all()}
# source_dict = {'queryset': Source.objects.all()}
# reference_dict = {'queryset': Reference.objects.all()}

sitemaps = {
    'media': GenericSitemap(media_dict, priority=0.7, changefreq='weekly'),
    # 'flatpages': FlatPageSitemap,
    # 'blog': GenericSitemap(blog_dict, priority=0.4, changefreq='monthly'),
    # 'photos': GenericSitemap(photo_dict, priority=0.7, changefreq='weekly'),
    # 'videos': GenericSitemap(video_dict, priority=0.7, changefreq='weekly'),
    # 'tours': GenericSitemap(tour_dict, priority=0.8, changefreq='monthly'),
    # 'taxa': GenericSitemap(taxon_dict, priority=1.0, changefreq='weekly'),
    # 'tags': GenericSitemap(tag_dict, priority=0.8, changefreq='weekly'),
    # 'places': GenericSitemap(place_dict, priority=0.8, changefreq='weekly'),
    # 'cities': GenericSitemap(city_dict, priority=0.6, changefreq='monthly'),
    # 'states': GenericSitemap(state_dict, priority=0.4, changefreq='monthly'),
    # 'countries': GenericSitemap(country_dict, priority=0.4, changefreq='monthly'),
    # 'authors': GenericSitemap(author_dict, priority=0.8, changefreq='weekly'),
    # 'sources': GenericSitemap(source_dict, priority=0.7, changefreq='weekly'),
    # 'references': GenericSitemap(reference_dict, priority=0.5, changefreq='monthly'),
}


urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('admin/', admin.site.urls),
        path('', include('django.contrib.auth.urls')),
        path('', include('meta.urls')),
        path('rosetta/', include('rosetta.urls')),
        path('i18n/', include('django.conf.urls.i18n')),
        path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap')

        # Sitemaps
        #url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

        # Site media
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
