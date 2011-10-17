# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from meta.models import *
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from itertools import chain


class LatestMedia(Feed):
    description_template = 'feeds/media_post.html'
    author_name = 'Cifonauta'
    author_email = 'cebimar@usp.br'
    author_link = 'http://cifonauta.cebimar.usp.br/'
    categories = (_('biologia marinha'), _('fotos'), _('vídeos'), 
            _('biologia'))
    feed_copyright = _(
            'Centro de Biologia Marinha da Universidade de São Paulo')

    def get_object(self, request, type='all'):
        return type

    def title(self, obj):
        if obj == 'all':
            return _('Cifonauta: últimas fotos e vídeos')
        elif obj == 'photos':
            return _('Cifonauta: últimas fotos')
        elif obj == 'videos':
            return _('Cifonauta: últimos vídeos')
        else:
            return None

    def link(self, obj):
        if obj == 'all':
            return '/feed/latest/all/'
        elif obj == 'photos':
            return '/feed/latest/photos/'
        elif obj == 'videos':
            return '/feed/latest/videos/'
        else:
            return None

    def description(self, obj):
        if obj == 'all':
            return _('Fotos e vídeos recentes do banco de imagens Cifonauta.')
        elif obj == 'photos':
            return _('Fotos recentes do banco de imagens Cifonauta.')
        elif obj == 'videos':
            return _('Vídeos recentes do banco de imagens Cifonauta.')
        else:
            return None

    def items(self, obj):
        if obj == 'all':
            results = chain(
                    Image.objects.filter(is_public=True).order_by('-pub_date')[:10],
                    Video.objects.filter(is_public=True).order_by('-pub_date')[:10],
                    )
            return sorted(results, key=lambda x: x.pub_date,
                    reverse=True)
        elif obj == 'photos':
            return Image.objects.filter(is_public=True).order_by('-pub_date')[:20]
        elif obj == 'videos':
            return Video.objects.filter(is_public=True).order_by('-pub_date')[:20]
        else:
            return None

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


class MetaMedia(Feed):
    description_template = 'feeds/media_post.html'
    author_name = 'Cifonauta'
    author_email = 'cebimar@usp.br'
    author_link = 'http://cifonauta.cebimar.usp.br/'
    categories = (_('biologia marinha'), _('fotos'), _('vídeos'), 
            _('biologia'))
    feed_copyright = _(
            'Centro de Biologia Marinha da Universidade de São Paulo')

    def get_object(self, request, field, slug, type='all'):
        keywords = {'slug': slug}
        model = eval('get_object_or_404(%s, **%s)' % (field.capitalize(), keywords))
        obj = {
                'instance': model,
                'field': field,
                'slug': slug,
                'type': type,
                }
        return obj

    def title(self, obj):
        if obj['type'] == 'all':
            return _('Cifonauta: fotos e vídeos (%(field)s=%(name)s)' % {
                'field': obj['field'], 'name': obj['instance'].name})
        elif obj['type'] == 'photos':
            return _('Cifonauta: apenas fotos (%(field)s=%(name)s)' % {
                'field': obj['field'], 'name': obj['instance'].name})
        elif obj['type'] == 'videos':
            return _('Cifonauta: apenas vídeos (%(field)s=%(name)s)' % {
                'field': obj['field'], 'name': obj['instance'].name})
        else:
            return None

    def link(self, obj):
        if obj['type'] == 'all':
            return '/%s/%s/feed/all/' % (obj['field'], obj['slug'])
        elif obj['type'] == 'photos':
            return '/%s/%s/feed/photos/' % (obj['field'], obj['slug'])
        elif obj['type'] == 'videos':
            return '/%s/%s/feed/videos/' % (obj['field'], obj['slug'])
        else:
            return None

    def description(self, obj):
        if obj['type'] == 'all':
            return _('Fotos e vídeos do banco de imagens Cifonauta com %(field)s=%(name)s.' % {'field': obj['field'], 'name': obj['instance'].name})
        elif obj['type'] == 'photos':
            return _('Fotos do banco de imagens Cifonauta com %(field)s=%(name)s.' % {'field': obj['field'], 'name': obj['instance'].name})
        elif obj['type'] == 'videos':
            return _('Vídeos do banco de imagens Cifonauta com %(field)s=%(name)s.' % {'field': obj['field'], 'name': obj['instance'].name})
        else:
            return None

    def items(self, obj):
        keywords = {obj['field']: obj['instance']}
        if obj['type'] == 'all':
            results = chain(
                    Image.objects.filter(**keywords).exclude(is_public=False).order_by('-pub_date')[:10],
                    Video.objects.filter(**keywords).exclude(is_public=False).order_by('-pub_date')[:10],
                    )
            return sorted(results, key=lambda x: x.pub_date,
                    reverse=True)
        elif obj['type'] == 'photos':
            return Image.objects.filter(**keywords).exclude(is_public=False).order_by('-pub_date')[:20]
        elif obj['type'] == 'videos':
            return Video.objects.filter(**keywords).exclude(is_public=False).order_by('-pub_date')[:20]
        else:
            return None

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


class LatestTours(Feed):
    description_template = 'feeds/tours.html'
    author_name = 'Cifonauta'
    author_email = 'cebimar@usp.br'
    author_link = 'http://cifonauta.cebimar.usp.br/'
    categories = (_('biologia marinha'), _('fotos'), _('vídeos'), 
            _('biologia'))
    feed_copyright = _(
            'Centro de Biologia Marinha da Universidade de São Paulo')
    title = _('Cifonauta: últimos tours')
    link = '/tours/feed/'
    description = _('Tours recentes do banco de imagens Cifonauta.')

    def items(self):
        return Tour.objects.filter(is_public=True).order_by('-pub_date')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    item_author_name = u'Cifonauta'

    def item_pubdate(self, item):
        return item.pub_date
