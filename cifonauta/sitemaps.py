from django.contrib.sitemaps import GenericSitemap


# Subclass sitemap to set lower pagination limit
class PaginatedSitemap(GenericSitemap):
    limit = 2000
