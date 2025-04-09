from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views
from django.urls import include, path
from django.views.generic.base import TemplateView
from .sitemaps import PaginatedSitemap

from meta.models import (
    Media,
    Person,
    Tag,
    Taxon,
    Location,
    City,
    State,
    Country,
    Tour,
    Reference,
)

# Generate paginated sitemaps for different model querysets
sitemaps = {
    "media": PaginatedSitemap(
        {
            "queryset": Media.objects.filter(is_public=True),
            "date_field": "date_modified",
        },
        priority=0.9,
        changefreq="daily",
    ),
    "persons": PaginatedSitemap(
        {"queryset": Person.objects.filter(media_as_author__isnull=False).distinct()},
        priority=0.8,
        changefreq="weekly",
    ),
    "tags": PaginatedSitemap(
        {"queryset": Tag.objects.filter(media__isnull=False).distinct()},
        priority=0.8,
        changefreq="weekly",
    ),
    "taxa": PaginatedSitemap(
        {"queryset": Taxon.objects.all()}, priority=1.0, changefreq="weekly"
    ),
    "locations": PaginatedSitemap(
        {"queryset": Location.objects.filter(media__isnull=False).distinct()},
        priority=0.7,
        changefreq="weekly",
    ),
    "cities": PaginatedSitemap(
        {"queryset": City.objects.filter(media__isnull=False).distinct()},
        priority=0.6,
        changefreq="monthly",
    ),
    "states": PaginatedSitemap(
        {"queryset": State.objects.filter(media__isnull=False).distinct()},
        priority=0.4,
        changefreq="monthly",
    ),
    "countries": PaginatedSitemap(
        {"queryset": Country.objects.filter(media__isnull=False).distinct()},
        priority=0.4,
        changefreq="monthly",
    ),
    "tours": PaginatedSitemap(
        {"queryset": Tour.objects.filter(is_public=True), "date_field": "timestamp"},
        priority=0.8,
        changefreq="monthly",
    ),
    "references": PaginatedSitemap(
        {"queryset": Reference.objects.all()}, priority=0.7, changefreq="monthly"
    ),
    "flatpages": FlatPageSitemap,
}

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("", include("meta.urls")),
    path("rosetta/", include("rosetta.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", views.index, {"sitemaps": sitemaps}),
    path(
        "sitemap-<section>.xml",
        views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
