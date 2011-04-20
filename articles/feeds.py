# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse
from articles.models import Article, Tag
from django.utils.translation import ugettext_lazy as _

SITE = Site.objects.get_current()

# default to 24 hours for feed caching
FEED_TIMEOUT = getattr(settings, 'ARTICLE_FEED_TIMEOUT', 86400)

class LatestEntries(Feed):
    description_template = 'feeds/post.html'
    author_name = 'Cifonauta'
    author_email = 'cebimar@usp.br'
    author_link = 'http://cifonauta.cebimar.usp.br/'
    categories = (_('marine biology'), _('photos'), _('videos'), 
            _('biology'))
    feed_copyright = _(
            'Marine Biology Center of University of São Paulo')

    def title(self):
        return _('%s Articles' % SITE.name)

    def link(self):
        return reverse('articles_archive')

    def description(self):
        return _('Latest blog articles from Cifonauta image database.')

    def items(self):
        key = 'latest_articles'
        articles = cache.get(key)

        if articles is None:
            articles = list(Article.objects.live().order_by('-publish_date')[:15])
            cache.set(key, articles, FEED_TIMEOUT)

        return articles

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.rendered_content

    def item_author_name(self, item):
        return item.author.username

    def item_pubdate(self, item):
        return item.publish_date

    def item_categories(self, item):
        return [c.name for c in item.tags.all()] + [keyword.strip() for keyword in item.keywords.split(',')]
