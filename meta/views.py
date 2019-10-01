# -*- coding: utf-8 -*-

import json
import logging
import os

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.aggregates import StringAgg
from functools import reduce
from operator import or_, and_

from .models import *
from .forms import *
from remove import compile_paths


# Home
def home_page(request):
    '''Home page showing image highlights.'''

    # Photos
    try:
        main_image = Media.objects.filter(highlight=True, is_public=True,
                datatype='photo').order_by('?')[0]
        photo = Media.objects.filter(highlight=True, is_public=True,
                datatype='photo').exclude(id=main_image.id).order_by('?')[0]

    except:
        main_image, photo = '', ''

    # Video
    try:
        video = Media.objects.filter(highlight=True, is_public=True,
                datatype='video').order_by('?')[0]
    except:
        video = ''

    # Tours
    try:
        tour = Tour.objects.order_by('?')[0]
        tour_image = tour.media.exclude(
                id=main_image.id).exclude(id=photo.id).order_by('?')[0]
    except:
        tour, tour_image = '', ''

    context = {
        'main_image': main_image,
        'photo': photo,
        'video': video,
        'tour': tour,
        'tour_image': tour_image,
        }
    return render(request, 'home.html', context)

# TODO: Why search and metadata pages do not have the same view?

def search_page(request, model_name='', field='', slug=''):
    '''Default gallery view for displaying and filtering metadata.'''

    # Get public media.
    media_list = Media.objects.filter(is_public=True)

    # Check request.GET for query refinements.
    if request.method == 'GET':

        # Make mutable copy of request.GET QueryDict.
        query_dict = request.GET.copy()

        # Inject meta information to request.
        if field:
            model = apps.get_model('meta', model_name)
            instance = get_object_or_404(model, slug=slug)
            query_dict.appendlist(field, instance.id)
        else:
            instance = ''

        # Datatype.
        datatype = query_dict.get('datatype', 'all')
        if not datatype == 'all':
            # Only filter if datatype is not all (i.e. photos or videos).
            media_list = media_list.filter(datatype=datatype)

        # Query
        query = query_dict.get('query', '').strip()
        if query:
            vector = SearchVector('title', weight='A') + \
                     SearchVector('caption', weight='A') + \
                     SearchVector(StringAgg('person__name', delimiter=' '), weight='A') + \
                     SearchVector(StringAgg('tag__name', delimiter=' '), weight='B') + \
                     SearchVector(StringAgg('sublocation__name', delimiter=' '), weight='B') + \
                     SearchVector(StringAgg('city__name', delimiter=' '), weight='B') + \
                     SearchVector(StringAgg('state__name', delimiter=' '), weight='B') + \
                     SearchVector(StringAgg('country__name', delimiter=' '), weight='B')

            media_list = media_list.annotate(search=vector).filter(search=query)

        # Operator
        operator = query_dict.get('operator', 'and')

        # Author
        if 'author' in query_dict:
            # Extract objects from query_dict.
            get_authors = query_dict.getlist('author')
            authors = Person.objects.filter(id__in=get_authors)

            # Filter media by field and operator.
            media_list = filter_request(media_list, authors, 'person', operator)

            # Fill form with values.
            form_authors = list(get_authors)
        else:
            form_authors = []

        # Tag
        if 'tag' in query_dict:
            get_tags = query_dict.getlist('tag')
            tags = Tag.objects.filter(id__in=get_tags)
            media_list = filter_request(media_list, tags, 'tag', operator)
            form_tags = list(get_tags)
        else:
            form_tags = []

        # Taxon
        if 'taxon' in query_dict:
            get_taxa = query_dict.getlist('taxon')
            taxa = Taxon.objects.filter(id__in=get_taxa)
            media_list = filter_request(media_list, taxa, 'taxon', operator)
            form_taxa = list(get_taxa)
        else:
            form_taxa = []

        # Sublocation
        if 'sublocation' in query_dict:
            get_sublocations = query_dict.getlist('sublocation')
            sublocations = Sublocation.objects.filter(id__in=get_sublocations)
            media_list = filter_request(media_list, sublocations, 'sublocation', operator)
            form_sublocations = list(get_sublocations)
        else:
            form_sublocations = []

        # City
        if 'city' in query_dict:
            get_cities = query_dict.getlist('city')
            cities = City.objects.filter(id__in=get_cities)
            media_list = filter_request(media_list, cities, 'city', operator)
            form_cities = list(get_cities)
        else:
            form_cities = []

        # State
        if 'state' in query_dict:
            get_states = query_dict.getlist('state')
            states = State.objects.filter(id__in=get_states)
            media_list = filter_request(media_list, states, 'state', operator)
            form_states = list(get_states)
        else:
            form_states = []

        # Country
        if 'country' in query_dict:
            get_countries = query_dict.getlist('country')
            countries = Country.objects.filter(id__in=get_countries)
            media_list = filter_request(media_list, countries, 'country', operator)
            form_countries = list(get_countries)
        else:
            form_countries = []

        # Reference
        if 'reference' in query_dict:
            get_references = query_dict.getlist('reference')
            references = Reference.objects.filter(id__in=get_references)
            media_list = filter_request(media_list, references, 'reference', operator)
            form_references = list(get_references)
        else:
            form_references = []

        # Sort and display options.

        # Get highlights only.
        highlight = query_dict.get('highlight', False)
        if highlight:
            media_list = media_list.filter(highlight=1)

        # Orderby: replace 'random' by '?'
        orderby = query_dict.get('orderby', 'random')
        order = query_dict.get('order', 'desc')
        if orderby == 'random':
            sorting = '?'
        else:
            if order == 'desc':
                sorting = '-{}'.format(orderby)
            else:
                sorting = orderby

        # Sort media.
        media_list = media_list.order_by(sorting)

        # Forçar int para paginator.
        n_page = int(query_dict.get('n', '40'))

        # Define modified display form.
        display_form = DisplayForm({
            'query': query,
            'highlight': highlight,
            'datatype': datatype,
            'n': n_page,
            'orderby': orderby,
            'order': order,
            'operator': operator,
            'author': form_authors,
            'tag': form_tags,
            'sublocation': form_sublocations,
            'city': form_cities,
            'state': form_states,
            'country': form_countries,
            'taxon': form_taxa,
            })

    else:
        # Define initial display form.
        display_form = DisplayForm()

    # Return paginated list.
    entries = get_paginated(query_dict, media_list, n_page)

    context = {
        'entries': entries,
        'display_form': display_form,
        'meta': instance,
        'field': field,
        }
    return render(request, 'search.html', context)


