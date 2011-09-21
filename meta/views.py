# -*- coding: utf-8 -*-

import logging
import operator
import os
from meta.forms import *
from meta.models import *
from meta.templatetags.extra_tags import extract_set
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
#from django.core.cache import cache
from itis import Itis
from remove import compile_paths

# Instancia logger do cifonauta.
logger = logging.getLogger('central.views')

# Main
def main_page(request):
    '''Página principal mostrando destaques e pontos de partida para navegar.'''
    # Fotos
    try:
        # Tenta encontrar destaques capa.
        images = Image.objects.filter(cover=True, is_public=True).select_related('size').defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude').order_by('?')

        # Processa queryset, definindo imagens de capa.
        image = images[0]
        photo = images[1]

        # Faz lista de destaques.
        thumbs = Image.objects.filter(highlight=True, is_public=True).select_related('size').defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude').order_by('?')[:10]
    except:
        image, photo, thumbs = '', '', []
    # Vídeos
    try:
        # Tenta encontrar destaques de capa.
        videos = Video.objects.filter(cover=True, is_public=True).defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude', 'webm_filepath', 'ogg_filepath', 'mp4_filepath').order_by('?')[:10]
        video = videos[0]
    except:
        video = ''
    # Tour
    try:
        tours = Tour.objects.order_by('?')
        tour = tours[0]
        tour_images = tour.images.defer('source_filepath', 'old_filepath', 
                'timestamp', 'stats', 'notes', 'review', 'pub_date', 
                'rights', 'sublocation', 'city', 'state', 'country', 'date', 
                'geolocation', 'latitude', 
                'longitude').exclude(id=image.id).exclude(id=photo.id).order_by('?')[:10]
        tour_image = tour_images[0]
    except:
        tour, tour_image = '', ''
    variables = RequestContext(request, {
        'main_image': image,
        'photo': photo,
        'video': video,
        'tour': tour,
        'tour_image': tour_image,
        'thumbs': thumbs,
        })
    return render_to_response('main_page.html', variables)

