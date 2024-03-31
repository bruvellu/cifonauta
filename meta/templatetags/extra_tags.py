# -*- coding: utf-8 -*-

import operator

from django import template
from django.apps import apps
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from meta.forms import *

register = template.Library()

# TODO: Cleanup this file...

main_ranks = [u'Reino', u'Filo', u'Classe', u'Ordem', u'Família', u'Gênero', u'Espécie', u'Kingdom', u'Phylum', u'Class', u'Order', u'Family', u'Genus', u'Species']

@register.inclusion_tag('metalist.html')
def print_metalist(metalist, field):
    '''Mostra lista de metadados com contador de imagens.'''
    return {'metalist': metalist, 'field': field}

@register.inclusion_tag('taxon_paths.html')
def taxon_paths(taxon):
    '''Mostra classificação de um táxon de forma linear.

    Exclui subrankings da lista.
    '''
    ancestors = [t for t in taxon.get_ancestors() if t.rank in main_ranks]
    return {'taxon': taxon, 'ancestors': ancestors}

@register.inclusion_tag('thumb_org.html', takes_context=True)
def print_thumb(context, field, obj):
    '''Generates random thumbnail for supplied metadata.'''
    Media = apps.get_model('meta', 'Media')
    media_url = context['MEDIA_URL']
    params = {field: obj, 'is_public': True}
    try:
        media = Media.objects.filter(**params).order_by('?')[0]
    except:
        media = ''
    return {'media': media, 'MEDIA_URL': media_url}


def slicer(query, media_id):
    '''Process queryset results.

    Discover the image index within the queryset, calculate and identify
    next/previous related images, and chop queryset to fit the 5 thumbnails of the
    linear browser.

    '''

    # Get image index within queryset.
    for index, item in enumerate(query):
        if item.id == media_id:
            media_index = index
            break
        else:
            continue

    # Calculate how many ahead and behind.
    ahead = len(query[media_index:]) - 1
    behind = len(query[:media_index])

    # Main object with relative positions.
    relative = {
        'ahead': ahead,
        'behind': behind,
        'current_index': media_index + 1,  # Relative indexes are non-pythonic.
        }

    # Total length of the queryset.
    size = len(query)

    # Matrix with conditionals for getting relative objects. First and last 2
    # are covered, others should not overlap, that is why media_index - value
    # should always be > 1.
    conditionals = (
        # conditional               field           index
        (media_index > 0,           'first1',       0),
        (media_index > 1,           'first2',       1),
        (media_index > 2,           'previous1',    media_index - 1),
        (media_index > 3,           'previous2',    media_index - 2),
        (media_index > 6,           'previous5',    media_index - 5),
        (media_index < size - 2,    'next1',        media_index + 1),
        (media_index < size - 3,    'next2',        media_index + 2),
        (media_index < size - 6,    'next5',        media_index + 5),
        (media_index < size - 1,    'last1',        size - 1),
        (media_index < size - 2,    'last2',        size - 2),
        )

    # Populate relative object only with available relative images.
    for cond, field, index in conditionals:
        if cond:
            relative[field] = {'index': index + 1, 'obj': query[index]}
        else:
            relative[field] = None

    # Standardize image to center of the index.
    if media_index < 2:
        media_index = 2

    # Slice full query to 5 images when necessary.
    if len(query) <= 5:
        rel_query = query
    else:
        rel_query = query[media_index - 2:media_index + 3]

    return rel_query, relative


def get_media_queryset(media, qobj):
    '''Returns queryset used in the linear browser.'''
    Media = apps.get_model('meta', 'Media')
    query = Media.objects.filter(qobj, is_public=True).order_by('id')
    return query

