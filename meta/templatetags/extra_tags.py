# -*- coding: utf-8 -*-

from meta.models import *
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
    params = {field:obj}
    try:
        image = Image.objects.filter(**params).order_by('?')[0]
    except:
        image = ''
    return {'image': image}

@register.inclusion_tag('related.html')
def show_related(media):
    '''Usa metadados da imagem para encontrar imagens relacionadas.
    
    Por enquanto procura apenas grupos taxonômicos relacionados, 
    usando o Q() para refinar a busca. Caso não encontre nenhum
    grupo relacionado, mostra imagens aleatórias.
    '''
    #TODO Idéia é criar um combobox para escolher por qual metadado filtrar.
    if media.taxon_set.all:
        qobj = Q()
        for taxon in media.taxon_set.all():
            qobj.add(Q(taxon=taxon), Q.AND)

        if media.genus_set.all:
            for genus in media.genus_set.all():
                qobj.add(Q(genus=genus), Q.OR)

            if media.species_set.all:
                for sp in media.species_set.all():
                    qobj.add(Q(species=sp), Q.OR)

        rel_images = Image.objects.filter(qobj).exclude(id=media.id).order_by('?')[:8]
    if rel_images:
        rand_images = []
    else:
        rand_images = Image.objects.all().order_by('?')[:8]
    return {'rel_images': rel_images, 'rand_images': rand_images}

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
        if item.author_set.all:
            for author in item.author_set.all():
                authors.append(author)
        if item.taxon_set.all:
            for taxon in item.taxon_set.all():
                taxa.append(taxon)
        if item.genus_set.all:
            for genus in item.genus_set.all():
                genera.append(genus)
        if item.species_set.all:
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
        if item.tag_set.all:
            for tag in item.tag_set.all():
                tags.append(tag)
    return list(set(authors)), list(set(taxa)), list(set(genera)), list(set(species)), list(set(sizes)), list(set(sublocations)), list(set(cities)), list(set(states)), list(set(countries)), list(set(tags))