def search_page(request):
    '''Página de busca.

    Procura termo no campo tsv do banco de dados, que possibilita o full-text 
    search.
    '''
    #TODO Documentar como funciona essa função.
    #TODO Implementar jQuery e AJAX para melhorar usabilidade.
    form = SearchForm()
    n_form = DisplayForm(initial={
        'n': 16,
        'order': 'random',
        'highlight': True
        })

    # Define highlight quando não estiver na sessão do usuário.
    if not 'highlight' in request.session:
        request.session['highlight'] = True

    # Refinamentos.
    queries = {
            u'query': '',
            u'author': [],
            u'tag': [],
            u'size': [],
            u'taxon': [],
            u'sublocation': [],
            u'city': [],
            u'state': [],
            u'country': [],
            u'type': [],
            }

    image_list = []
    video_list = []
    images = []
    videos = []
    show_results = False

    if 'query' in request.GET or 'type' in request.GET or 'author' in request.GET or 'size' in request.GET or 'tag' in request.GET or 'taxon' in request.GET or 'sublocation' in request.GET or 'city' in request.GET or 'state' in request.GET or 'country' in request.GET:
        # Iniciando querysets para serem filtrados para cada metadado presente na query.
        #XXX Não sei se é muito eficiente, mas por enquanto será assim.
        image_list = Image.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').exclude(is_public=False)
        video_list = Video.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',).exclude(is_public=False)

        show_results = True
        qobj = Q()

        # Query
        if 'query' in request.GET:
            query = request.GET['query'].strip()
            # Faz full-text search no banco de dados, usando o campo tsv.
            image_list = image_list.extra(
                    select={
                        'rank': "ts_rank_cd(tsv, plainto_tsquery('portuguese', %s), 32)",
                        },
                    where=["tsv @@ plainto_tsquery('portuguese', %s)"],
                    params=[query],
                    select_params=[query, query],
                    order_by=('-rank',)
                    )
            video_list = video_list.extra(
                    select={
                        'rank': "ts_rank_cd(tsv, plainto_tsquery('portuguese', %s), 32)",
                        },
                    where=["tsv @@ plainto_tsquery('portuguese', %s)"],
                    params=[query],
                    select_params=[query, query],
                    order_by=('-rank',)
                    )
            form = SearchForm({'query': query})
            queries['query'] = query
        else:
            # Só para passar a informação adiante.
            query = []

        # Author
        if 'author' in request.GET:
            authors = request.GET['author'].split(',')
            queries['author'] = Author.objects.filter(slug__in=authors)
            for author in authors:
                image_list = image_list.filter(author__slug=author)
                video_list = video_list.filter(author__slug=author)

        # Tag 
        if 'tag' in request.GET:
            tags = request.GET['tag'].split(',')
            queries['tag'] = Tag.objects.filter(slug__in=tags)
            for tag in tags:
                image_list = image_list.filter(tag__slug=tag)
                video_list = video_list.filter(tag__slug=tag)

        # Size
        if 'size' in request.GET:
            size_id = request.GET['size']
            queries['size'] = Size.objects.filter(id=size_id)
            image_list = image_list.filter(size__id=size_id)
            video_list = video_list.filter(size__id=size_id)

        # Taxon
        if 'taxon' in request.GET:
            taxa = request.GET['taxon'].split(',')
            queries['taxon'] = Taxon.objects.filter(slug__in=taxa)
            # Precisa listar descendentes também, logo use o recurse:
            q =[]
            for taxon_slug in taxa:
                taxon = Taxon.objects.get(slug=taxon_slug)
                q.append(Q(**{'taxon':taxon}))
                q = recurse(taxon, q)
            image_list = image_list.filter(reduce(operator.or_, q))
            video_list = video_list.filter(reduce(operator.or_, q))

        # Sublocation
        if 'sublocation' in request.GET:
            sublocations = request.GET['sublocation'].split(',')
            queries['sublocation'] = Sublocation.objects.filter(slug__in=sublocations)
            for sublocation in sublocations:
                image_list = image_list.filter(sublocation__slug=sublocation)
                video_list = video_list.filter(sublocation__slug=sublocation)

        # City
        if 'city' in request.GET:
            cities = request.GET['city'].split(',')
            queries['city'] = City.objects.filter(slug__in=cities)
            for city in cities:
                image_list = image_list.filter(city__slug=city)
                video_list = video_list.filter(city__slug=city)

        # State
        if 'state' in request.GET:
            states = request.GET['state'].split(',')
            queries['state'] = State.objects.filter(slug__in=states)
            for state in states:
                image_list = image_list.filter(state__slug=state)
                video_list = video_list.filter(state__slug=state)

        # Country
        if 'country' in request.GET:
            countries = request.GET['country'].split(',')
            queries['country'] = Country.objects.filter(slug__in=countries)
            for country in countries:
                image_list = image_list.filter(country__slug=country)
                video_list = video_list.filter(country__slug=country)

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
                n_form = DisplayForm(initial={'n': request.session['n'], 
                    'orderby': request.session['orderby'], 'order': 
                    request.session['order'], 'highlight': 
                    request.session['highlight']})
                n_page = request.session['n']
                orderby = request.session['orderby']
                order = request.session['order']
                highlight = request.session['highlight']
            except:
                n_form = DisplayForm(
                        initial={'n': 16, 'orderby': 'random',
                            'order': 'desc', 'highlight': True})
                n_page = 16
                orderby = 'random'
                order = 'desc'
                highlight = True

        # Forçar int.
        n_page = int(n_page)

        # Restringe à destaques.
        if highlight:
            image_list = image_list.filter(highlight=True)
            video_list = video_list.filter(highlight=True)

        # Substitui 'random' por '?'
        if orderby == 'random':
            orderby = '?'
        # Ordena por request.POST['orderby'].
        image_list = image_list.order_by(orderby)
        video_list = video_list.order_by(orderby)

        # Reverte a ordem se necessário.
        if order == 'desc':
            image_list = image_list.reverse()
            video_list = video_list.reverse()

        # Retorna lista paginada.
        images = get_paginated(request, image_list, n_page)
        videos = get_paginated(request, video_list, n_page)

        # Exclui tipo.
        if 'type' in request.GET:
            if request.GET['type'] == 'photo':
                queries['type'] = 'photo'
                videos = []
                video_list = []
            elif request.GET['type'] == 'video':
                queries['type'] = 'video'
                images = []
                image_list = []
            elif request.GET['type'] == 'all':
                # Não precisa entrar no queries, para não poluir o url.
                pass

    variables = RequestContext(request, {
        'form': form,
        'images': images,
        'videos': videos,
        'image_list': image_list,
        'video_list': video_list,
        'show_results': show_results,
        'queries': queries,
        'n_form': n_form,
        })
    return render_to_response('buscar.html', variables)