def org_page(request):
    '''Página mostrando a organização dos metadados.

    Além de buscar as descrições de cada categoria, mostra exemplos aleatórios de imagens.
    '''
    # Tamanhos
    sizes = TagCategory.objects.get(name_en='Size')
    # Técnicas
    technique = TagCategory.objects.get(name_en='Imaging technique')
    microscopy = TagCategory.objects.get(name_en='Microscopy')
    # Estágios
    stage = TagCategory.objects.get(name_en='Life stage')
    stages = stage.tags.all()
    # Modos
    mode = TagCategory.objects.get(name_en='Life mode')
    # Habitat
    habitat = TagCategory.objects.get(name_en='Habitat')
    # Diversos
    assorted = TagCategory.objects.get(name_en='Miscellaneous')
    context = {
        'sizes': sizes,
        'microscopy': microscopy,
        'technique': technique,
        'stages': stages,
        'stage': stage,
        'mode': mode,
        'habitat': habitat,
        'assorted': assorted,
        }
    return render(request, 'organization.html', context)


def old_media(request, datatype, old_id):
    '''Redirect old Image and Video URLs to new Media pages.'''

    if datatype == 'image':
        media = get_object_or_404(Media, old_image=old_id)
    elif datatype == 'video':
        media = get_object_or_404(Media, old_video=old_id)

    return redirect('media_url', media_id=media.id)


