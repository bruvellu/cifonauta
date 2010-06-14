# -*- coding: utf-8 -*-

from meta.models import *
from meta.forms import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# Main
def main_page(request):
    images = Image.objects.order_by('-id')
    hot_images = Image.objects.order_by('-view_count')[:4]
    image_count = images.count()
    images = images#[:10]
    videos = Video.objects.order_by('-id')
    video_count = videos.count()
    videos = videos[:10]
    taxa = Taxon.objects.exclude(name='')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'image_count': image_count,
        'video_count': video_count,
        'hot_images': hot_images,
        'taxa': taxa,
        'show_tags': False,
        'show_title': False,
        })
    return render_to_response('main_page.html', variables)

def search_page(request):
    form = SearchForm()
    images = []
    videos = []
    show_results = False
    authors, taxa, genera, species, sizes, sublocations, cities, states, countries = [],[],[],[],[],[],[],[],[]
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            queryset = Image.objects.extra(
                    select={
                        'rank': "ts_rank_cd(tsv, plainto_tsquery('portuguese', %s), 32)",
                        },
                    where=["tsv @@ plainto_tsquery('portuguese', %s)"],
                    params=[query],
                    select_params=[query, query],
                    order_by=('-rank',)
                    )
            #keywords = query.split()
            q = Q()
            #for keyword in keywords:
            #    q_author = Q(author__name__icontains=keyword)
            #    q_taxon = Q(taxon__name__icontains=keyword)
            #    q_genus = Q(genus__name__icontains=keyword)
            #    q_species = Q(species__name__icontains=keyword)
            #    q_size = Q(size__name__icontains=keyword)
            #    q_source = Q(source__name__icontains=keyword)
            #    q_sublocation = Q(sublocation__name__icontains=keyword)
            #    q_city = Q(city__name__icontains=keyword)
            #    q_state = Q(state__name__icontains=keyword)
            #    q_country = Q(country__name__icontains=keyword)
            #    q = q | q_author | q_taxon | q_genus | q_species | q_size | q_source | q_sublocation | q_city | q_state | q_country
                #FIXME Não está funcionando...
                #imgs = Image.objects.raw("SELECT * FROM meta_image WHERE translate(title, 'ã', 'a') ILIKE translate(%s, 'ã', 'a')", [keyword])
            form = SearchForm({'query': query})
            #images = Image.objects.filter(q)
            images = queryset
            videos = Video.objects.filter(q)
            authors, taxa, genera, species, sizes, sublocations, cities, states, countries = extract_set(images)
    variables = RequestContext(request, {
        'form': form,
        'images': images,
        'videos': videos,
        'authors': authors,
        'taxa': taxa,
        'genera': genera,
        'species': species,
        'sizes': sizes,
        'sublocations': sublocations,
        'cities': cities,
        'states': states,
        'countries': countries,
        'show_results': show_results,
        })
    return render_to_response('buscar.html', variables)

def extract_set(query):
    authors = []
    taxa = []
    genera = []
    species = []
    sizes = []
    sublocations = []
    cities = []
    states = []
    countries = []
    for item in query:
        authors.append(item.author)
        taxa.append(item.taxon)
        genera.append(item.genus)
        species.append(item.species)
        sizes.append(item.size)
        sublocations.append(item.sublocation)
        cities.append(item.city)
        states.append(item.state)
        countries.append(item.country)
    strip = lambda mylist: [x for x in mylist if not x == '']
    return list(set(authors)), list(set(taxa)), list(set(genera)), list(set(species)), list(set(sizes)), list(set(sublocations)), list(set(cities)), list(set(states)), list(set(countries))

