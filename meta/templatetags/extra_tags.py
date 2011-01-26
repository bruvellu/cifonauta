# -*- coding: utf-8 -*-

import operator
from meta.models import *
from meta.forms import *
from django import template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

main_ranks = [u'Reino', u'Filo', u'Classe', u'Ordem', u'Família', u'Gênero', u'Espécie']

@register.inclusion_tag('tree.html')
def show_tree():
    #XXX Não está sendo usado mais. Apagar?
    taxa = Taxon.tree.all()
    #TODO Count não funciona com ManyToMany...
    #taxa = Taxon.tree.add_related_count(Taxon.tree.all(), Taxon, 'images', 'image_count', cumulative=True)
    return {'taxa': taxa, 'main_ranks': main_ranks}

@register.inclusion_tag('splist.html')
def show_spp():
    spp = Taxon.objects.filter(rank=u'Espécie').order_by('name')
    return {'spp': spp}

@register.inclusion_tag('taxon_paths.html')
def taxon_paths(taxon):
    ancestors = [t for t in taxon.get_ancestors() if t.rank in main_ranks]
    return {'taxon': taxon, 'ancestors': ancestors}

@register.inclusion_tag('hot_images.html')
def show_hot():
    hot_images = Image.objects.order_by('-view_count')[:4]
    return {'hot_images': hot_images}

@register.inclusion_tag('thumb_org.html')
def print_thumb(field, obj):
    params = {field: obj, 'is_public': True}
    try:
        media = Image.objects.filter(**params).order_by('?')[0]
    except:
        media = ''
    return {'media': media}

def slicer(query, media_id):
    '''Processa resultado do queryset.

    Busca o metadado, encontra o índice da imagem e reduz amostra.
    '''
    relative = {
            'ahead': '',
            'behind': '',
            'next': '',
            'previous': '',
            }
    for index, item in enumerate(query):
        if item.id == media_id:
            media_index = index
        else:
            pass
    ahead = len(query[media_index:]) - 1
    behind = len(query[:media_index])
    relative = {'ahead': ahead, 'behind': behind}
    if media_index < 2:
        media_index = 2
    if len(query) <= 5:
        rel_query = query
    else:
        rel_query = query[media_index-2:media_index+3]

    for index, item in enumerate(rel_query):
        if item.id == media_id:
            if index == 0:
                relative['previous'] = ''
            else:
                relative['previous'] = rel_query[index-1]
            if index == len(rel_query)-1:
                relative['next'] = ''
            else:
                relative['next'] = rel_query[index+1]
    return rel_query, relative

def mediaque(media, qobj):
    '''Retorna queryset de vídeo ou foto.'''
    if media.datatype == 'photo':
        query = Image.objects.filter(qobj, is_public=True).distinct().order_by('id')
    elif media.datatype == 'video':
        query = Video.objects.filter(qobj, is_public=True).distinct().order_by('id')
    else:
        print '%s é um datatype desconhecido.' % media.datatype
    return query

