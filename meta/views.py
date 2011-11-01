# -*- coding: utf-8 -*-

import logging
import operator
import os
from meta.forms import *
from meta.models import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.transaction import commit_on_success
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
#from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import get_language

from itis import Itis
from remove import compile_paths

# Instancia logger do cifonauta.
logger = logging.getLogger('central.views')

# Main
@csrf_protect
def main_page(request):
    '''Página principal mostrando destaques e pontos de partida para navegar.'''

    # Fotos
    try:
        # Tenta encontrar destaques capa.
        main_image = Image.objects.filter(cover=True, is_public=True).select_related('size').defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude').order_by('?')[0]
        photo = Image.objects.filter(cover=True, is_public=True).select_related('size').defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude').exclude(id=main_image.id).order_by('?')[0]

        # Faz lista de destaques.
        thumbs = Image.objects.filter(highlight=True, is_public=True).select_related('size').defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude').order_by('?')[:8]
    except:
        main_image, photo, thumbs = '', '', []

    # Vídeos
    try:
        # Tenta encontrar destaques de capa.
        video = Video.objects.filter(cover=True, is_public=True).defer('source_filepath', 'old_filepath', 'timestamp', 'stats', 'notes', 'review', 'pub_date', 'rights', 'sublocation', 'city', 'state', 'country', 'date', 'geolocation', 'latitude', 'longitude', 'webm_filepath', 'ogg_filepath', 'mp4_filepath').order_by('?')[0]
    except:
        video = ''

    # Tours
    try:
        tour = Tour.objects.order_by('?')[0]
        tour_image = tour.images.defer('source_filepath', 'old_filepath', 
                'timestamp', 'stats', 'notes', 'review', 'pub_date', 
                'rights', 'sublocation', 'city', 'state', 'country', 'date', 
                'geolocation', 'latitude', 
                'longitude').exclude(id=main_image.id).exclude(id=photo.id).order_by('?')[0]
    except:
        tour, tour_image = '', ''

    variables = RequestContext(request, {
        'main_image': main_image,
        'photo': photo,
        'video': video,
        'tour': tour,
        'tour_image': tour_image,
        'thumbs': thumbs,
        })
    return render_to_response('main_page.html', variables)