# Single
def image_page(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.view_count = image.view_count + 1
    image.save()
    variables = RequestContext(request, {
        'media': image,
        'type': 'image',
        })
    return render_to_response('media_page.html', variables)

def video_page(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.view_count = video.view_count + 1
    video.save()
    variables = RequestContext(request, {
        'media': video,
        'type': 'video',
        })
    return render_to_response('media_page.html', variables)

def tag_page(request, tag_slug):
    images = []
    tag = get_object_or_404(Tag, slug=tag_slug)
    images = tag.images.order_by('-id')
    videos = tag.videos.order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': tag,
        })
    return render_to_response('meta_page.html', variables)

    #if '&' and '|' in tag_name:
    #    and_tags = tag_name.split('&')
    #    for and_tag in and_tags:
    #        if '|' in and_tag:
    #            preor_imgs = []
    #            or_tags = and_tag.split('|')
    #            for or_tag in or_tags:
    #                or_tag = get_object_or_404(Tag, name=or_tag)
    #                or_imgs = or_tag.images.order_by('-id')
    #                preor_imgs.append(set(or_imgs))
    #            allor_imgs = preor_imgs[0]
    #            for or_set in preor_imgs:
    #                # Return union between sets
    #                allor_imgs |= or_set
    #            images.append(allor_imgs)
    #        else:
    #            and_tag = get_object_or_404(Tag, name=and_tag)
    #            and_imgs = and_tag.images.order_by('-id')
    #            images.append(set(and_imgs))
    #    final_set = images[0]
    #    for pre_set in images:
    #        # Return intersection between sets
    #        final_set &= pre_set
    #    images = final_set
    #elif '|' in tag_name:
    #    preor_imgs = []
    #    or_tags = tag_name.split('|')
    #    for or_tag in or_tags:
    #        or_tag = get_object_or_404(Tag, name=or_tag)
    #        or_imgs = or_tag.images.order_by('-id')
    #        preor_imgs.append(set(or_imgs))
    #    allor_imgs = preor_imgs[0]
    #    for or_set in preor_imgs:
    #        allor_imgs |= or_set
    #    images = allor_imgs
    #elif '&' in tag_name:
    #    and_tags = tag_name.split('&')
    #    for and_tag in and_tags:
    #        and_tag = get_object_or_404(Tag, name=and_tag)
    #        and_imgs = and_tag.images.order_by('-id')
    #        images.append(set(and_imgs))
    #    final_set = images[0]
    #    for pre_set in images:
    #        final_set &= pre_set
    #    images = final_set
    #else:
    #    tag = get_object_or_404(Tag, name=tag_name)
    #    images = tag.images.order_by('-id')

def author_page(request, author_slug):
    author = get_object_or_404(Author, slug=author_slug)
    images = Image.objects.filter(author__exact=author).order_by('-id')
    videos = Video.objects.filter(author__exact=author).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': author,
        })
    return render_to_response('meta_page.html', variables)

def taxon_page(request, taxon_slug):
    taxon = get_object_or_404(Taxon, slug=taxon_slug)
    images = Image.objects.filter(taxon__exact=taxon).order_by('-id')
    videos = Video.objects.filter(taxon__exact=taxon).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': taxon,
        })
    return render_to_response('meta_page.html', variables)

def genus_page(request, genus_slug):
    genus = get_object_or_404(Genus, slug=genus_slug)
    images = Image.objects.filter(genus__exact=genus).order_by('-id')
    videos = Video.objects.filter(genus__exact=genus).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': genus,
        })
    return render_to_response('meta_page.html', variables)

def species_page(request, species_slug):
    species = get_object_or_404(Species, slug=species_slug)
    images = Image.objects.filter(species__exact=species).order_by('-id')
    videos = Video.objects.filter(species__exact=species).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': species,
        })
    return render_to_response('meta_page.html', variables)

def size_page(request, size_slug):
    size = get_object_or_404(Size, slug=size_slug)
    images = Image.objects.filter(size__exact=size).order_by('-id')
    videos = Video.objects.filter(size__exact=size).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': size,
        })
    return render_to_response('meta_page.html', variables)

def sublocation_page(request, sublocation_slug):
    sublocation = get_object_or_404(Sublocation, slug=sublocation_slug)
    images = Image.objects.filter(sublocation__exact=sublocation).order_by('-id')
    videos = Video.objects.filter(sublocation__exact=sublocation).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': sublocation,
        })
    return render_to_response('meta_page.html', variables)

