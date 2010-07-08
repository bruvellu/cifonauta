# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from meta.models import *

class LatestMedia(Feed):
    description_template = 'feeds/media_post.html'
    title = u'Últimas imagens | CEBIMar USP'
    link = u'/feed/'
    description = 'Imagens e vídeos recentes do CEBIMar USP.'
    author_name = 'Cifonauta'
    author_email = 'cebimar@usp.br'
    author_link = 'http://www.usp.br/cbm/'
    categories = ('biologia marinha', 'fotos', 'vídeos', 'biologia')
    feed_copyright = 'Centro de Biologia Marinha da Universidade de São Paulo'

    def items(self):
        return Image.objects.order_by('-pub_date')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.caption

    def item_author(self, item):
        return item.author.name

    def item_pubdate(self, item):
        return item.pub_date

    def item_categories(self, item):
        return item.tag_set.all()