def org_page(request):
    '''Página mostrando a organização dos metadados.

    Além de buscar as descrições de cada categoria, mostra exemplos aleatórios de imagens.
    '''
    # Tamanhos
    sizes = Size.objects.order_by('position')
    #FIXME Does not work when locale is different!
    # Técnicas
    technique = TagCategory.objects.get(name=u'Técnica')
    microscopy = TagCategory.objects.get(name=u'Microscopia')
    # Estágios
    stage = TagCategory.objects.get(name=u'Estágio de vida')
    stages = stage.tags.order_by('position')
    # Modos
    pelagic = TagCategory.objects.get(name=u'Pelágicos')
    benthic = TagCategory.objects.get(name=u'Bentônicos')
    # Habitat
    habitat = TagCategory.objects.get(name=u'Habitat')
    # Diversos 
    assorted = TagCategory.objects.get(name=u'Diversos')
    variables = RequestContext(request, {
        'sizes': sizes,
        'microscopy': microscopy,
        'technique': technique,
        'stages': stages,
        'stage': stage,
        'pelagic': pelagic,
        'benthic': benthic,
        'habitat': habitat,
        'assorted': assorted,
        })
    return render_to_response('organizacao.html', variables)

# Manage
@login_required
def hidden_page(request):
    '''Página mostrando imagens não públicas.

    Usada pelos administradores como referência para a edição de metadados.
    '''
    images = Image.objects.filter(is_public=False)
    videos = Video.objects.filter(is_public=False)
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        })
    return render_to_response('hidden.html', variables)

@login_required
def fixtaxa_page(request):
    '''Página mostrando táxons órfãos e sem ranking.

    Se o formulário foi enviado ele revisa os táxons selecionados.
    '''
    invalids = []
    valids = []
    if request.method == 'POST':
        form = FixTaxaForm(request.POST)
        if form.is_valid():
            for name in form.cleaned_data['review']:
                taxon = review_taxon(name)
                if taxon:
                    valids.append(name)
                else:
                    invalids.append(name)
            # Retira táxons concertados da lista.
            fixed_indexes = []
            for i, v in enumerate(form.fields['review'].choices):
                if v[0] in valids:
                    fixed_indexes.append(i)
            # Ordena lista de índices
            fixed_indexes.sort()
            fixed_indexes.reverse()
            # Remove choices na ordem reversa para não alterar o índice e 
            # excluir o táxon errado...
            for i in fixed_indexes:
                form.fields['review'].choices.pop(i)
    else:
        form = FixTaxaForm()
    variables = RequestContext(request, {
        'form': form,
        'invalids': invalids,
        'valids': valids,
        })
    return render_to_response('fixtaxa.html', variables)

@login_required
def fixmedia_page(request):
    '''Página para gerenciar imagens órfãs e duplicadas.'''
    deleted, not_deleted, paths = [], [], []
    if request.method == 'POST':
        try:
            photo_id = request.POST['photo']
            media = Image.objects.get(id=photo_id)
        except:
            video_id = request.POST['video']
            media = Video.objects.get(id=video_id)
        try:
            paths = compile_paths(media)
            for path in paths:
                try:
                    os.remove(path)
                    deleted.append(path)
                except:
                    not_deleted.append(path)
            try:
                media.delete()
            except:
                print 'Não rolou apagar do banco de dados?'
        except:
            print 'Algo deu errado para ler os caminhos.'
        # Insere no log?
        for path in paths:
            logger.debug('Supostamente removido: %s', path)
    # Pega todas as fotos.
    photos = Image.objects.all()
    orphaned_photos, duplicated_photos = get_orphans(photos)
    # Pega todos os vídeos.
    videos = Video.objects.all()
    orphaned_videos, duplicated_videos = get_orphans(videos)

    # Cria lista de órfãs e dic de duplicadas.
    orphaned = orphaned_photos
    duplicates = duplicated_photos
    # Adiciona vídeos à lista.
    orphaned.extend(orphaned_videos)
    duplicates.extend(duplicated_videos)

    print orphaned, duplicates

    variables = RequestContext(request, {
        'orphaned': orphaned,
        'duplicates': duplicates,
        'paths': paths,
        'deleted': deleted,
        'not_deleted': not_deleted,
        })
    return render_to_response('fixmedia.html', variables)

