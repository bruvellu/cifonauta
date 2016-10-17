# -*- coding: utf-8 -*-

import operator

from meta.models import *
from meta.forms import *
from django import template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()

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
    '''Gera thumbnail aleatório de determinado metadado.'''
    media_url = context['MEDIA_URL']
    params = {field: obj, 'is_public': True}
    try:
        media = Image.objects.filter(**params).order_by('?')[0]
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


def mediaque(media, qobj):
    '''Retorna queryset de vídeo ou foto, baseado no datatype.

    Usado no navegador linear.
    '''
    if media.datatype == 'photo':
        query = Image.objects.filter(qobj, is_public=True).order_by('id')
    elif media.datatype == 'video':
        query = Video.objects.filter(qobj, is_public=True).order_by('id')
    else:
        print '%s é um datatype desconhecido.' % media.datatype
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
    if related == u'author':
        # Salva queryset para performance.
        authors = media.author_set.all()
        if authors:
            qobj = Q()
            for meta in authors:
                # Adiciona parâmetros para futuro query usando Q.
                qobj.add(Q(author=meta), Q.OR)
            if qobj.__len__():
                # Se objeto não estiver vazio, descobrir seu tipo (foto ou vídeo) e gerar o queryset.
                query = mediaque(media, qobj)
                # Processar queryset para se adaptar ao navegador linear.
                rel_media, relative = slicer(query, media.id)
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'taxon':
        taxa = media.taxon_set.all()
        if taxa:
            qobj = Q()
            for meta in taxa:
                qobj.add(Q(taxon=meta), Q.OR)
            if qobj.__len__():
                query = mediaque(media, qobj)
                rel_media, relative = slicer(query, media.id)
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'size':
        if media.size:
            qobj = Q(size=media.size_id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == u'sublocation':
        if media.sublocation:
            qobj = Q(sublocation=media.sublocation_id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == u'city':
        if media.city:
            qobj = Q(city=media.city_id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == u'state':
        if media.state:
            qobj = Q(state=media.state_id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    elif related == u'country':
        if media.country:
            qobj = Q(country=media.country_id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id)
        else:
            rel_media = ''

    else:
        rel_media = ''

    # Mostra os valores avaliados para o navegador linear.
    if related == u'author':
        crumbs = authors
    elif related == u'taxon':
        crumbs = taxa
    else:
        #XXX Necessário forçar a criação de uma lista.
        crumbs = [eval('media.%s' % related)]

    current = media

    return {'current': current, 'rel_media': rel_media, 'relative': relative, 'form': form, 'related': related, 'type': choices[related], 'crumbs': crumbs, 'MEDIA_URL': media_url}

@register.inclusion_tag('stats.html')
def show_stats():
    '''Gera linha com estatísticas do banco.'''
    #TODO Otimizar isso é necessário? Guardar no banco de dados?
    photos = Image.objects.filter(is_public=True).count()
    videos = Video.objects.filter(is_public=True).count()
    tags = Tag.objects.count()
    spp = Taxon.objects.filter(rank=u'Espécie').count()
    locations = Sublocation.objects.count()
    return {'photos': photos, 'videos': videos, 'spp': spp, 'locations': locations, 'tags': tags}

@register.inclusion_tag('tree.html')
def show_tree(current=None):
    '''Passa objeto para gerar árvore.

    Usa o recursetree do MPTT no template para gerar a árvore. Aceita argumento opcional para pré-expandir os nós mostrando os táxons da imagem aberta.

    Usar o selected_related para pegar o 'parent' diminuiu 100 queries!
    '''
    taxa = Taxon.objects.select_related('parent')
    return {'taxa': taxa, 'current': current}

@register.inclusion_tag('searchbox.html')
def search_box(query=None):
    '''Gera buscador para ser usado no header do site.'''
    if query:
        form = SearchForm({'query': query})
    else:
        form = SearchForm()
    return {'form': form}

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
def icount(value, field):
    '''Conta número de imagens+vídeos associados com metadado.'''
    q = {field:value}
    return Image.objects.filter(**q).count() + Video.objects.filter(**q).count()


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