# Single media file
def media_page(request, media_id):
    '''Invididual page for media file with all the information.'''

    # Get object.
    media = get_object_or_404(Media.objects.select_related('sublocation', 'city', 'state', 'country'), id=media_id)

    # Nullify forms.
    form, admin_form = None, None

    # Process related media form.
    if request.method == 'POST' and 'related' in request.POST:
        form = RelatedForm(request.POST)
        if form.is_valid():
            related = form.data['type']
            request.session['rel_type'] = form.data['type']

    # Process admin form.
    elif request.method == 'POST' and 'admin' in request.POST:
        admin_form = AdminForm(request.POST)
        if admin_form.is_valid():
            # Se algum tour tiver sido submetido no formulário.
            if 'tours' in request.POST:
                # Pega a lista de tours ligadas à imagem.
                media_tours = media.tour_set.values_list('id', flat=True)
                # Define lista de tours submetidos no formulário.
                form_tours = [int(id) for id in admin_form.cleaned_data['tours']]
                # Usa sets para descobrir imagens que foram removidas,
                remove_media = set(media_tours) - set(form_tours)
                # e imagens que devem ser adicionadas.
                add_media = set(form_tours) - set(media_tours)
                # Remove imagem de cada tour.
                for tour_id in remove_media:
                    tour = Tour.objects.get(id=tour_id)
                    tour.media.remove(media)
                    tour.save()
                # Adiciona imagem em cada tour.
                for tour_id in add_media:
                    tour = Tour.objects.get(id=tour_id)
                    tour.media.add(media)
                    tour.save()

            # Caso nenhum tour tenha sido selecionado.
            else:
                # Se tours estiverem desmarcados, retirar imagem de todos.
                media_tours = media.tour_set.all()
                # Mas, somente se ela está em algum.
                if media_tours:
                    for tour in media_tours:
                        tour.media.remove(media)
                        tour.save()
            # Atualiza campo do destaque.
            if 'highlight' in request.POST:
                media.highlight = True
            else:
                media.highlight = False
            # Salva imagem.
            media.save()
    if not form:
        try:
            form = RelatedForm(initial={'type': request.session['rel_type']})
            related = request.session['rel_type']
        except:
            form = RelatedForm(initial={'type': 'taxon'})
            related = 'taxon'
    if not admin_form:
        try:
            tour_list = media.tour_set.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': media.highlight,
                'tours': tour_list
                })
        except:
            tour_list = Tour.objects.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': False,
                'tours': tour_list
                })

    tags = media.tag_set.all()
    authors = media.person_set.filter(is_author=True)
    taxa = media.taxon_set.all()
    sources = media.person_set.all()
    references = media.reference_set.all()

    context = {
        'media': media,
        'form': form,
        'admin_form': admin_form,
        'related': related,
        'tags': tags,
        'authors': authors,
        'taxa': taxa,
        'sources': sources,
        'references': references,
        }

    if request.is_ajax():
        return render(request, 'media_page_ajax.html', context)
    else:
        return render(request, 'media_page.html', context)


def tour_page(request, slug):
    '''Tour page.'''
    tour = get_object_or_404(Tour, slug=slug)
    # TODO: Think better how references will be managed.
    references = tour.references.all()
    entries = tour.media.select_related('sublocation', 'city', 'state', 'country')

    # Get first thumbnail.
    try:
        thumb = entries.values_list('coverpath', flat=True)[0]
    except:
        thumb = ''

    # Extract media metadata.
    # TODO: Do I really need to get all of these?
    authors, taxa, sublocations, cities, states, countries, tags = extract_set(entries)
    # Only using authors/taxa/tags for meta keywords.

    context = {
        'tour': tour,
        'entries': entries,
        'thumb': thumb,
        'authors': authors,
        'taxa': taxa,
        'tags': tags,
        'references': references,
        }

    return render(request, 'tour_page.html', context)


# Menu
def taxa_page(request):
    '''Taxa organized in a tree and species list.

    Species list is a genus list to show undefined species as well.
    '''
    genera = Taxon.objects.filter(rank_en='Genus').order_by('name')
    context = {
        'genera': genera,
        }
    return render(request, 'taxa_page.html', context)


def places_page(request):
    '''Página mostrando locais de maneira organizada.'''
    sublocations = Sublocation.objects.order_by('name')
    cities = City.objects.order_by('name')
    states = State.objects.order_by('name')
    countries = Country.objects.order_by('name')
    context = {
        'sublocations': sublocations,
        'cities': cities,
        'states': states,
        'countries': countries,
        }
    return render(request, 'places_page.html', context)


def tags_page(request):
    '''Página mostrando tags organizados por categoria.'''
    tagcats = TagCategory.objects.prefetch_related('tags')
    context = {
        'tagcats': tagcats,
        }
    return render(request, 'tags_page.html', context)


def authors_page(request):
    '''Página mostrando autores e especialistas.'''
    authors = Person.objects.filter(is_author=True).order_by('name')
    sources = Person.objects.filter(is_author=False).order_by('name')
    context = {
        'authors': authors,
        'sources': sources,
        }
    return render(request, 'authors_page.html', context)


def refs_page(request):
    '''Página mostrando referências.'''
    references = Reference.objects.order_by('-citation')
    context = {
        'references': references,
        }
    return render(request, 'refs_page.html', context)


