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

@register.inclusion_tag('splist.html')
def show_spp():
    '''Mostra lista simples de espécies presentes no banco.'''
    spp = Taxon.objects.filter(rank=u'Espécie').order_by('name')
    return {'spp': spp}

@register.inclusion_tag('metalist.html')
def print_metalist(metalist, field):
    '''Mostra lista de metadados com contador de imagens.'''
    return {'metalist': metalist, 'field': field}

@register.inclusion_tag('taxon_paths.html')
def taxon_paths(taxon):
    '''Mostra classificação de um táxon de forma linear.

    Exclui subrankings da lista.
    '''
    #XXX É a forma mais eficaz de retirar os subrankings?
    ancestors = [t for t in taxon.get_ancestors() if t.rank in main_ranks]
    return {'taxon': taxon, 'ancestors': ancestors}

@register.inclusion_tag('tree.html', takes_context=True)
def show_tree(context):
    '''Gera árvore taxonômica.'''
    taxa = Taxon.tree.all()
    return {'taxa': taxa}

@register.inclusion_tag('hot_images.html')
def show_hot():
    '''Mostra imagens mais acessadas.'''
    # XXX Precisa ser repensado.
    hot_images = Image.objects.order_by('-view_count')[:4]
    return {'hot_images': hot_images}

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
    '''Processa resultado do queryset.

    Busca o metadado, encontra o índice da imagem e reduz amostra. Usado para navegador linear.
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
    '''Retorna queryset de vídeo ou foto, baseado no datatype.
    
    Usado no navegador linear.
    '''
    if media.datatype == 'photo':
        query = Image.objects.filter(qobj, is_public=True).distinct().select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').order_by('id')
    elif media.datatype == 'video':
        query = Video.objects.filter(qobj, is_public=True).distinct().select_related('size', 'sublocation', 'city', 'state', 'country', 'rights').defer('source_filepath', 'old_filepath').order_by('id')
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
    photos = Image.objects.filter(is_public=True).count()
    videos = Video.objects.filter(is_public=True).count()
    tags = Tag.objects.count()
    spp = Taxon.objects.filter(rank=u'Espécie').count()
    locations = Sublocation.objects.count()
    return {'photos': photos, 'videos': videos, 'spp': spp, 'locations': locations}

@register.inclusion_tag('tree.html')
def show_tree():
    '''Passa objeto para gerar árvore.'''
    taxa = Taxon.tree.select_related().all()
    return {'taxa': taxa}

@register.inclusion_tag('searchbox.html')
def search_box():
    '''Gera buscador para ser usado no header do site.'''
    form = SearchForm()
    return {'form': form}

@register.filter
def sp_em(meta, autoescape=None):
    '''Filtro que aplica itálico à espécies e gêneros.'''
    # Tem que levar em conta tradução...
    italics = [
            u'Gênero', u'Genus',
            u'Subgênero', u'Subgenus',
            u'Espécie', u'Species'
            ]
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    try:
        if meta.rank in italics:
            output = u'<em>%s</em>' % esc(meta.name)
        else:
            output = esc(meta.name)
    except:
        output = esc(meta.name)
    return mark_safe(output)
sp_em.needs_autoescape = True

@register.filter
def fielter(field):
    '''Converte nome do campo em nome apresentável (taxon>Táxon).'''
    if field == 'tag':
    	return u'Marcador'
    elif field == 'author':
        return u'Autor'
    elif field == 'source':
        return u'Especialista'
    elif field == 'taxon':
        return u'Táxon'
    elif field == 'size':
        return u'Tamanho'
    elif field == 'sublocation':
        return u'Local'
    elif field == 'city':
        return u'Cidade'
    elif field == 'state':
        return u'Estado'
    elif field == 'country':
        return u'País'
    elif field == 'reference':
        return u'Referência'
    else:
    	return u'ERRO'

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

@register.inclusion_tag('mais.html')
def show_info(image_list, video_list, queries):
    '''Extrair metadados e exclui o que estiver nas queries.
    
    Manda a lista de imagens e de vídeos para a função extract_set que vai extrair todos os metadados associados a estes arquivos.
    
    Para identificar os valores que estão sendo procurados (queries), estes são excluídos de cada lista correspondente de metadados (authors, taxa, etc.)
    '''
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
    return {'actives': actives, 'inactives': inactives,
            'field': field, 'queries': queries}

@register.inclusion_tag('fino.html')
def refiner(actives, inactives, field, queries):
    '''Gera lista de metadados ativos e inativos.'''
    return {'actives': actives, 'inactives': inactives,
            'field': field, 'queries': queries}

@register.simple_tag
def paged_url(query_string, page_number):
    '''Constrói o url para lidar navegação paginada.'''
    print query_string.split('&'), page_number
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

@register.simple_tag
def build_url(meta, field, queries, remove=False):
    '''Constrói o url para lidar com o refinamento.
    
    Estou usando a infra para remover o tipo (photo/video) do url 
    (remove=True). Se remove=False a adição não vai funcionar, se for preciso 
    acrescentar código para lidar com o type.
    '''
    first = True
    prefix = '/buscar/?' 

    # Se for para remover o metadado, remover.
    if remove:
        try:
            queries[field] = queries[field].exclude(slug=meta.slug)
        except:
            # Só por segurança diferenciar o tamanho.
            if field == 'size':
                queries[field].remove(str(meta.id))
            elif field == 'type':
                queries[field] = []
            else:
                queries[field].remove(meta.slug)
    else:
        # Adiciona (ou retira) o metadado na lista de queries.
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
            type_field = False
            if isinstance(v, list):
                final_list = v
            else:
                if k == 'size':
                    final_list = v.values_list('id', flat=True)
                    final_list = [str(n) for n in final_list]
                elif k == 'query':
                    search = v
                    search_field = True
                elif k == 'type':
                    type = v
                    type_field = True
                else:
                    final_list = v.values_list('slug', flat=True)
            if search_field or type_field:
                if search_field:
                    prefix = prefix + search
                if type_field:
                    prefix = prefix + type
            else:
                prefix = prefix + ','.join(final_list)
    if prefix[-1] == '?':
        prefix = prefix[:-1]
    url = prefix
    # É preciso recolocar o meta removido para não afetar os urls seguintes.
    if remove:
        # Adiciona o metadado na lista de queries.
        queries[field] = add_meta(meta, field, queries[field])
    else:
        # Como modificações no queries passa para próximos ítens, é necessário
        # retirar o valor da variável (do queries) após criação do url.
        if field == 'size':
            try:
                queries[field].remove(str(meta.id))
            except:
                queries[field] = queries[field].exclude(id=meta.id)
        else:
            try:
                queries[field].remove(meta.slug)
            except:
                queries[field] = queries[field].exclude(slug=meta.slug)
    return url

@register.inclusion_tag('sets.html')
def show_set(set, prefix, suffix, sep, method='name'):
    '''Gera série a partir de um set.

    Pega os elementos do set e cria lista separada por vírgulas ou qualquer outro separador. Um prefixo e um sufixo também podem ser indicados, além do método ('link' gera url, 'slug' gera slug e vazio mostra o nome normal).
    '''
    return {'set': set, 'prefix': prefix, 'suffix': suffix, 'sep': sep, 'method': method}

def extract_set(image_list, video_list):
    '''Extrai outros metadados das imagens buscadas.'''
    # XXX Q vídeos deixou meio lento, tem como melhorar?
    # Salva IDs dos arquivos em uma lista.

    # Imagens.
    image_ids = []
    try:
        image_values = image_list.values()
        for image in image_values.iterator():
            image_ids.append(image['id'])
    except:
        pass

    # Vídeos.
    video_ids = []
    try:
        video_values = video_list.values()
        for video in video_values.iterator():
            video_ids.append(video['id'])
    except:
        pass

    # ManyToMany relationships
    refined_tags = Tag.objects.filter(
            Q(images__pk__in=image_ids) | Q(videos__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_authors = Author.objects.filter(
            Q(images__pk__in=image_ids) | Q(videos__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_taxa = Taxon.objects.filter(
            Q(images__pk__in=image_ids) | Q(videos__pk__in=video_ids)
            ).distinct().order_by('name')

    # ForeignKey relationships
    refined_sizes = Size.objects.filter(
            Q(image__pk__in=image_ids) | Q(video__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_sublocations = Sublocation.objects.filter(
            Q(image__pk__in=image_ids) | Q(video__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_cities = City.objects.filter(
            Q(image__pk__in=image_ids) | Q(video__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_states = State.objects.filter(
            Q(image__pk__in=image_ids) | Q(video__pk__in=video_ids)
            ).distinct().order_by('name')
    refined_countries = Country.objects.filter(
            Q(image__pk__in=image_ids) | Q(video__pk__in=video_ids)
            ).distinct().order_by('name')

    return refined_authors, refined_taxa, refined_sizes, refined_sublocations, refined_cities, refined_states, refined_countries, refined_tags

def add_meta(meta, field, query):
    '''Adiciona metadado à lista de query.

    Se a lista estiver vazia simplesmente cria uma nova com o metadado. Caso a lista já exista e tenha elementos, adiciona o metadado à ela.
    '''
    # Se o campo estiver vazio, já preencher com o valor do meta.
    if not query:
        if field == 'size':
            query = [str(meta.id)]
        elif field == 'type':
            query = [meta]
        else:
            query = [meta.slug]
    # Se o campo não estiver vazio, adicionar o valor do meta ao final.
    else:
        # Se for para remover o metadado, retirar do url.
        if isinstance(query, list):
            values_list = query
        else:
            if field == 'type':
                query = [meta]
                return query
            elif field == 'size':
                values_list = query.values_list('id', flat=True)
                values_list = [str(n) for n in values_list]
            else:
                values_list = query.values_list('slug', flat=True)
        query = [meta.slug]
        query.extend(values_list)
    return query