def search_page(request):
    '''Página de busca.

    Procura termo no campo tsv do banco de dados usando o extra(). Refina este 
    queryset de acordo com as variáveis presentes no request.GET.
    '''
    # Define formulários.
    form = SearchForm()
    n_form = DisplayForm(initial={
        'n': 16,
        'order': 'random',
        'highlight': True
        })

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

    # Define variáveis principais.
    image_list = []
    video_list = []
    images = []
    videos = []
    show_results = False

    # Verifica se qualquer um dos campos foi passado no request.
    if catch_get(queries.keys(), request.GET):

        # Sinal para mostrar resultados no template.
        show_results = True

        # Define formulário de controle e variáveis.
        n_form, n_page, orderby, order, highlight = control_form(request)

        # Cria querysets somente com imagens públicas para serem filtrados por
        # cada metadado presente no request.
        image_list = Image.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').exclude(is_public=False)
        video_list = Video.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').exclude(is_public=False)

        # Query
        if 'query' in request.GET:
            # Limpa espaços extras.
            query = request.GET['query'].strip()

            # Ajusta busca textual para locale do usuário, 'portuguese' padrão.
            language = get_language()
            pg_lang = 'portuguese'
            if language == 'en':
                pg_lang = 'english'
            elif language == 'pt-br':
                pg_lang = 'portuguese'

            # Faz full-text search no banco de dados, usando o campo tsv.
            image_list = image_list.extra(
                    select={
                        'rank': "ts_rank_cd(tsv, plainto_tsquery(%s, %s), 32)",
                        },
                    where=["tsv @@ plainto_tsquery(%s, %s)"],
                    params=[pg_lang, query],
                    select_params=[pg_lang, query],
                    order_by=('-rank',)
                    )
            video_list = video_list.extra(
                    select={
                        'rank': "ts_rank_cd(tsv, plainto_tsquery(%s, %s), 32)",
                        },
                    where=["tsv @@ plainto_tsquery(%s, %s)"],
                    params=[pg_lang, query],
                    select_params=[pg_lang, query],
                    order_by=('-rank',)
                    )
            # Popula formulário de busca com o query.
            form = SearchForm({'query': query})
            # Passa valor para as queries.
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

        # Restringe aos destaques.
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

        # Forçar int para paginator.
        n_page = int(n_page)

        # Retorna lista paginada.
        images = get_paginated(request, image_list, n_page)
        videos = get_paginated(request, video_list, n_page)

        # Exclui tipo.
        if 'type' in request.GET:
            if request.GET['type'] == 'photo':
                queries['type'] = ['photo']
                videos = []
                video_list = []
            elif request.GET['type'] == 'video':
                queries['type'] = ['video']
                images = []
                image_list = []
            elif request.GET['type'] == 'all':
                queries['type'] = ['']
                # Não precisa entrar no queries, para não poluir o url.
                pass

    # Gera keywords.
    #XXX Usar essa lista para processar os querysets acima?
    keylist = []
    for k, v in request.GET.iteritems():
        keylist.append(v)
    keylist = [item for item in keylist if item]
    keywords = ','.join(keylist)

    # Extrai metadados das imagens.
    data, queries, urls = show_info(image_list, video_list, queries)

    variables = RequestContext(request, {
        'form': form,
        'images': images,
        'videos': videos,
        'image_list': image_list,
        'video_list': video_list,
        'show_results': show_results,
        'queries': queries,
        'data': data,
        'urls': urls,
        'n_form': n_form,
        'keywords': keywords,
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
@commit_on_success #TODO Colocar save em função separada?
def photo_page(request, image_id):
    '''Página única de cada imagem com todas as informações.'''
    # Pega o objeto.
    image = get_object_or_404(Image.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath'), id=image_id)

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
                form_tours = [int(id) for id in admin_form.cleaned_data['tours']]
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

@commit_on_success #TODO Colocar save em função separada?
def video_page(request, video_id):
    '''Página única de cada vídeo com todas as informações.'''
    # Pega o objeto.
    video = get_object_or_404(Video.objects.select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',), id=video_id)

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
            form = RelatedForm(initial={'type': 'taxon'})
            related = u'taxon'
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
    variables = RequestContext(request, {
        'media': video,
        })
    return render_to_response('embed.html', variables)

def meta_page(request, model_name, field, slug):
    '''Página de um metadado.

    Mostra galeria com todas as imagens que o possuem.
    '''
    # Formulário para controle de ordenação.
    n_form = DisplayForm(initial={
        'n': 16,
        'order': 'random',
        'highlight': True,
        })

    # Define formulário de controle e variáveis.
    n_form, n_page, orderby, order, highlight = control_form(request)

    # Queries guardam variáveis do request para o refinador.
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

    #XXX Serve para identificar o field na meta_page. Mas precisa ser 
    # um queryset para rolar o values_list do show_info no extra_tags.
    # Se possível otimizar isso.
    qmodels = model_name.objects.filter(slug__in=[slug])
    queries[field] = qmodels

    # Pega objeto.
    model = get_object_or_404(model_name, slug=slug)

    # Constrói argumentos.
    filter_args = {field: model, 'is_public': True}

    if field == 'taxon':
        q = [Q(**filter_args),]
        q = recurse(model, q)
        image_list = Image.objects.filter(reduce(operator.or_, q)).select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').order_by(orderby)
        video_list = Video.objects.filter(reduce(operator.or_, q)).select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',).order_by(orderby)
        #XXX Retirei o .distinct() destes queries. Conferir...
    else:
        image_list = Image.objects.filter(**filter_args).select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').order_by(orderby)
        video_list = Video.objects.filter(**filter_args).select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath',).order_by(orderby)

    # Restringe aos destaques.
    if highlight:
        image_list = image_list.filter(highlight=True)
        video_list = video_list.filter(highlight=True)

    # Reverte a ordem se necessário.
    if order == 'desc':
        image_list = image_list.reverse()
        video_list = video_list.reverse()

    # Forçar int para paginator.
    n_page = int(n_page)

    # Cria paginação.
    images = get_paginated(request, image_list, n_page)
    videos = get_paginated(request, video_list, n_page)

    # Extrai metadados das imagens.
    data, queries, urls = show_info(image_list, video_list, queries)

    variables = RequestContext(request, {
        'images': images,
        'videos': videos,
        'image_list': image_list,
        'video_list': video_list,
        'meta': model,
        'queries': queries,
        'data': data,
        'urls': urls,
        'field': field,
        'queries': queries,
        'n_form': n_form,
        })
    return render_to_response('meta_page.html', variables)

def tour_page(request, slug):
    '''Página única de cada tour.'''
    tour = get_object_or_404(Tour, slug=slug)
    references = tour.references.all()
    photos = tour.images.filter(tourposition__tour=tour).select_related('size', 'sublocation', 'city', 'state', 'country').order_by('tourposition')
    videos = tour.videos.select_related('size', 'sublocation', 'city', 'state', 'country')
    try:
        thumb = photos.values_list('thumb_filepath', flat=True)[0]
    except:
        thumb = ''

    # Extrair metadados das imagens.
    authors, taxa, sizes, sublocations, cities, states, countries, tags = extract_set(photos, videos)

    # Atualiza contador de visualizações.
    stats = tour.stats
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
    '''Página mostrando grupos taxonômicos de maneira organizada.

    Lista de espécies é, na verdade, lista de gêneros para que apareçam os 
    diversos táxons cuja espécie não está definida (ie, Gênero sp.).'''
    genera = Taxon.objects.filter(rank=u'Gênero').order_by('name')
    variables = RequestContext(request, {
        'genera': genera,
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

@csrf_protect
def press_page(request):
    '''Página com kit imprensa, texto melhores imagens.'''
    # Fotos
    photos = Image.objects.filter(cover=True).order_by('?')
    cover_photo = photos[0]
    photos = photos.exclude(id=cover_photo.id)[:8]
    # Videos
    videos = Video.objects.filter(cover=True).order_by('?')[:8]
    variables = RequestContext(request, {
        'photos': photos,
        'videos': videos,
        'cover_photo': cover_photo,
        })
    return render_to_response('press_page.html', variables)

# Internal functions

def catch_get(keys, get):
    '''Checa se alguma das chaves está no request.GET.'''
    for key in keys:
        if key in get:
            return True
        else:
            continue
    else:
        False

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
    return orphaned, duplicates

def show_info(image_list, video_list, queries):
    '''Extrai metadados das imagens e exclui o que estiver nas queries.

    Manda a lista de imagens e de vídeos para a função extract_set que vai extrair todos os metadados associados a estes arquivos.

    Para identificar os valores que estão sendo procurados (queries), estes são excluídos de cada lista correspondente de metadados (authors, taxa, etc.)

    Retorna 3 objetos: data, queries e urls.
    '''
    authors, taxa, sizes, sublocations, cities, states, countries, tags = extract_set(image_list, video_list)
    for k, v in queries.iteritems():
        if v:
            if k == 'author':
                authors = authors.exclude(pk__in=queries['author'])
            elif k == 'tag':
                tags = tags.exclude(pk__in=queries['tag'])
            elif k == 'size':
                sizes = sizes.exclude(pk__in=queries['size'])
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

    # A partir daqui somente "values", sem objetos.
    data = {
            'author': authors.values(),
            'taxon': taxa.values(),
            'size': sizes.values(),
            'sublocation': sublocations.values(),
            'city': cities.values(),
            'state': states.values(),
            'country': countries.values(),
            'tag': tags.values(),
            }

    # Gera url do refinamento para cada metadado.
    for k, v in data.iteritems():
        if v:
            for meta in v:
                meta['filter_url'] = build_url(meta, k, queries)

    # Gera url do refinamento para cada query no request.GET.
    for k, v in queries.iteritems():
        # Ignora 'query' e 'type'.
        if k == 'query':
            pass
        elif k == 'type':
            pass
        else:
            if v:
                for meta in v:
                    meta['filter_url'] = build_url(meta, k, queries, remove=True)

    # Salva temporariamente o 'type', para restaurar depois da parte abaixo.
    request_type = queries['type']

    # Gera urls estáticos para vídeos, fotos ou os dois.
    urls = {}
    urls['videos'] = build_url('video', 'type', queries)
    urls['photos'] = build_url('photo', 'type', queries)
    urls['all'] = build_url('photo', 'type', queries, remove=True, append='type=all')

    # Restaura o 'type' original.
    queries['type'] = request_type

    return data, queries, urls

def control_form(request):
    '''Build the control form and return options.'''
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
            n_form = DisplayForm(initial={'n': 16, 'orderby': 'random', 'order': 'desc', 'highlight': True})
            n_page = 16
            orderby = 'random'
            order = 'desc'
            highlight = True

    # Substitui 'random' por '?'
    if orderby == 'random':
        orderby = '?'

    # Define highlight quando não estiver na sessão do usuário.
    if not 'highlight' in request.session:
        request.session['highlight'] = True

    return n_form, n_page, orderby, order, highlight

def extract_set(image_list, video_list):
    '''Extrai outros metadados das imagens buscadas.

    Retorna querysets de cada modelo.
    '''
    # ManyToMany relationships
    #TODO fazer um select_related('parent') para as tags?
    # Talvez seja útil para mostrar a categoria delas no refinador.
    refined_tags = Tag.objects.filter(
            Q(images__pk__in=image_list) | Q(videos__pk__in=video_list)
            ).distinct()
    refined_authors = Author.objects.filter(
            Q(images__pk__in=image_list) | Q(videos__pk__in=video_list)
            ).distinct()
    refined_taxa = Taxon.objects.filter(
            Q(images__pk__in=image_list) | Q(videos__pk__in=video_list)
            ).distinct()

    # ForeignKey relationships
    refined_sizes = Size.objects.filter(
            Q(image__pk__in=image_list) | Q(video__pk__in=video_list)
            ).distinct()
    refined_sublocations = Sublocation.objects.filter(
            Q(image__pk__in=image_list) | Q(video__pk__in=video_list)
            ).distinct()
    refined_cities = City.objects.filter(
            Q(image__pk__in=image_list) | Q(video__pk__in=video_list)
            ).distinct()
    refined_states = State.objects.filter(
            Q(image__pk__in=image_list) | Q(video__pk__in=video_list)
            ).distinct()
    refined_countries = Country.objects.filter(
            Q(image__pk__in=image_list) | Q(video__pk__in=video_list)
            ).distinct()

    return refined_authors, refined_taxa, refined_sizes, refined_sublocations, refined_cities, refined_states, refined_countries, refined_tags

def add_meta(meta, field, query):
    '''Adiciona metadado à lista de query.

    Se a lista estiver vazia simplesmente cria uma nova com o metadado. Caso a lista já exista e tenha elementos, adiciona o metadado à ela.

    Quando o campo for 'type' só substitui o valor (sem estender a lista).
    '''
    # Se o campo estiver vazio, já preencher com o valor do meta.
    if not query:
        final_query = [meta]
    # Se o campo não estiver vazio, adicionar o valor do meta ao final.
    else:
        final_query = [meta]
        final_query.extend(query)
    if field == 'type':
        final_query = [meta]
    return final_query

def build_url(meta, field, queries, remove=False, append=None):
    '''Constrói o url para lidar com o refinamento.

    Descrição dos campos:
        - meta: valor do campo do request.GET, pode ser 'photo' ou o slug de 
          algum metadado.
        - field: nome do campo do request.GET, 'type', 'author', 'tag', etc.
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
    adicionada ao prefixo original. Os valores podem ser strings (type e query) 
    ou listas (tags, authors, etc). Por isso é preciso usar condicionais para 
    diferenciar os dois tipos na hora de criar a string a ser adicionada.

    Após adicionar todos os valores das queries ele checa a existência do 
    append e acrescenta ao final do prefixo. O único caso peculiar é não 
    incluir o type=all no url quando houver os parâmetros. O type=all só é 
    usado quando o url estiver vazio (ie, '/search/?type=all') para mostrar 
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
    # Usado para diferenciar o primeiro query que não precisa do '&'.
    first = True
    prefix = '/search/?'
    #XXX Ao passar manualmente o tipo de busca para os urls do search-status, 
    # ele acaba recolocando, no final desta função, o campo type:photo. Isso 
    # gera um problema, pois o queries original não continha o type (que foi 
    # passado só para gerar estes urls). Assim, criei esta variável para não 
    # colocar o type no queries quando este não estiverem no queries original.
    do_not_readd = False

    # Se for para remover o metadado, remover.
    if remove:
        if field == 'size':
            queries[field] = [q for q in queries[field] if not q['id'] == meta['id']]
        elif field == 'type':
            if not queries[field]:
                do_not_readd = True
            queries[field] = []
        else:
            queries[field] = [q for q in queries[field] if not q['slug'] == meta['slug']]
    else:
        # Adiciona o valor meta do seu respectivo field na lista de queries.
        queries[field] = add_meta(meta, field, queries[field])

    # Constrói o url de fato.
    for k, v in queries.iteritems():
        if v:
            if first:
                prefix = prefix + k + '='
                first = False
            else:
                prefix = prefix + '&' + k + '='

            # Faz checagem antes de adicionar últimos valores.
            # Search field e type field são strings, tratados diferente.
            search_field = False

            # Tratamento diferenciado para alguns metadados.
            if k == 'size':
                final_list = [str(size['id']) for size in v]
            elif k == 'type':
                final_list = [type for type in v]
            elif k == 'query':
                search = v
                search_field = True
            else:
                final_list = [obj['slug'] for obj in v]

            # Search/Type fields.
            if search_field:
                prefix = prefix + search
            else:
                prefix = prefix + ','.join(final_list)

    if append:
        if prefix[-1] == '?':
            prefix = prefix + append
        else:
            # Não acrescentar o type=all quando o url não estiver vazio (outros 
            # metadados presentes).
            if not append == 'type=all':
                prefix = prefix + '&' + append
    elif not append:
        if prefix[-1] == '?':
            prefix = prefix + 'type=all'
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
        if field == 'size':
            queries[field] = [q for q in queries[field] if not q['id'] == meta['id']]
        elif field == 'type':
            queries[field] = [q for q in queries[field] if not q == meta]
        else:
            queries[field] = [q for q in queries[field] if not q['slug'] == meta['slug']]
    return url