def tours_page(request):
    '''Página mostrando lista de tours disponíveis.'''
    tours = Tour.objects.order_by('-pub_date')
    context = {
        'tours': tours,
        }
    return render(request, 'tours_page.html', context)


def press_page(request):
    '''Página com kit imprensa, texto melhores imagens.'''
    # Fotos
    photos = Media.objects.filter(highlight=True, is_public=True, datatype='photo').order_by('?')
    cover_photo = photos[0]
    photos = photos.exclude(id=cover_photo.id)[:8]
    # Videos
    videos = Media.objects.filter(highlight=True, is_public=True, datatype='video').order_by('?')[:8]
    context = {
        'photos': photos,
        'videos': videos,
        'cover_photo': cover_photo,
        }
    return render(request, 'press_page.html', context)


# Internal functions
def catch_get(keys, get):
    '''Checks if any of the keys is in the request.GET.'''
    for key in keys:
        if key in get:
            return True
        else:
            continue
    else:
        False


def get_paginated(query_dict, media_list, n_page=16):
    '''Return queryset paginator. n_page must be integer.'''
    paginator = Paginator(media_list, n_page)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(query_dict.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        media_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        media_page = paginator.page(paginator.num_pages)
    return media_page


def show_info(media_list, queries, full_results=False):
    '''Extrai metadados das imagens e exclui o que estiver nas queries.

    Manda a lista de imagens e de vídeos para a função extract_set que vai extrair todos os metadados associados a estes arquivos.

    Para identificar os valores que estão sendo procurados (queries), estes são excluídos de cada lista correspondente de metadados (authors, taxa, etc.)

    Retorna 3 objetos: data, queries e urls.
    '''

    # TODO: DEPRECATED, DELETE!

    # Define querysets.
    if full_results:
        authors = Person.objects.exclude(media__isnull=True)
        taxa = Taxon.objects.exclude(media__isnull=True)
        sublocations = Sublocation.objects.all()
        cities = City.objects.all()
        states = State.objects.all()
        countries = Country.objects.all()
        tags = Tag.objects.exclude(media__isnull=True)
    else:
        authors, taxa, sublocations, cities, states, countries, tags = extract_set(media_list)

    for k, v in queries.items():
        if v:
            if k == 'author':
                authors = authors.exclude(pk__in=queries['author'])
            elif k == 'tag':
                tags = tags.exclude(pk__in=queries['tag'])
            elif k == 'taxon':
                taxa = taxa.exclude(pk__in=queries['taxon'])
            elif k == 'sublocation':
                sublocations = sublocations.exclude(pk__in=queries['sublocation'])
            elif k == 'city':
                cities = cities.exclude(pk__in=queries['city'])
            elif k == 'state':
                states = states.exclude(pk__in=queries['state'])
            elif k == 'country':
                countries = countries.exclude(pk__in=queries['country'])

            # Convert to values.
            try:
                queries[k] = v.values()
            except:
                pass

    # From here on, only values (not objects).
    data = {
            'author': authors.values(),
            'taxon': taxa.values(),
            'sublocation': sublocations.values(),
            'city': cities.values(),
            'state': states.values(),
            'country': countries.values(),
            'tag': tags.values(),
            }

    # Create refinement url for each metadata.
    for k, v in data.items():
        if v:
            for meta in v:
                meta['filter_url'] = build_url(meta, k, queries)
                if k == 'author':
                    meta['url'] = reverse('person_url', args=[meta['slug']])
                else:
                    meta['url'] = reverse('%s_url' % k, args=[meta['slug']])

    # Create refinement url for each query in request.GET.
    for k, v in queries.items():
        # Ignore 'query' and 'datatype'.
        if k not in ['query', 'datatype', 'n', 'orderby', 'order', 'highlight']:
            if v:
                for meta in v:
                    meta['filter_url'] = build_url(meta, k, queries, remove=True)
                    meta['url'] = reverse('%s_url' % k, args=[meta['slug']])

    # Temporarily save 'datatype' (used further below).
    request_type = queries['datatype']

    # Generate static urls for media.
    urls = {}
    urls['videos'] = build_url('video', 'datatype', queries)
    urls['photos'] = build_url('photo', 'datatype', queries)
    urls['all'] = build_url('photo', 'datatype', queries, remove=True, append='datatype=all')

    # Restaura o 'datatype' original.
    queries['datatype'] = request_type

    return data, queries, urls


def control_form(request):
    '''Build the control form and return options.'''

    # TODO: DEPRECATED, DELETE!

    # Usando POST para definir:
    #   1. Número de resultados por página.
    #   2. Ordenação por qual metadado (id, visitas, datas, etc).
    #   3. Tipo de ordenação, ascendente ou descendente.
    #   4. Mostrar apenas imagens de destaque.
    if request.method == 'POST':
        n_form = DisplayForm(request.POST)
        if n_form.is_valid():
            n_page = n_form.data['n']
            request.session['n'] = n_form.data['n']
            orderby = n_form.data['orderby']
            request.session['orderby'] = n_form.data['orderby']
            order = n_form.data['order']
            request.session['order'] = n_form.data['order']
            #XXX Meio bizarro, formulário não está mandando False, quando
            # destaque é falso. Está enviando vazio e quando é True está
            # mandando a string 'on'.
            try:
                highlight = n_form.data['highlight']
                request.session['highlight'] = n_form.data['highlight']
            except:
                highlight = False
                request.session['highlight'] = False
    else:
        try:
            n_form = DisplayForm(initial={'n': request.session['n'], 'orderby': request.session['orderby'], 'order': request.session['order'], 'highlight': request.session['highlight']})
            n_page = request.session['n']
            orderby = request.session['orderby']
            order = request.session['order']
            highlight = request.session['highlight']
        except:
            n_form = DisplayForm(initial={'n': 40, 'orderby': 'random', 'order': 'desc', 'highlight': False})
            n_page = 16
            orderby = 'random'
            order = 'desc'
            highlight = False

    # Substitui 'random' por '?'
    if orderby == 'random':
        orderby = '?'

    # Define highlight quando não estiver na sessão do usuário.
    if not 'highlight' in request.session:
        request.session['highlight'] = False

    return n_form, n_page, orderby, order, highlight


def extract_set(media_list):
    '''Extract other metadata from media list.

    Returns invididual querysets for each model.
    '''

    authors = Person.objects.filter(id__in=media_list.values_list('person', flat=True))
    tags = Tag.objects.filter(id__in=media_list.values_list('tag', flat=True))
    taxa = Taxon.objects.filter(id__in=media_list.values_list('taxon', flat=True))
    sublocations = Sublocation.objects.filter(id__in=media_list.values_list('sublocation', flat=True))
    cities = City.objects.filter(id__in=media_list.values_list('city', flat=True))
    states = State.objects.filter(id__in=media_list.values_list('state', flat=True))
    countries = Country.objects.filter(id__in=media_list.values_list('country', flat=True))

    return authors, taxa, sublocations, cities, states, countries, tags


def add_meta(meta, field, query):
    '''Adiciona metadado à lista de query.

    Se a lista estiver vazia simplesmente cria uma nova com o metadado. Caso a lista já exista e tenha elementos, adiciona o metadado à ela.

    Quando o campo for 'datatype' só substitui o valor (sem estender a lista).
    '''
    # Se o campo estiver vazio, já preencher com o valor do meta.
    if not query:
        final_query = [meta]
    # Se o campo não estiver vazio, adicionar o valor do meta ao final.
    else:
        final_query = [meta]
        final_query.extend(query)
    if field == 'datatype':
        final_query = [meta]
    return final_query


def filter_request(media_list, objects, field, operator):
    '''Filter media based on fields and operator.'''
    
    if operator == 'and':
        for obj in objects:
            media_list = media_list.filter(**{field: obj})

    elif operator == 'or':
        queries = []
        for obj in objects:
            queries.append(Q(**{field: obj}))
            if field == 'taxon':
                children = obj.get_descendants()
                for child in children:
                    queries.append(Q(**{field: child}))

        media_list = media_list.filter(reduce(or_, queries)).distinct()
    
    return media_list


def build_url(meta, field, queries, remove=False, append=None):
    '''Constrói o url para lidar com o refinamento.

    Descrição dos campos:
        - meta: valor do campo do request.GET, pode ser 'photo' ou o slug de
          algum metadado.
        - field: nome do campo do request.GET, 'datatype', 'author', 'tag', etc.
        - queries: dicionário com field:meta passados pelo request.GET, será
          usado para construir o url.
        - remove: se verdadeiro, a função irá limpar dos queries o meta do
          field passado como argumento, excluindo o valor do url final. Usado
          para criar os urls do 'menos' no refinamento (metadados ativos).
        - XXX provavelmente será deprecada >> append: string extra que pode
          ser passada como argumento para ter maior flexibilidade na hora de
          criar os urls no template.

    A função começa com o prefixo base '/search/?' e acrescenta ou remove os
    valores de acordo com os parâmetros acima.

    Se remove=True o valor meta é retirado das queries, caso contrário é
    adicionado. Para cada ítem não-vazio é criado uma string concatenada e
    adicionada ao prefixo original. Os valores podem ser strings (datatype e query)
    ou listas (tags, authors, etc). Por isso é preciso usar condicionais para
    diferenciar os dois tipos na hora de criar a string a ser adicionada.

    Após adicionar todos os valores das queries ele checa a existência do
    append e acrescenta ao final do prefixo. O único caso peculiar é não
    incluir o datatype=all no url quando houver os parâmetros. O datatype=all só é
    usado quando o url estiver vazio (ie, '/search/?datatype=all') para mostrar
    todos os arquivos sem nenhum refinamento.

    Por fim, é extremamente importante que as queries saiam da função
    exatamente como entraram (com os mesmos valores). Nos loops do refinador
    para gerar os urls dos metadados, uma modificação nas queries afeta a
    construção do próximo url. Assim, se o valor de meta foi removido ele deve
    ser recolocado e se o valor foi adicionado ele deve ser removido.

    XXX Não encontrei um jeito de contornar a situação acima. Instanciar o
    'queries' em um novo objeto não resolve.

    A função retorna uma string com o url.
    '''

    # TODO Update documentation to English.
    #import pdb; pdb.set_trace()


    # Usado para diferenciar o primeiro query que não precisa do '&'.
    first = True
    prefix = '/search/?'
    #XXX Ao passar manualmente o tipo de busca para os urls do search-status,
    # ele acaba recolocando, no final desta função, o campo datatype:photo. Isso
    # gera um problema, pois o queries original não continha o datatype (que foi
    # passado só para gerar estes urls). Assim, criei esta variável para não
    # colocar o datatype no queries quando este não estiverem no queries original.
    do_not_readd = False

    # Se for para remover o metadado, remover.
    if remove:
        if field == 'datatype':
            if not queries[field]:
                do_not_readd = True
            queries[field] = []
        elif field in ['n', 'orderby', 'order', 'highlight']:
            pass
        else:
            queries[field] = [q for q in queries[field] if not q['slug'] == meta['slug']]
    else:
        # Adiciona o valor meta do seu respectivo field na lista de queries.
        queries[field] = add_meta(meta, field, queries[field])

    # Constrói o url de fato.
    for k, v in queries.items():
        if v:
            if first:
                prefix = prefix + k + '='
                first = False
            else:
                prefix = prefix + '&' + k + '='

            # Faz checagem antes de adicionar últimos valores.
            # Search field e datatype field são strings, tratados diferente.
            search_field = False

            # Tratamento diferenciado para alguns metadados.
            if k == 'datatype':
                final_list = [datatype for datatype in v]
            elif k == 'n':
                final_list = v
            elif k == 'orderby':
                final_list = v
            elif k == 'order':
                final_list = v
            elif k == 'highlight':
                final_list = v
            elif k == 'query':
                search = v
                search_field = True
            else:
                final_list = [obj['slug'] for obj in v]

            # Search/DataType fields.
            if search_field:
                prefix = prefix + search
            else:
                prefix = prefix + ','.join(final_list)

    if append:
        if prefix[-1] == '?':
            prefix = prefix + append
        else:
            # Não acrescentar o datatype=all quando o url não estiver vazio (outros
            # metadados presentes).
            if not append == 'datatype=all':
                prefix = prefix + '&' + append
    elif not append:
        if prefix[-1] == '?':
            prefix = prefix + 'datatype=all'
            # Opção para retirar tudo, volta para o search vazio...
            #prefix = prefix[:-1]
    url = prefix

    # É preciso recolocar o meta removido para não afetar os urls seguintes.
    if remove:
        if not do_not_readd:
            # Adiciona o metadado na lista de queries.
            queries[field] = add_meta(meta, field, queries[field])
    else:
        # Como modificações no queries passa para próximos ítens, é necessário
        # retirar o valor da variável (do queries) após criação do url.
        #TODO Criar função remove_meta.
        if field == 'datatype':
            queries[field] = [q for q in queries[field] if not q == meta]
        else:
            queries[field] = [q for q in queries[field] if not q['slug'] == meta['slug']]
    return url