@login_required
def translate_page(request):
    '''Página inicial para traduções.'''
    variables = RequestContext(request, {})
    return render_to_response('translate.html', variables)

# Single
def photo_page(request, image_id):
    '''Página única de cada imagem com todas as informações.'''
    # Pega o objeto.
    image = get_object_or_404(Image.objects.select_related('stats', 'size', 
        'sublocation', 'city', 'state', 'country', 
        'rights').defer('source_filepath', 'old_filepath'), id=image_id)

    # Tentando contornar o uso de dois forms em uma view...
    form, admin_form = None, None

    # Processa o formulário das imagens relacionadas.
    if request.method == 'POST' and 'related' in request.POST:
        form = RelatedForm(request.POST)
        if form.is_valid():
            related = form.data['type']
            request.session['rel_type'] = form.data['type']

    # Processa formulário do administrador.
    elif request.method == 'POST' and 'admin' in request.POST:
        admin_form = AdminForm(request.POST)
        if admin_form.is_valid():
            # Se algum tour tiver sido submetido no formulário.
            if 'tours' in request.POST:
                # Pega a lista de tours ligadas à imagem.
                image_tours = image.tour_set.values_list('id', flat=True)
                # Define lista de tours submetidos no formulário.
                form_tours = [int(id) for id in 
                        admin_form.cleaned_data['tours']]
                # Usa sets para descobrir imagens que foram removidas,
                remove_image = set(image_tours) - set(form_tours)
                # e imagens que devem ser adicionadas.
                add_image = set(form_tours) - set(image_tours)
                # Remove imagem de cada tour.
                for tour_id in remove_image:
                    tour = Tour.objects.get(id=tour_id)
                    tour.images.remove(image)
                    tour.save()
                # Adiciona imagem em cada tour.
                for tour_id in add_image:
                    tour = Tour.objects.get(id=tour_id)
                    tour.images.add(image)
                    tour.save()
            # Caso nenhum tour tenha sido selecionado.
            else:
                # Se tours estiverem desmarcados, retirar imagem de todos.
                image_tours = image.tour_set.all()
                # Mas, somente se ela está em algum.
                if image_tours:
                    for tour in image_tours:
                        tour.images.remove(image)
                        tour.save()
            # Atualiza campo do destaque.
            if 'highlight' in request.POST:
                image.highlight = True
            else:
                image.highlight = False
            # Atualiza campo do destaque de capa.
            if 'cover' in request.POST:
                image.cover = True
            else:
                image.cover = False
            # Salva imagem.
            image.save()
    if not form:
        try:
            form = RelatedForm(initial={'type': request.session['rel_type']})
            related = request.session['rel_type']
        except:
            form = RelatedForm(initial={'type': 'author'})
            related = u'author'
    if not admin_form:
        try:
            tour_list = image.tour_set.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': image.highlight,
                'cover': image.cover,
                'tours': tour_list
                })
        except:
            tour_list = Tour.objects.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': False,
                'cover': False,
                'tours': tour_list
                })

    #XXX Será o save() mais eficiente que o update()?
    # Este era o comando antigo para atualizar, só pra lembrar.
    #Image.objects.filter(id=image_id).update(view_count=F('view_count') + 1)
    #TODO Checar sessão para evitar overdose de views
    #stats = Stats.objects.get(image=image)
    stats = image.stats
    #stats.pageviews = stats.pageviews + 1
    #stats.save()
    #Stats.objects.get(image=image).update(pageviews=F('pageviews') + 1)
    pageviews = stats.pageviews
    tags = image.tag_set.all()
    authors = image.author_set.all()
    taxa = image.taxon_set.all()
    sources = image.source_set.all()
    references = image.reference_set.all()
    variables = RequestContext(request, {
        'media': image,
        'form': form,
        'admin_form': admin_form,
        'related': related,
        'tags': tags,
        'authors': authors,
        'taxa': taxa,
        'sources': sources,
        'references': references,
        'pageviews': pageviews,
        })
    if request.is_ajax():
        return render_to_response('disqus.html', variables)
    else:
        return render_to_response('media_page.html', variables)

