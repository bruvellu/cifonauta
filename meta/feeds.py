# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from meta.models import *

class LatestMedia(Feed):
    title = u'Banco de Imagens CEBIMar/USP | Últimas'
    link = u'/feed/'
    description = 'Últimas imagens e vídeos do CEBIMar/USP.'

    def items(self):
        return Image.objects.order_by('-pub_date')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.caption

    def item_author(self, item):
        return item.author.name