@register.inclusion_tag('related.html', takes_context=True)
def show_related(context, media, form, related):
    '''Usa metadados da imagem para encontrar imagens relacionadas.'''
    media_url = context['MEDIA_URL']
    # Limpa imagens relacionadas.
    rel_media = ''
    relative = ''
    # Transforma choices em dicionário.
    form_choices = form.fields['type'].choices
    choices = {}
    for c in form_choices:
        choices[c[0]] = c[1]

    # Se o choice escolhido no navegador for:
    if related == 'author':
        # Salva queryset para performance.
        authors = media.authors.all()
        if authors:
            qobj = Q()
            for meta in authors:
                # Adiciona parâmetros para futuro query usando Q.
                qobj.add(Q(authors=meta), Q.OR)
            if qobj.__len__():
                # Se objeto não estiver vazio, descobrir seu tipo (foto ou vídeo) e gerar o queryset.
                query = get_media_queryset(media, qobj)
                # Processar queryset para se adaptar ao navegador linear.
                rel_media, relative = slicer(query, media.id)
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == 'taxon':
        taxa = media.taxa.all()
        if taxa:
            qobj = Q()
            for meta in taxa:
                qobj.add(Q(taxa=meta), Q.OR)
            if qobj.__len__():
                query = get_media_queryset(media, qobj)
                rel_media, relative = slicer(query, media.id)
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == 'location':
        if media.location:
            qobj = Q(location=media.location_id)
            query = get_media_queryset(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == 'city':
        if media.city:
            qobj = Q(city=media.city_id)
            query = get_media_queryset(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == 'state':
        if media.state:
            qobj = Q(state=media.state_id)
            query = get_media_queryset(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == 'country':
        if media.country:
            qobj = Q(country=media.country_id)
            query = get_media_queryset(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    else:
        rel_media = ''

    # Mostra os valores avaliados para o navegador linear.
    if related == 'author':
        crumbs = authors
    elif related == 'taxon':
        crumbs = taxa
    else:
        #XXX Necessário forçar a criação de uma lista.
        crumbs = [eval('media.%s' % related)]

    current = media

    return {'current': current, 'rel_media': rel_media, 'relative': relative, 'form': form, 'related': related, 'type': choices[related], 'crumbs': crumbs, 'MEDIA_URL': media_url}

@register.inclusion_tag('stats.html')
def show_stats():
    '''Generates the stats line in the header.'''
    # Load model.
    Stats = apps.get_model('meta', 'Stats')
    cifo = Stats.objects.get(site='cifonauta')

    return {'photos': cifo.photos, 'videos': cifo.videos, 'species':
            cifo.species, 'locations': cifo.locations, 'tags': cifo.tags}

@register.inclusion_tag('tree.html')
def show_tree(current=None):
    '''Passa objeto para gerar árvore.

    Usa o recursetree do MPTT no template para gerar a árvore. Aceita argumento opcional para pré-expandir os nós mostrando os táxons da imagem aberta.

    Usar o selected_related para pegar o 'parent' diminuiu 100 queries!
    '''
    Taxon = apps.get_model('meta', 'Taxon')
    taxa = Taxon.objects.filter(media__status='published').get_ancestors(include_self=True)

    return {'taxa': taxa, 'current': current}

@register.inclusion_tag('search_box.html')
def search_box(query=None):
    '''Creates search form in the header.'''
    if query:
        search_form = SearchForm({'query': query})
    else:
        search_form = SearchForm()
    return {'search_form': search_form}

@register.filter
def sp_em(meta, autoescape=None):
    '''Filtro que aplica itálico à espécies e gêneros.

    Meta pode vir como objeto ou values.
    '''
    # Tem que levar em conta tradução...
    italics = [
            u'Gênero', u'Genus',
            u'Subgênero', u'Subgenus',
            u'Espécie', u'Species'
            ]

    # Autoescape.
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    # Gerar output em itálico.
    try:
        if meta.rank in italics:
            output = u'<em>%s</em>' % esc(meta.name)
        else:
            output = esc(meta.name)
    except:
        try:
            if meta['rank'] in italics:
                output = u'<em>%s</em>' % esc(meta['name'])
            else:
                output = esc(meta['name'])
        except:
            try:
                output = esc(meta.name)
            except:
                output = esc(meta['name'])

    return mark_safe(output)
sp_em.needs_autoescape = True

@register.filter
def islist(obj):
    '''Determina se objeto é uma lista.'''
    return isinstance(obj, list)

@register.filter
def in_list(value, arg):
    '''Determina se um valor está na lista.'''
    return value in arg

@register.filter
def wordsplit(value):
    '''Retorna lista de palavras.'''
    return value.split()

@register.filter
def truncate(value, arg):
    """
    Truncates a string after a given number of chars
    Argument: Number of chars to truncate after

    From: http://djangosnippets.org/snippets/163/
    """
    try:
        length = int(arg)
    except ValueError: # invalid literal for int()
        return value # Fail silently.
    if not isinstance(value, basestring):
        value = str(value)
    if (len(value) > length):
        return value[:length] + "..."
    else:
        return value

@register.simple_tag
def paged_url(query_string, page_number):
    '''Constrói o url para lidar navegação paginada.'''
    url = '?'
    queries = query_string.split('&')
    for query in queries:
        if query.startswith('page'):
            queries.remove(query)
    if queries:
        url = url + '&'.join(queries) + '&page=%d' % page_number
    else:
        url = url + 'page=%d' % page_number
    return url

@register.inclusion_tag('sets.html')
def show_set(set, prefix, suffix, sep, method='name', before='', after=''):
    '''Gera série a partir de um set.

    Pega os elementos do set e cria lista separada por vírgulas ou qualquer outro separador. Um prefixo e um sufixo também podem ser indicados, além do método ('link' gera url, 'slug' gera slug e vazio mostra o nome normal).
    '''
    return {'set': set, 'prefix': prefix, 'suffix': suffix, 'sep': sep, 'method': method, 'before': before, 'after': after}