def video_page(request, video_id):
    '''Página única de cada vídeo com todas as informações.'''
    # Pega o objeto.
    video = get_object_or_404(Video.objects.select_related('stats', 'size', 
        'sublocation', 'city', 'state', 'country', 
        'rights').defer('source_filepath',), id=video_id)

    # Tentando contornar o uso de dois forms em uma view...
    form, admin_form = None, None

    # Processa o formulário das imagens relacionadas.
    if request.method == 'POST' and 'related' in request.POST:
        form = RelatedForm(request.POST)
        if form.is_valid():
            related = form.data['type']
            request.session['rel_type'] = form.data['type']

    # Processa formulário do administrador.
    elif request.method == 'POST' and 'admin' in request.POST:
        admin_form = AdminForm(request.POST)
        if admin_form.is_valid():
            # Se algum tour tiver sido submetido no formulário.
            if 'tours' in request.POST:
                # Pega a lista de tours ligadas ao vídeo.
                video_tours = video.tour_set.values_list('id', flat=True)
                # Define lista de tours submetidos no formulário.
                form_tours = [int(id) for id in 
                        admin_form.cleaned_data['tours']]
                # Usa sets para descobrir vídeos que foram removidas,
                remove_video = set(video_tours) - set(form_tours)
                # e imagens que devem ser adicionadas.
                add_video = set(form_tours) - set(video_tours)
                # Remove imagem de cada tour.
                for tour_id in remove_video:
                    tour = Tour.objects.get(id=tour_id)
                    tour.videos.remove(video)
                    tour.save()
                # Adiciona imagem em cada tour.
                for tour_id in add_video:
                    tour = Tour.objects.get(id=tour_id)
                    tour.videos.add(video)
                    tour.save()

            # Caso nenhum tour tenha sido selecionado.
            else:
                # Se tours estiverem desmarcados, retirar vídeo de todos.
                video_tours = video.tour_set.all()
                # Mas, somente se ela está em algum.
                if video_tours:
                    for tour in video_tours:
                        tour.videos.remove(video)
                        tour.save()
            # Atualiza campo do destaque.
            if 'highlight' in request.POST:
                video.highlight = True
            else:
                video.highlight = False
            # Atualiza campo do destaque de capa.
            if 'cover' in request.POST:
                video.cover = True
            else:
                video.cover = False
            # Salva imagem.
            video.save()
    if not form:
        try:
            form = RelatedForm(initial={'type': request.session['rel_type']})
            related = request.session['rel_type']
        except:
            form = RelatedForm(initial={'type': 'author'})
            related = u'author'
    if not admin_form:
        try:
            tour_list = video.tour_set.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': video.highlight,
                'cover': video.cover,
                'tours': tour_list
                })
        except:
            tour_list = Tour.objects.values_list('id', flat=True)
            admin_form = AdminForm(initial={
                'highlight': False,
                'cover': False,
                'tours': tour_list
                })

    #TODO Checar sessão para evitar overdose de views
    stats = video.stats
    #stats.pageviews = stats.pageviews + 1
    #stats.save()
    pageviews = stats.pageviews
    tags = video.tag_set.all()
    authors = video.author_set.all()
    taxa = video.taxon_set.all()
    sources = video.source_set.all()
    references = video.reference_set.all()
    # Para lidar com tamanhos de vídeos.
    if video.old_filepath.endswith('m2ts'):
    	height = 288
    else:
    	height = 384
    variables = RequestContext(request, {
        'media': video,
        'form': form,
        'admin_form': admin_form,
        'related': related,
        'height': height,
        'tags': tags,
        'authors': authors,
        'taxa': taxa,
        'sources': sources,
        'references': references,
        'pageviews': pageviews,
        })
    if request.is_ajax():
        return render_to_response('disqus.html', variables)
    else:
        return render_to_response('media_page.html', variables)

def embed_page(request, video_id):
    '''Página para embed dos vídeos.'''
    video = get_object_or_404(Video, id=video_id)
    stats = video.stats
    #stats.pageviews = stats.pageviews + 1
    #stats.save()
    variables = RequestContext(request, {
        'media': video,
        })
    return render_to_response('embed.html', variables)

