import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views
from django.contrib.sitemaps import GenericSitemap
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.urls import include, path
from meta.models import Media, Person, Tag, Taxon, Location, City, State, Country, Tour

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
person_dict = {'queryset': Person.objects.all()}
tag_dict = {'queryset': Tag.objects.all()}
taxon_dict = {'queryset': Taxon.objects.all()}
location_dict = {'queryset': Location.objects.all()}
city_dict = {'queryset': City.objects.all()}
state_dict = {'queryset': State.objects.all()}
country_dict = {'queryset': Country.objects.all()}
tour_dict = {'queryset': Tour.objects.filter(is_public=True), 'date_field': 'timestamp'}
# reference_dict = {'queryset': Reference.objects.all()}

sitemaps = {
    'media': GenericSitemap(media_dict, priority=0.7, changefreq='weekly'),
    'persons': GenericSitemap(person_dict, priority=0.9, changefreq='weekly'),
    'tags': GenericSitemap(tag_dict, priority=0.8, changefreq='weekly'),
    'taxa': GenericSitemap(taxon_dict, priority=1.0, changefreq='weekly'),
    'locations': GenericSitemap(location_dict, priority=0.8, changefreq='weekly'),
    'cities': GenericSitemap(city_dict, priority=0.6, changefreq='monthly'),
    'states': GenericSitemap(state_dict, priority=0.4, changefreq='monthly'),
    'countries': GenericSitemap(country_dict, priority=0.4, changefreq='monthly'),
    'tours': GenericSitemap(tour_dict, priority=0.8, changefreq='monthly'),
    'flatpages': FlatPageSitemap,
    # 'references': GenericSitemap(reference_dict, priority=0.5, changefreq='monthly'),
}


urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
        path('admin/', admin.site.urls),
        path('user/', include('user.urls')),
        path('', include('django.contrib.auth.urls')),
        path('', include('meta.urls')),
        path('rosetta/', include('rosetta.urls')),
        path('i18n/', include('django.conf.urls.i18n')),
        path('sitemap.xml', views.index, {'sitemaps': sitemaps}),
        path('sitemap-<section>.xml', views.sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
        # Site media
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