@register.inclusion_tag('related.html')
def show_related(media, form, related):
    '''Usa metadados da imagem para encontrar imagens relacionadas.'''
    # Limpa imagens relacionadas.
    rel_media = ''
    relative = ''
    # Transforma choices em dicionário.
    form_choices = form.fields['type'].choices
    choices = {}
    for c in form_choices:
        choices[c[0]] = c[1]

    if related == u'author':
        if media.author_set.all():
            qobj = Q()
            for meta in media.author_set.all():
                if meta.name:
                    qobj.add(Q(author=meta), Q.OR)
            if qobj.__len__():
                query = mediaque(media, qobj)
                rel_media, relative = slicer(query, media.id) 
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'taxon':
        if media.taxon_set.all():
            qobj = Q()
            for meta in media.taxon_set.all():
                if meta.name:
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
            qobj = Q(size=media.size.id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'sublocation':
        if media.sublocation:
            qobj = Q(sublocation=media.sublocation.id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'city':
        if media.city:
            qobj = Q(city=media.city.id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'state':
        if media.state:
            qobj = Q(state=media.state.id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'country':
        if media.country:
            qobj = Q(country=media.country.id)
            query = mediaque(media, qobj)
            rel_media, relative = slicer(query, media.id) 
        else:
            rel_media = ''

    else:
        rel_media = ''

    if related in [u'author', u'taxon',]:
        crumbs = eval('list(media.%s_set.all())' % related)
        pseudo = crumbs
        for index, item in enumerate(pseudo):
            if not item.name:
                crumbs.pop(index)
    else:
        crumbs = eval('media.%s' % related)

    current = media

    return {'current': current, 'rel_media': rel_media, 'relative': relative, 'form': form, 'related': related, 'type': choices[related], 'crumbs': crumbs}

@register.inclusion_tag('stats.html')
def show_stats():
    images = Image.objects.filter(is_public=True).count()
    videos = Video.objects.filter(is_public=True).count()
    genera = Taxon.objects.filter(rank=u'Gênero').count()
    spp = Taxon.objects.filter(rank=u'Espécie').count()
    locations = Sublocation.objects.count()
    cities = City.objects.count()
    states = State.objects.count()
    countries = Country.objects.count()
    tags = Tag.objects.count()
    references = Reference.objects.count()
    return {'images': images, 'videos': videos, 'genera': genera, 'spp': spp, 'locations': locations, 'cities': cities, 'states': states, 'countries': countries, 'tags': tags, 'references': references}

@register.filter
def sp_em(meta, autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    try:
        if meta.rank == u'Gênero' or meta.rank == u'Espécie':
            output = u'<em>%s</em>' % esc(meta.name)
        else:
            output = esc(meta.name)
    except:
        output = esc(meta.name)
    return mark_safe(output)
sp_em.needs_autoescape = True

@register.filter
def islist(obj):
    return isinstance(obj, list)

@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def wordsplit(value):
    return value.split()

@register.filter
def icount(value, field):
    q = {field:value}
    return Image.objects.filter(**q).count() + Video.objects.filter(**q).count()

@register.inclusion_tag('mais.html')
def show_info(image_list, video_list, queries):
    '''Apenas manda extrair os metadados e envia para template.'''
    authors, taxa, sizes, sublocations, cities, states, countries, tags = extract_set(image_list, video_list)
    for k, v in queries.iteritems():
        if v:
            if k == 'author':
                authors = authors.exclude(pk__in=queries['author'].values_list('id'))
            elif k == 'tag':
                tags = tags.exclude(pk__in=queries['tag'].values_list('id'))
            elif k == 'size':
                sizes = sizes.exclude(pk__in=queries['size'].values_list('id'))
            elif k == 'taxon':
                taxa = taxa.exclude(pk__in=queries['taxon'].values_list('id'))
            elif k == 'sublocation':
                sublocations = sublocations.exclude(pk__in=queries['sublocation'].values_list('id'))
            elif k == 'city':
                cities = cities.exclude(pk__in=queries['city'].values_list('id'))
            elif k == 'state':
                states = states.exclude(pk__in=queries['state'].values_list('id'))
            elif k == 'country':
                countries = countries.exclude(pk__in=queries['country'].values_list('id'))
    return {
            'authors': authors, 'taxa': taxa, 'sizes': sizes,
            'sublocations': sublocations, 'cities': cities,
            'states': states, 'countries': countries, 'tags': tags,
            'queries': queries,
            }

@register.inclusion_tag('fino.html')
def refiner(actives, inactives, field, queries):
    '''Gera lista de metadados ativos e inativos.'''
    print
    print field
    print
    print actives
    print inactives
    return {'actives': actives, 'inactives': inactives,
            'field': field, 'queries': queries}

@register.simple_tag
def build_url(meta, field, queries):
    '''Constrói o url para lidar com o refinamento.'''
    first = True
    prefix = '/buscar/?'
    # Se o campo estiver vazio, já preencher com o valor do meta.
    if not queries[field]:
        if field == 'size':
            queries[field] = [str(meta.id)]
        else:
            queries[field] = [meta.slug]
    # Se o campo não estiver vazio, adicionar o valor do meta ao final.
    else:
        if isinstance(queries[field], list):
            values_list = queries[field]
        else:
            if field == 'size':
                values_list = queries[field].values_list('id', flat=True)
                values_list = [str(n) for n in values_list]
            else:
                values_list = queries[field].values_list('slug', flat=True)
        queries[field] = [meta.slug]
        queries[field].extend(values_list)
    for k, v in queries.iteritems():
        if v:
            if first:
                prefix = prefix + k + '='
                first = False
            else:
                prefix = prefix + '&' + k + '='
            # Faz checagem antes de adicionar últimos valores.
            if isinstance(v, list):
                final_list = v
            else:
                if k == 'size':
                    final_list = v.values_list('id', flat=True)
                    final_list = [str(n) for n in final_list]
                else:
                    final_list = v.values_list('slug', flat=True)
            prefix = prefix + ','.join(final_list)
    url = prefix
    # Como modificações no queries passa para próximos ítens, é necessário
    # retirar o valor da variável (do queries) após criação do url.
    if field == 'size':
        queries[field].remove(str(meta.id))
    else:
        queries[field].remove(meta.slug)
    return url

@register.inclusion_tag('sets.html')
def show_set(set, prefix, suffix, sep, method='name'):
    return {'set': set, 'prefix': prefix, 'suffix': suffix, 'sep': sep, 'method': method}

def extract_set(image_list, video_list):
    '''Extrai outros metadados das imagens buscadas.'''
    #TODO Incluir vídeos nessas queries!
    # Salva IDs dos arquivos em uma lista.
    # Imagens.
    image_values = image_list.values()
    image_ids = []
    for image in image_values.iterator():
        image_ids.append(image['id'])
    # Vídeos.
    video_values = video_list.values()
    video_ids = []
    for video in video_values.iterator():
        video_ids.append(video['id'])

    # ManyToMany relationships
    refined_tags = Tag.objects.filter(images__pk__in=image_ids).distinct().order_by('name')
    refined_authors = Author.objects.filter(images__pk__in=image_ids).distinct().order_by('name')
    refined_taxa = Taxon.objects.filter(images__pk__in=image_ids).distinct().order_by('name')

    # ForeignKey relationships
    refined_sizes = Size.objects.filter(image__pk__in=image_ids).distinct().order_by('name')
    refined_sublocations = Sublocation.objects.filter(image__pk__in=image_ids).distinct().order_by('name')
    refined_cities = City.objects.filter(image__pk__in=image_ids).distinct().order_by('name')
    refined_states = State.objects.filter(image__pk__in=image_ids).distinct().order_by('name')
    refined_countries = Country.objects.filter(image__pk__in=image_ids).distinct().order_by('name')

    return refined_authors, refined_taxa, refined_sizes, refined_sublocations, refined_cities, refined_states, refined_countries, refined_tags