def meta_page(request, model_name, field, slug):
    '''Página de um metadado.

    Mostra galeria com todas as imagens que o possuem.
    '''
    #TODO Documentar melhor como funciona.
    queries = {
            u'query': '',
            u'author': [],
            u'tag': [],
            u'size': [],
            u'taxon': [],
            u'sublocation': [],
            u'city': [],
            u'state': [],
            u'country': [],
            }
    #XXX Serve para identificar o field na meta_page. Mas precisa ser 
    # um queryset para rolar o values_list do show_info no extra_tags.
    # Se possível otimizar isso.
    qmodels = model_name.objects.filter(slug__in=[slug])
    queries[field] = qmodels
    # Pega objeto.
    model = get_object_or_404(model_name, slug=slug)
    filter_args = {field: model}
    try:
        q = [Q(**filter_args),]
        if field == 'taxon':
            q = recurse(model, q)
        image_list = Image.objects.filter(reduce(operator.or_, q)).select_related('stats', 'size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').exclude(is_public=False).distinct().order_by('-id')
        video_list = Video.objects.filter(reduce(operator.or_, q)).select_related('stats', 'size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',).exclude(is_public=False).distinct().order_by('-id')
    except:
        image_list = Image.objects.filter(**filter_args).select_related('stats', 'size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').exclude(is_public=False).distinct().order_by('-id')
        video_list = Video.objects.filter(**filter_args).select_related('stats', 'size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',).exclude(is_public=False).distinct().order_by('-id')
    images = get_paginated(request, image_list)
    videos = get_paginated(request, video_list)
    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'image_list': image_list,
        'video_list': video_list,
        'meta': model,
        'field': field,
        'queries': queries,
        })
    return render_to_response('meta_page.html', variables)

def tour_page(request, slug):
    '''Página única de cada tour.'''
    tour = get_object_or_404(Tour, slug=slug)
    references = tour.references.all()
    photos = tour.images.select_related('stats', 'size', 'sublocation', 'city', 'state', 'country')
    videos = tour.videos.select_related('stats', 'size', 'sublocation', 'city', 'state', 'country')
    try:
        thumb = photos.values_list('thumb_filepath', flat=True)[0]
    except:
        thumb = ''

    # Extrair metadados das imagens.
    authors, taxa, sizes, sublocations, cities, states, countries, tags = extract_set(photos, videos)

    # Atualiza contador de visualizações.
    stats = tour.stats
    #stats.pageviews = stats.pageviews + 1
    #stats.save()
    pageviews = stats.pageviews
    variables = RequestContext(request, {
        'tour': tour,
        'photos': photos,
        'videos': videos,
        'thumb': thumb,
        'taxa': taxa,
        'tags': tags,
        'authors': authors,
        'references': references,
        'pageviews': pageviews,
        })
    return render_to_response('tour_page.html', variables)

# Menu
def taxa_page(request):
    '''Página mostrando grupos taxonômicos de maneira organizada.'''
    variables = RequestContext(request, {
        })
    return render_to_response('taxa_page.html', variables)

def places_page(request):
    '''Página mostrando locais de maneira organizada.'''
    sublocations = Sublocation.objects.order_by('name')
    cities = City.objects.order_by('name')
    states = State.objects.order_by('name')
    countries = Country.objects.order_by('name')
    variables = RequestContext(request, {
        'sublocations': sublocations,
        'cities': cities,
        'states': states,
        'countries': countries,
        })
    return render_to_response('places_page.html', variables)

def tags_page(request):
    '''Página mostrando tags organizados por categoria.'''
    tagcats = TagCategory.objects.select_related('tags').exclude(name='Modo de vida')
    sizes = Size.objects.order_by('id')
    variables = RequestContext(request, {
        'tagcats': tagcats,
        'sizes': sizes,
        })
    return render_to_response('tags_page.html', variables)

def authors_page(request):
    '''Página mostrando autores e especialistas.'''
    authors = Author.objects.order_by('name')
    sources = Source.objects.order_by('name')
    variables = RequestContext(request, {
        'authors': authors,
        'sources': sources,
        })
    return render_to_response('authors_page.html', variables)

def refs_page(request):
    '''Página mostrando referências.'''
    references = Reference.objects.order_by('-citation')
    variables = RequestContext(request, {
        'references': references,
        })
    return render_to_response('refs_page.html', variables)

# Tests
def empty_page(request):
    '''Página com template vazio somente para testes de performance.'''
    variables = RequestContext(request, {})
    return render_to_response('empty_page.html', variables)

def static_page(request):
    '''Página estática somente para testes de performance.'''
    variables = RequestContext(request, {})
    return render_to_response('static_page.html', variables)

def dynamic_page(request):
    '''Página dinâmica somente para testes de performance.'''
    images = Image.objects.filter(tag__name='adulto', is_public=True).order_by('stats__views')[:20]
    variables = RequestContext(request, {
        'images': images,
        })
    return render_to_response('dynamic_page.html', variables)