def city_page(request, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    images = Image.objects.filter(city__exact=city).order_by('-id')
    videos = Video.objects.filter(city__exact=city).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': city,
        })
    return render_to_response('meta_page.html', variables)

def state_page(request, state_slug):
    state = get_object_or_404(State, slug=state_slug)
    images = Image.objects.filter(state__exact=state).order_by('-id')
    videos = Video.objects.filter(state__exact=state).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': state,
        })
    return render_to_response('meta_page.html', variables)

def country_page(request, country_slug):
    country = get_object_or_404(Country, slug=country_slug)
    images = Image.objects.filter(country__exact=country).order_by('-id')
    videos = Video.objects.filter(country__exact=country).order_by('-id')
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'meta': country,
        })
    return render_to_response('meta_page.html', variables)

# Lists
def tag_list_page(request):
    tags = Tag.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': tags,
        'plural': u'Marcadores',
        'url': 'tag',
        })
    return render_to_response('meta_list_page.html', variables)

def author_list_page(request):
    authors = Author.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': authors,
        'plural': u'Autores',
        'url': 'autor'
        })
    return render_to_response('meta_list_page.html', variables)

def taxon_list_page(request):
    taxa = Taxon.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': taxa,
        'plural': u'Táxons',
        'url': 'taxon',
        })
    return render_to_response('meta_list_page.html', variables)

def genus_list_page(request):
    genera = Genus.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': genera,
        'plural': u'Gêneros',
        'url': 'genero',
        })
    return render_to_response('meta_list_page.html', variables)

def species_list_page(request):
    spp = Species.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': spp,
        'plural': u'Espécies',
        'url': 'especie',
        })
    return render_to_response('meta_list_page.html', variables)

def size_list_page(request):
    sizes = Size.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': sizes,
        'plural': u'Tamanhos',
        'url': 'tamanho',
        })
    return render_to_response('meta_list_page.html', variables)

def sublocation_list_page(request):
    sublocations = Sublocation.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': sublocations,
        'plural': u'Locais',
        'url': 'local',
        })
    return render_to_response('meta_list_page.html', variables)

def city_list_page(request):
    cities = City.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': cities,
        'plural': u'Cidades',
        'url': 'cidade',
        })
    return render_to_response('meta_list_page.html', variables)

def state_list_page(request):
    states = State.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': states,
        'plural': u'Estados',
        'url': 'estado',
        })
    return render_to_response('meta_list_page.html', variables)

def country_list_page(request):
    countries = Country.objects.order_by('name')
    variables = RequestContext(request, {
        'metas': countries,
        'plural': u'Países',
        'url': 'pais',
        })
    return render_to_response('meta_list_page.html', variables)

# Menu
def taxa_page(request):
    taxa = Taxon.objects.exclude(name='').order_by('name')
    genera = Genus.objects.order_by('name')
    spp = Species.objects.order_by('name')
    variables = RequestContext(request, {
        'taxa': taxa,
        'genera': genera,
        'spp': spp,
        })
    return render_to_response('taxa_page.html', variables)

def places_page(request):
    sublocations = Sublocation.objects.exclude(name='').order_by('name')
    cities = City.objects.exclude(name='').order_by('name')
    states = State.objects.exclude(name='').order_by('name')
    countries = Country.objects.exclude(name='').order_by('name')
    variables = RequestContext(request, {
        'sublocations': sublocations,
        'cities': cities,
        'states': states,
        'countries': countries,
        })
    return render_to_response('places_page.html', variables)

def tags_page(request):
    tags = Tag.objects.exclude(name='').order_by('parent')
    sizes = Size.objects.exclude(name='').order_by('id')
    variables = RequestContext(request, {
        'tags': tags,
        'sizes': sizes,
        })
    return render_to_response('tags_page.html', variables)
# Internal functions
# none...
