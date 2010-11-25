# -*- coding: utf-8 -*-

from meta.models import *
from meta.forms import *
from django import template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify
from django.db.models import Q

register = template.Library()

@register.inclusion_tag('tree.html')
def show_tree():
    taxa = Taxon.objects.exclude(name='').order_by('name')
    return {'taxa': taxa}

@register.inclusion_tag('splist.html')
def show_spp():
    genera = Genus.objects.exclude(name='').order_by('name')
    spcount = Species.objects.count()
    return {'genera': genera, 'spcount': spcount}

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
    for index, item in enumerate(query):
        if item.id == media_id:
            media_index = index
        else:
            pass
    if media_index < 2:
        media_index = 2
    if len(query) <= 5:
        rel_query = query
    else:
        rel_query = query[media_index-2:media_index+3]
    return rel_query

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
    '''Usa metadados da imagem para encontrar imagens relacionadas.
    
    Por enquanto procura apenas grupos taxonômicos relacionados, 
    usando o Q() para refinar a busca. Caso não encontre nenhum
    grupo relacionado, mostra imagens aleatórias.
    '''
    # Limpa imagens relacionadas.
    rel_media = ''
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
                rel_media = slicer(query, media.id) 
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
                rel_media = slicer(query, media.id)
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'genus':
        if media.genus_set.all():
            qobj = Q()
            for meta in media.genus_set.all():
                if meta.name:
                    qobj.add(Q(genus=meta), Q.OR)
            if qobj.__len__():
                query = mediaque(media, qobj)
                rel_media = slicer(query, media.id) 
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'species':
        if media.species_set.all():
            qobj = Q()
            for meta in media.species_set.all():
                if meta.name:
                    qobj.add(Q(species=meta), Q.OR)
            if qobj.__len__():
                query = mediaque(media, qobj)
                rel_media = slicer(query, media.id) 
            else:
                rel_media = ''
        else:
            rel_media = ''

    elif related == u'size':
        if media.size.name:
            qobj = Q(size=media.size.id)
            query = mediaque(media, qobj)
            rel_media = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'sublocation':
        if media.sublocation.name:
            qobj = Q(sublocation=media.sublocation.id)
            query = mediaque(media, qobj)
            rel_media = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'city':
        if media.city.name:
            qobj = Q(city=media.city.id)
            query = mediaque(media, qobj)
            rel_media = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'state':
        if media.state.name:
            qobj = Q(state=media.state.id)
            query = mediaque(media, qobj)
            rel_media = slicer(query, media.id) 
        else:
            rel_media = ''

    elif related == u'country':
        if media.country.name:
            qobj = Q(country=media.country.id)
            query = mediaque(media, qobj)
            rel_media = slicer(query, media.id) 
        else:
            rel_media = ''

    else:
        rel_media = ''

    if related in [u'author', u'taxon', u'genus', u'species']:
        crumbs = eval('list(media.%s_set.all())' % related)
        pseudo = crumbs
        for index, item in enumerate(pseudo):
            if not item.name:
                crumbs.pop(index)
    else:
        crumbs = eval('media.%s.name' % related)

    media_id = media.id

    return {'media_id': media_id, 'rel_media': rel_media, 'form': form, 'related': related, 'type': choices[related], 'crumbs': crumbs}

@register.inclusion_tag('stats.html')
def show_stats():
    images = Image.objects.count()
    videos = Video.objects.count()
    taxa = Taxon.objects.count()
    genera = Genus.objects.count()
    spp = Species.objects.count()
    locations = Sublocation.objects.count()
    cities = City.objects.count()
    states = State.objects.count()
    countries = Country.objects.count()
    tags = Tag.objects.count()
    return {'images': images, 'videos': videos, 'taxa': taxa, 'genera': genera, 'spp': spp, 'locations': locations, 'cities': cities, 'states': states, 'countries': countries, 'tags': tags}

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

@register.inclusion_tag('fino.html')
def refine(meta, query, qsize):
    '''Recebe metadado, processa a query para lista e manda refinar.
    
    A lista serve para marcar os metadados que estão selecionados.
    O refinamento é baseado no buscador, apenas o tamanho que é literal.
    '''
    qlist = [slugify(q) for q in query.split()]
    return {'meta': meta, 'query': query, 'qlist': qlist, 'qsize': qsize}

@register.inclusion_tag('mais.html')
def show_info(media, query, qsize):
    '''Apenas manda extrair os metadados e envia para template.'''
    authors, taxa, genera, species, sizes, sublocations, cities, states, countries, tags = extract_set(media)
    return {'authors': authors, 'taxa': taxa, 'genera': genera, 'species':
            species, 'sizes': sizes, 'sublocations': sublocations, 'cities':
            cities, 'states': states, 'countries': countries, 'tags': tags,
            'query': query, 'qsize': qsize}

@register.inclusion_tag('sets.html')
def show_set(set, prefix, suffix, sep, method='name'):
    return {'set': set, 'prefix': prefix, 'suffix': suffix, 'sep': sep, 'method': method}

def extract_set(query):
    '''Extrai outros metadados das imagens buscadas.'''
    authors = []
    taxa = []
    genera = []
    species = []
    sizes = []
    sublocations = []
    cities = []
    states = []
    countries = []
    tags = []
    for item in query:
        if item.author_set.all():
            for author in item.author_set.all():
                authors.append(author)
        if item.taxon_set.all():
            for taxon in item.taxon_set.all():
                taxa.append(taxon)
        if item.genus_set.all():
            for genus in item.genus_set.all():
                genera.append(genus)
        if item.species_set.all():
            for sp in item.species_set.all():
                species.append(sp)
        if item.size.name:
            sizes.append(item.size)
        if item.sublocation.name:
            sublocations.append(item.sublocation)
        if item.city.name:
            cities.append(item.city)
        if item.state.name:
            states.append(item.state)
        if item.country.name:
            countries.append(item.country)
        if item.tag_set.all():
            for tag in item.tag_set.all():
                tags.append(tag)
    return list(set(authors)), list(set(taxa)), list(set(genera)), list(set(species)), list(set(sizes)), list(set(sublocations)), list(set(cities)), list(set(states)), list(set(countries)), list(set(tags))