def tours_page(request):
    '''Página mostrando lista de tours disponíveis.'''
    tours = Tour.objects.order_by('name')
    variables = RequestContext(request, {
        'tours': tours,
        })
    return render_to_response('tours_page.html', variables)

# Internal functions
def get_paginated(request, obj_list, n_page=16):
    '''Retorna o Paginator de um queryset.'''
    paginator = Paginator(obj_list, n_page)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        obj = paginator.page(paginator.num_pages)
    return obj

def recurse(taxon, q=None):
    '''Recursivamente retorna todos os táxons-filho em um Q object.'''
    if not q:
        q = []
    children = taxon.get_descendants()
    for child in children:
        q.append(Q(**{'taxon': child}))
    return q

def insert_parents(taxon):
    '''Gerencia atualização de um táxon no banco de dados.
    
    Pega ou cria cada parent, incluindo ranking, tsn e parent; pega o táxon em 
    questão e atualiza seu ranking, tsn e parent.
    '''
    try:
        # Iterate por cada parent.
        for parent in taxon.parents:
            print u'Criando %s...' % parent.taxonName
            newtaxon, new = Taxon.objects.get_or_create(name=parent.taxonName)
            if new:
                newtaxon.rank = parent.rankName
                newtaxon.tsn = parent.tsn
                if parent.parentName:
                    newtaxon.parent = Taxon.objects.get(name=parent.parentName)
                newtaxon.save()
                print u'Salvo!'
            else:
                print u'Já existe!'
        # Táxon original para atualizar o ranking, tsn e parent.
        original = Taxon.objects.get(name=taxon.name)
        if taxon.parent_name:
            original.parent = Taxon.objects.get(name=taxon.parent_name)
            print u'Parent: %s' % original.parent
        if taxon.tsn:
            original.tsn = taxon.tsn
            print u'TSN: %s' % original.tsn
        if taxon.rank:
            original.rank = taxon.rank
            print u'Rank: %s' % original.rank
        original.save()
    except:
        print u'Não rolou pegar hierarquia...'

def review_taxon(name):
    '''Revisa o táxon e atualiza banco de dados.

    1. Busca o nome no Itis. Se encontrar, adiciona e atualiza banco de dados.  
       E adicionado na lista de válidos.
    2. Se for espécie, buscar pelo gênero. Se encontrar gênero, adicioná-lo 
       junto com toda a hierarquia e, depois, adicionar como parent da espécie 
       e incluir ranking da mesma.
    3. Retorna True se tiver conseguido e False se não.
    '''
    #TODO revisar toda essa função...
    try:
        taxon = Itis(name)
        if taxon.hierarchy:
            # Atualiza parents
            insert_parents(taxon)
            return True
        else:
            name_split = name.split()
            if len(name_split) > 1:
                # XXX Se ele coloca o ranking, mas o gênero não é encontrado, o 
                # retorno é False, logo, não será incluído na lista de válidos 
                # e não será excluído do formulário. Aparentemente pode 
                # acontecer alguma incongruência por causa disso...
                original = Taxon.objects.get(name=name)
                original.rank = u'Espécie'
                original.save()
                try:
                    # Gambiarra para encontrar gêneros nas tabelas.
                    genus = name_split[0]
                    taxon = Itis(genus)
                    if taxon.hierarchy:
                        genus, new = Taxon.objects.get_or_create(name=genus)
                        # Atualiza parents
                        insert_parents(genus)
                        genus.save()
                        # Atualiza ranking do táxon original.
                        original.parent = genus
                        original.save()
                        return True
                    else:
                        return False
                except:
                    return False
            else:
                return False
    except:
        return False

def get_orphans(entries):
    '''Get orphans and duplicates from a queryset.

    Works for photos and videos, returns 2 lists.'''
    # Cria lista de órfãs e dic de duplicadas.
    orphaned = []
    duplicates = []
    dups = {}
    # Le o link com o caminho para o arquivo original.
    # Se o original não existir, é orfã.
    for entry in entries:
        try:
            original = os.readlink(entry.source_filepath)
            if dups.has_key(original):
                dups[original].append(entry)
            else:
                dups[original] = [entry]
        except OSError:
            orphaned.append(entry)
        else:
            pass
    # Coloca na lista tudo é duplicado.
    for k, v in dups.iteritems():
        if len(v) > 1:
            duplicates.append({'path': k, 'replicas': v})
    print orphaned, duplicates
    print
    return orphaned, duplicates
