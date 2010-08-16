from meta.models import *
from django import template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify

register = template.Library()

@register.inclusion_tag('tree.html')
def show_tree():
    taxa = Taxon.objects.exclude(name='').order_by('name')
    return {'taxa': taxa}

@register.inclusion_tag('splist.html')
def show_spp():
    genera = Genus.objects.exclude(name='').order_by('name')
    return {'genera': genera}

@register.inclusion_tag('hot_images.html')
def show_hot():
    hot_images = Image.objects.order_by('-view_count')[:4]
    return {'hot_images': hot_images}

@register.inclusion_tag('thumb.html')
def print_thumb(field, obj):
    params = {field:obj}
    try:
        image = Image.objects.filter(**params).order_by('?')[0]
    except:
        image = ''
    return {'image': image}

@register.inclusion_tag('related.html')
def show_related(media):
    taxa = Image.objects.filter(taxon=media.taxon).exclude(id=media.id)
    if media.genus.name:
        genera = Image.objects.filter(genus=media.genus).exclude(id=media.id)
    else:
        genera = []
    if media.species.name:
        species = Image.objects.filter(species=media.species).exclude(id=media.id)
    else:
        species = []
    if taxa and genera and species:
        rel_images = taxa | genera | species
        rel_images = rel_images.order_by('?')[:8]
        rand_images = []
    else:
        rel_images = []
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
    return {'images': images, 'videos': videos, 'taxa': taxa, 'genera': genera, 'spp': spp, 'locations': locations, 'cities': cities, 'states': states, 'countries': countries}

@register.filter
def in_list(value, arg):
    return value in arg

@register.filter
def wordsplit(value):
    return value.split()

@register.inclusion_tag('fino.html')
def refine(meta, query, qsize):
    qlist = [slugify(q) for q in query.split()]
    return {'meta': meta, 'query': query, 'qlist': qlist, 'qsize': qsize}

@register.inclusion_tag('mais.html')
def show_info(media, query, qsize):
    authors, taxa, genera, species, sizes, sublocations, cities, states, countries, tags = extract_set(media)
    return {'authors': authors, 'taxa': taxa, 'genera': genera, 'species':
            species, 'sizes': sizes, 'sublocations': sublocations, 'cities':
            cities, 'states': states, 'countries': countries, 'tags': tags,
            'query': query, 'qsize': qsize}

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
        if item.author.name:
            authors.append(item.author)
        if item.taxon.name:
            taxa.append(item.taxon)
        if item.genus.name:
            genera.append(item.genus)
        if item.species.name:
            species.append(item.species)
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
            print item.tag_set.all()
            for tag in item.tag_set.all():
                tags.append(tag)
    return list(set(authors)), list(set(taxa)), list(set(genera)), list(set(species)), list(set(sizes)), list(set(sublocations)), list(set(cities)), list(set(states)), list(set(countries)), list(set(tags))
