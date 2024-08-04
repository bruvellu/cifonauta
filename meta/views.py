# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import json

from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Count
from django.db.models.functions import Lower
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.aggregates import StringAgg
from functools import reduce
from utils.media import Metadata, number_of_entries_per_page, format_name
from utils.taxa import TaxonUpdater
from operator import or_, and_
from PIL import Image

import datetime as date

from .models import *
from .forms import *

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from .decorators import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.models import UserCifonauta
from cifonauta.settings import MEDIA_EXTENSIONS, FILENAME_REGEX, MEDIA_ROOT
from django.core.files import File
from django.utils.translation import get_language, get_language_info
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReferenceSerializer, TaxonSerializer, LocationSerializer, CoauthorSerializer
from utils.views import execute_bash_action

from dotenv import load_dotenv
load_dotenv()


@api_view(['POST'])
def create_reference(request):
    serializer = ReferenceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response('Referência já existe', status=status.HTTP_409_CONFLICT)
    return Response(serializer.data)

@api_view(['POST']) 
def create_taxa(request):
    request_data = request.data.copy()
    #TODO: format_name function is tailored for people's names. Species' names have a different formatting, see TaxonUpdater.sanitize_name() method (applied below). Either call sanitize_name here or get sanitized taxon name from TaxonUpdater below and save to the serializer object.
    #request_data['name'] = format_name(request_data['name'])
    request_data['name'] = request_data['name'].strip().lower().capitalize()
    
    serializer = TaxonSerializer(data=request_data)
    if serializer.is_valid():
        taxon_name = serializer.validated_data['name']
        try:
            taxon = Taxon.objects.get(name_iexact=taxon_name)
            if taxon:
                return Response('Táxon com esse nome já existe.', status=status.HTTP_409_CONFLICT)
        except:
            pass
        serializer.save()

        return Response({ "message": 'Táxon adicionado com sucesso', "data": serializer.data })

    return Response('Táxon com esse nome já existe.', status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def create_location(request):
    request_data = request.data.copy()
    request_data['name'] = format_name(request_data['name'])

    serializer = LocationSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
        return Response({ "message": 'Local adicionado com sucesso', "data": serializer.data })

    return Response('Local com esse nome já existe.', status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def create_authors(request):
    request_data = request.data.copy()
    request_data['name'] = format_name(request_data['name'])

    serializer = CoauthorSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
        return Response({ "message": 'Coautor registrado com sucesso', "data": serializer.data })
    
    return Response('Coautor com esse nome já existe.', status=status.HTTP_409_CONFLICT)


@never_cache
@authentication_required
def dashboard(request):
    is_specialist = Curadoria.objects.filter(Q(specialists=request.user)).exists()
    is_curator = Curadoria.objects.filter(Q(curators=request.user)).exists()

    context = {
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'dashboard.html', context)


@never_cache
@author_required
def upload_media_step1(request):

    if request.method == 'POST':

        # Files selected via upload form
        files = request.FILES.getlist('files')

        if files:
            user_person = Person.objects.filter(user_cifonauta=request.user.id)

            # Iterate over multiple files
            for file in files:

                # Prevent upload of large files
                if file.size > 3000000:
                    messages.error(request, 'Arquivo maior que 3MB')
                    return redirect('upload_media_step1')

                # Split lower cased name and extension
                filename, extension = os.path.splitext(file.name.lower())

                #TODO: Use elif for capturing every possibility
                #TODO: Also check for content_type
                
                if extension:
                    if not re.match(FILENAME_REGEX, filename):
                        messages.error(request, f'Nome de arquivo inválido: {file.name}')
                        messages.warning(request, 'Caracteres especiais aceitos: - _ ( )')
                        return redirect('upload_media_step1')
                    
                    if not extension.endswith(MEDIA_EXTENSIONS):
                        messages.error(request, f'Formato de arquivo não aceito: {file.name}')
                        messages.warning(request, 'Verifique os tipos de arquivos aceitos')
                        return redirect('upload_media_step1')
                else:
                    messages.error(request, f'Arquivo inválido: {file.name}')
                    return redirect('upload_media_step1')

            #TODO: Don't loop twice
            for file in files:
                # Create empty Media instance for new UUID
                media = Media()
                # Rename file name with UUID and lowercase extension
                file_noext, extension = os.path.splitext(file.name.lower())
                file.name = f'{media.uuid}{extension}'

                # Define file field of Media instance
                media.file = file
                # Define user field of Media instance
                media.user = request.user
                # Define if media is a photo or a video
                if extension.endswith(settings.PHOTO_EXTENSIONS):
                    media.datatype = 'photo'
                elif extension.endswith(settings.VIDEO_EXTENSIONS):
                    media.datatype = 'video'

                # Save instance
                media.save()

                # Define the user as author
                media.authors.set(user_person)

            messages.success(request, 'Mídias carregadas com sucesso')
            messages.info(request, 'Preencha os dados para completar o upload')
            return redirect('upload_media_step2')

        messages.error(request, 'Por favor, selecione as mídias')
        return redirect('upload_media_step1')

    if Media.objects.filter(user=request.user, status='loaded').exists():
        messages.warning(request, 'Você tem mídias carregadas')
        messages.info(request, 'Complete ou cancele o upload para adicionar outras mídias')
        return redirect('upload_media_step2')
    
    media_extensions = ''
    for media_extension in MEDIA_EXTENSIONS:
        media_extensions += f'{media_extension[1:].upper()} '

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'media_extensions': media_extensions,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'upload_media_step1.html', context)


@never_cache
@loaded_media_required
def upload_media_step2(request):
    medias = Media.objects.filter(user=request.user, status='loaded')
    user_person = Person.objects.get(user_cifonauta=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cancel':
            medias.delete()
            messages.success(request, 'Upload de mídias cancelado com sucesso')
            return redirect('upload_media_step1')
        else:
            form = UploadMediaForm(request.POST, request.FILES, media_author=user_person)
            
            if form.is_valid():
                for media in medias:
                    specific_form = UploadMediaForm(request.POST, request.FILES, media_author=user_person, instance=media)
                    
                    # Create media instance from form and set status to draft
                    media_instance = specific_form.save()
                    media_instance.status = 'draft'

                    # Create media files with different dimensions
                    media_instance.resize_files()

                    # Set sitepath and coverpath from new fields
                    #TODO: Temporary workaround until fields are removed
                    media_instance.sitepath = media_instance.file_medium
                    media_instance.coverpath = media_instance.file_cover

                    #Update taxons
                    not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                    for taxon in form.cleaned_data['taxa']:
                        if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                            with Taxon.objects.disable_mptt_updates():
                                update = TaxonUpdater(taxon.name)
                            Taxon.objects.rebuild()
                            if update.status == 'not_exist':
                                curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                                curadory.taxons.add(taxon)
                            else:
                                curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                                curadory.taxons.add(taxon)
                        if taxon.valid_taxon != None:
                            media_instance.taxa.add(taxon.valid_taxon)
                            media_instance.taxa.remove(taxon)
                            curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                            curadory.taxons.add(taxon.valid_taxon)
                                    
                    # Save media instance
                    media_instance.save() #TODO: Move down (last)
                    
                # Send email 
                curations = Curadoria.objects.filter(taxons__in=form.cleaned_data['taxa'])
                specialists_user = set()
                for curation in curations:
                    for specialist in curation.specialists.all():
                        specialists_user.add(specialist)
                
                form.send_mail(request.user, specialists_user, medias, 'Nova mídia para edição no Cifonauta', 'email_media_to_editing_specialists.html')
                messages.success(request, 'As mídias foram enviadas para o especialista editar.')
                messages.info(request, 'Você ainda pode editá-las antes de serem submetidas para o curador.')
                return redirect('my_media_list')

            messages.error(request, 'Houve um erro ao tentar salvar mídia(s)')

    else:
        form = UploadMediaForm(initial={'authors': user_person.id})
        form.fields['state'].queryset = State.objects.none()
        form.fields['city'].queryset = City.objects.none()

        metadata = None
        for media in medias:
            # print(media.file.name)
            try:
                metadata = Metadata(f'{MEDIA_ROOT}/{media.file.name}')
                try:
                    read_metadata = metadata.read_metadata()
                except Exception as error:
                    print(error)
                    metadata = None
                finally:
                    break
            except:
                print('Erro')
                pass        
        
        if metadata:
            # print(read_metadata)
            authors = []
            authors_meta = read_metadata['authors'].split(',')
            for author in authors_meta:
                if author.strip() != '':
                    try:
                        authors.append(Person.objects.filter(name=author.strip()).get().id)
                    except:
                        messages.error(request, f'O Co-Autor {author.strip()} não está cadastrado.')
            if user_person.id not in authors:
                authors.append(user_person.id)
        
            if read_metadata['datetime'] != '':
                datetime = read_metadata['datetime']
            else:
                datetime = '1900:01:01'

            if not read_metadata['gps']:
                latitude = ''
                longitude = ''
            else:
                latitude = read_metadata['gps']['latitude']
                longitude = read_metadata['gps']['longitude']

            form = UploadMediaForm(initial={
                'authors': authors,
                'title_pt_br': read_metadata['title_pt'],
                'title_en': read_metadata['title_en'],
                'caption_pt_br': read_metadata['description_pt'],
                'caption_en': read_metadata['description_en'],
                'latitude': latitude,
                'longitude': longitude,
                'date_created': datetime
            })

    authors_form = AddAuthorsForm()
    location_form = AddLocationForm()
    taxa_form = AddTaxaForm()
    
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'authors_form': authors_form,
        'location_form': location_form,
        'taxa_form': taxa_form,
        'medias': medias,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'upload_media_step2.html', context)


def synchronize_fields(request):
    if request.GET.get('country_id'):
        country_id = request.GET.get('country_id')

        query = State.objects.filter(country_id=country_id)

        data = {
            'states': list(query.values('id', 'name'))
        }

        return JsonResponse(data)

    if request.GET.get('state_id'):
        state_id = request.GET.get('state_id')
        
        query = City.objects.filter(state_id=state_id)

        data = {
            'cities': list(query.values('id', 'name'))
        }

        return JsonResponse(data)
    
    return JsonResponse({})


@never_cache
@media_specialist_required
def editing_media_details(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    
    if request.method == 'POST':
        action = request.POST.get('action', None)

        form = EditMetadataForm(request.POST, instance=media, editing_media_details=True)

        action = request.POST.get('action')

        if action == 'submit':
            form.fields['title_pt_br'].required = True
            form.fields['title_en'].required = True
            
        if form.is_valid():
            media_instance = form.save()
            
            if action == 'submit':
                media_instance.status = 'submitted'

            person = Person.objects.filter(user_cifonauta=request.user.id).first()
            media_instance.specialists.add(person)

            #Update taxons
            not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
            for taxon in form.cleaned_data['taxa']:
                if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                    with Taxon.objects.disable_mptt_updates():
                        update = TaxonUpdater(taxon.name)
                    Taxon.objects.rebuild()
                    if update.status == 'not_exist':
                        curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                        curadory.taxons.add(taxon)
                    else:
                        curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                        curadory.taxons.add(taxon)
                if taxon.valid_taxon != None:
                    media_instance.taxa.add(taxon.valid_taxon)
                    media_instance.taxa.remove(taxon)
                    curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                    curadory.taxons.add(taxon.valid_taxon)

            media_instance.save()

            if action == 'submit':
                author = UserCifonauta.objects.filter(id=media.user.id)
                form.send_mail(request.user, author, [media], 'Mídia enviada para revisão no Cifonauta', 'email_media_to_revision_author.html')

                curations = Curadoria.objects.filter(taxons__in=form.cleaned_data['taxa'])
                curators_user = set()
                for curation in curations:
                    for curator in curation.curators.all():
                        curators_user.add(curator)

                form.send_mail(request.user, curators_user, media, 'Fluxo da mídia no Cifonauta', 'email_media_to_revision_curators.html')

            if action == 'submit':
                messages.success(request, f'A mídia ({media.title}) foi enviada para revisão com sucesso')
            else:
                messages.success(request, f'A mídia ({media.title}) foi salva com sucesso')
                messages.warning(request, f'Você ainda não a enviou para revisão')


            return redirect('editing_media_list')
        else:
            messages.error(request, 'Houve um erro ao tentar salvar mídia')

    else:
        form = EditMetadataForm(instance=media, editing_media_details=True)    
    
    if media.state:
        form.fields['city'].queryset = City.objects.filter(state=media.state.id)
    else:
        form.fields['city'].queryset = City.objects.none()
    if media.country:
        form.fields['state'].queryset = State.objects.filter(country=media.country.id)
    else:
        form.fields['state'].queryset = State.objects.none()
    form.fields['title_pt_br'].required = False
    form.fields['title_en'].required = False

    location_form = AddLocationForm()
    taxa_form = AddTaxaForm()

    # media = get_object_or_404(Media, pk=media_id)
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'location_form': location_form,
        'taxa_form': taxa_form,
        'media': media,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'editing_media_details.html', context) 

def search_media(queryset, query):
    '''Search Media's search vector and return filtered queryset.'''

    # Get language.
    language = get_language()

    # Change search config based on language
    if language == 'en':
        langconfig = 'english'
    elif language == 'pt-br':
        langconfig = 'portuguese_unaccent'

    # Create SearchQuery
    search_query = SearchQuery(query, config=langconfig)

    # Create SearchRank
    search_rank = SearchRank(F('search_vector'), search_query)

    # Filter media_list by search_query
    filtered_queryset = queryset.annotate(rank=search_rank).filter(search_vector=search_query)

    return filtered_queryset


def filter_medias(queryset, query_dict, curations=''):
    filtered_queryset = queryset

    search_value = query_dict.get('search', None)
    if 'search' in query_dict and search_value != '':
        filtered_queryset = search_media(filtered_queryset, search_value)

    curation_ids = query_dict.getlist('curations', None)
    if curation_ids:
        if curations:
            filtered_curations = curations.filter(id__in=curation_ids).distinct()
        else:
            filtered_curations = Curadoria.objects.filter(id__in=curation_ids).distinct()

        taxons = set()
        for curation in filtered_curations:
            taxons.update(curation.taxons.all())

        filtered_queryset = filtered_queryset.filter(taxa__in=taxons)


    status = query_dict.getlist('status', None)
    if status:
        filtered_queryset = filtered_queryset.filter(status__in=status)


    alphabetical_order = query_dict.get('alphabetical_order', None)
    if alphabetical_order:
        filtered_queryset = filtered_queryset.order_by('title')

    # print(query_dict)
    return filtered_queryset


@never_cache
@specialist_required
def editing_media_list(request):
    records_number = number_of_entries_per_page(request, 'entries_curadoria_media_list')

    user = request.user
    curations = user.curatorship_specialist.all()
    curations_taxons = set()

    for curadoria in curations:
        taxons = curadoria.taxons.all()
        curations_taxons.update(taxons)

    queryset = Media.objects.filter(status='draft').filter(taxa__in=curations_taxons).distinct().order_by('-date_modified')

    if request.method == "POST":
        action = request.POST['action']
        
        if action == 'entries_number':
            records_number = number_of_entries_per_page(request, 'entries_curadoria_media_list', request.POST['entries_number'])
        else:
            media_ids = request.POST.getlist('selected_media_ids')

            if media_ids:
                form = BashActionsForm(request.POST, view_name='editing_media_list')

                if form.is_valid():
                    medias = Media.objects.filter(id__in=media_ids)

                    for media in medias:
                        if media.status == 'submitted':
                            messages.error(request, 'Não é possível realizar ação em lotes de mídia já submetida para revisão')
                            return redirect('editing_media_list')

                        if form.cleaned_data['status_action'] != 'maintain':
                            if not media.title_pt_br or not media.title_en:
                                messages.error(request, 'Não é possível submeter mídia com campos obrigatórios faltando')
                                return redirect('editing_media_list')
                        
                        #Update taxons
                        #TODO: Revise this code, it breaks when batch updating without taxa
                        # A quick fix is below.
                        if 'taxa' in form.cleaned_data.keys():
                            not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                            for taxon in form.cleaned_data['taxa']:
                                if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                                    with Taxon.objects.disable_mptt_updates():
                                        update = TaxonUpdater(taxon.name)
                                    Taxon.objects.rebuild()
                                    if update.status == 'not_exist':
                                        curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                                        curadory.taxons.add(taxon)
                                    else:
                                        curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                                        curadory.taxons.add(taxon)
                                if taxon.valid_taxon != None:
                                    media.taxa.add(taxon.valid_taxon)
                                    media.taxa.remove(taxon)
                                    curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                                    curadory.taxons.add(taxon.valid_taxon)
                    media.save()

                    error = execute_bash_action(request, medias, user, 'editing_media_list')
                    if error:
                        return redirect('editing_media_list')

                    if form.cleaned_data['status_action'] != 'maintain':
                        authors = set()
                        for media in medias:
                            authors.add(media.user)

                        form.send_mail(request.user, authors, medias, 'Mídia publicada no Cifonauta', 'email_media_to_revision_author.html')

                        curations = []
                        if form.cleaned_data['taxa_action'] != 'maintain':
                            curations = Curadoria.objects.filter(taxons__in=form.cleaned_data['taxa'])
                        else:
                            taxons = Taxon.objects.filter(media__id__in=media_ids).distinct()
                            curations = Curadoria.objects.filter(taxons__in=taxons)
                        curators_user = set()
                        for curation in curations:
                            for curator in curation.curators.all():
                                curators_user.add(curator)

                        form.send_mail(request.user, curators_user, medias, 'Fluxo da mídia no Cifonauta', 'email_media_to_revision_curators.html')
                    


                    messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
                else:
                    messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
            else:
                messages.warning(request, _('Nenhum registro foi selecionado'))

    query_dict = request.GET.copy()
    filtered_queryset = filter_medias(queryset, query_dict, curations)
    
    filter_form = DashboardFilterForm(query_dict, user_curations=curations, is_editing_media_list=True)
    

    queryset_paginator = Paginator(filtered_queryset, records_number)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    form = BashActionsForm(view_name='editing_media_list')
    taxa_form = AddTaxaForm()
    location_form = AddLocationForm()

    context = {
        'records_number': records_number,
        'form': form,
        'filter_form': filter_form,
        'taxa_form': taxa_form,
        'location_form': location_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': user.curatorship_specialist.exists(),
        'is_curator': user.curatorship_curator.exists(),
        'list_page': True
    }

    return render(request, 'editing_media_list.html', context)
    

@never_cache
@media_owner_required
def my_media_details(request, pk):
    media = get_object_or_404(Media, pk=pk)
    modified_media = ModifiedMedia.objects.filter(media=media).first()
    user_person = Person.objects.get(user_cifonauta=request.user)

    is_modification_owner = False
    if modified_media and modified_media.modification_person == user_person:
        is_modification_owner = True
    
    if request.method == 'POST':
        action = request.POST.get('action', None)

        if action == 'discard':
            modified_media.delete()
            messages.success(request, "Alterações discartadas com sucesso")
            return redirect('my_media_details', pk)
        
        if media.status == 'submitted':
            messages.error(request, f'Não foi possível fazer alteração')
            return redirect('my_media_details', pk)

        if modified_media and not modified_media.altered_by_author:
            messages.error(request, "Não é possível realizar mudanças em uma mídia com alterações pendentes.")

            return redirect('my_media_details', pk)

        form = UpdateMyMediaForm(request.POST, instance=media, media_author=user_person, media_status=media.status)
        if form.is_valid():
            if media.status == 'published':
                if modified_media:
                    if modified_media.altered_by_author:
                        if form.has_changed():
                            form = UpdateMyMediaForm(request.POST, instance=modified_media, media_author=user_person, media_status=media.status)

                            form.save()

                        else:
                            messages.error(request, 'Mudança igual à versão publicada no site')
                            messages.warning(request, 'Descarte a alteração pendente ou efetue uma alteração válida')
                            return redirect('my_media_details', media.pk)
                    else:
                        messages.warning(request, "Esta mídia tem alterações pendentes de um especialista. Não é possível realizar alterações até que elas sejam revisadas pelo curador")
                        return redirect('my_media_details', pk)

                else:
                    if form.has_changed():
                        new_modified_media = ModifiedMedia(media=media, modification_person=user_person)
                        form = UpdateMyMediaForm(request.POST, instance=new_modified_media, media_author=user_person, media_status=media.status)

                        form.save()

                    else:
                        messages.error(request, 'Nenhuma alteração identificada')
                        return redirect('my_media_details', media.pk)
                
                messages.success(request, 'Informações alteradas com sucesso')
                messages.warning(request, 'As alterações serão avaliadas e podem ou não serem aceitas')
            else:
                if media.status == 'submitted' and not form.has_changed():
                    messages.error(request, 'Nenhuma alteração identificada')
                    return redirect('my_media_details', media.pk)

                media_instance = form.save()

                media_instance.status = 'draft'

                media_instance.save()

                messages.success(request, 'Informações alteradas com sucesso')
            
            #Update taxons
            not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
            for taxon in form.cleaned_data['taxa']:
                if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                    with Taxon.objects.disable_mptt_updates():
                        update = TaxonUpdater(taxon.name)
                    Taxon.objects.rebuild()
                    if update.status == 'not_exist':
                        curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                        curadory.taxons.add(taxon)
                    else:
                        curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                        curadory.taxons.add(taxon)
                if taxon.valid_taxon != None:
                    media.taxa.add(taxon.valid_taxon)
                    media.taxa.remove(taxon)
                    curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                    curadory.taxons.add(taxon.valid_taxon)

            media.save()

            return redirect('my_media_details', pk)
        

        messages.error(request, 'Houve um erro com as alterações feitas')
    else:
        form = UpdateMyMediaForm(instance=media, media_status=media.status)

    if modified_media:
        if not messages.get_messages(request):
            if modified_media.altered_by_author:
                messages.warning(request, "Esta mídia tem alterações pendentes. Clique no botão abaixo para ver as alterações. Se você fizer novas alterações, as anteriores serão sobrepostas")
            elif not is_modification_owner:
                messages.warning(request, "Esta mídia tem alterações pendentes de um especialista. Não é possível realizar alterações até que elas sejam revisadas pelo curador")
        if is_modification_owner and not modified_media.altered_by_author:
            url = reverse('my_curations_media_details', args=[pk])
            messages.warning(request, f'Esta mídia tem alterações sua como especialista. Para vê-las, <a href={url}>Clique aqui</a>')
    elif media.status == 'submitted':
        messages.warning(request, "Não é possível fazer alteração em mídias que estão submetidas para revisão")

    if media.state:
        form.fields['city'].queryset = City.objects.filter(state=media.state.id)
    else:
        form.fields['city'].queryset = City.objects.none()
    if media.country:
        form.fields['state'].queryset = State.objects.filter(country=media.country.id)
    else:
        form.fields['state'].queryset = State.objects.none()
    if media.status == 'published':
        license_choices = [choice[0] for choice in Media.LICENSE_CHOICES]
        license_index = license_choices.index(media.license)
        form.fields['license'].choices = Media.LICENSE_CHOICES[:license_index + 1]

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    authors_form = AddAuthorsForm()
    location_form = AddLocationForm()
    taxa_form = AddTaxaForm()
    modified_media_form = ModifiedMediaForm(instance=media, author_form=True)

    context = {
        'media': media,
        'modified_media': modified_media,
        'modified_media_form': modified_media_form,
        'form': form,
        'authors_form': authors_form,
        'location_form': location_form,
        'taxa_form': taxa_form,
        'is_modification_owner': is_modification_owner,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'my_media_details.html', context)
    

@never_cache
@author_required
def my_media_list(request):
    records_number = number_of_entries_per_page(request, 'entries_my_medias')

    user = request.user
    user_person = Person.objects.filter(user_cifonauta=user).first()
    queryset = Media.objects.filter(user=user).exclude(status='loaded').order_by('-pk')

    if request.method == "POST":
        action = request.POST['action']

        if action == 'entries_number':
            records_number = number_of_entries_per_page(request, 'entries_my_medias', request.POST['entries_number'])
        else:
            media_ids = request.POST.getlist('selected_media_ids')

            if media_ids:
                form = BashActionsForm(request.POST, view_name='my_media_list')

                if form.is_valid():
                    medias = Media.objects.filter(id__in=media_ids)

                    has_published_media = medias.filter(status='published').exists()
                    if has_published_media:
                        messages.error(request, _('Não é possível realizar ação em lotes de mídia já publicada'))
                        return redirect('my_media_list')
                    
                    has_submitted_media = medias.filter(status='submitted').exists()
                    if has_submitted_media:
                        messages.error(request, _('Não é possível realizar ação em lotes de mídia submetida para revisão'))
                        return redirect('my_media_list')

                    error = execute_bash_action(request, medias, user, 'my_media_list')
                    if error:
                        return redirect('my_media_list')

                    messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
                else:
                    messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
            else:
                messages.warning(request, _('Nenhum registro foi selecionado'))

    query_dict = request.GET.copy()
    filtered_queryset = filter_medias(queryset, query_dict)
    
    filter_form = DashboardFilterForm(query_dict)

    user = request.user
    queryset = Media.objects.filter(user=user).exclude(status='loaded').order_by('-pk')
    
    form = BashActionsForm(view_name='my_media_list', user_person=user_person)
    taxa_form = AddTaxaForm()
    authors_form = AddAuthorsForm()
    location_form = AddLocationForm()

    is_specialist = user.curatorship_specialist.exists()
    is_curator = user.curatorship_curator.exists()

    queryset_paginator = Paginator(filtered_queryset, records_number)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    context = {
        'records_number': records_number,
        'form': form,
        'filter_form': filter_form,
        'taxa_form': taxa_form,
        'location_form': location_form,
        'authors_form': authors_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
        'list_page': True
    }

    return render(request, 'my_media_list.html', context)


@never_cache
@curator_required
def manage_users(request):
    users_queryset = UserCifonauta.objects.all().exclude(id=request.user.id)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'enable-authors':
            author_ids = request.POST.getlist('author_ids')

            authors = UserCifonauta.objects.filter(id__in=author_ids)
            not_authors = UserCifonauta.objects.exclude(Q(id__in=author_ids) | Q(id=request.user.id))

            for user in not_authors:
                if user.uploaded_media.all():
                    messages.error(request, f'O usuário "{user.first_name} {user.last_name}" possui mídia relacionada')
                    return redirect('manage_users')

                user.curatorship_specialist.clear()
                user.curatorship_curator.clear()
                
            authors.update(is_author=True)
            not_authors.update(is_author=False)

            messages.success(request, "Os autores foram atualizados com sucesso")
        else:
            specialist_ids = request.POST.getlist('specialist_ids')
            curatorship_id = request.POST.get('curatorship_id')

            specialists = UserCifonauta.objects.filter(id__in=specialist_ids)
            curatorship = Curadoria.objects.filter(id=curatorship_id).first()
            curatorship.specialists.set(specialists)

            messages.success(request, "Os especialistas foram atualizados com sucesso")

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    curatorships = Curadoria.objects.filter(curators=request.user.id)
    authors_queryset = UserCifonauta.objects.filter(is_author=True).exclude(id=request.user.id)
    
    users = [
        {
            'name': f'{user.first_name} {user.last_name}',
            'id': user.id,
            'is_author': user.is_author,
            'curatorship_ids': [str(curatorship.id) for curatorship in curatorships.filter(Q(specialists=user.id))]
        } for user in users_queryset
    ]

    authors = [
        {
            'name': f'{user.first_name} {user.last_name}',
            'id': user.id,
            'curatorship_ids': [str(curatorship.id) for curatorship in curatorships.filter(Q(specialists=user.id))]
        } for user in authors_queryset
    ]

    context = {
        'users': users,
        'authors': authors,
        'curatorships': curatorships,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }
    return render(request, 'manage_users.html', context)        


@never_cache
@curator_required
def revision_media_list(request):
    records_number = number_of_entries_per_page(request, 'entries_revision_media')

    user = request.user

    curations = user.curatorship_curator.all()
    curations_taxons = set()

    for curadoria in curations:
        taxons = curadoria.taxons.all()
        curations_taxons.update(taxons)
    
    queryset = None

    queryset = Media.objects.filter(
        Q(status='submitted') & Q(taxa__in=curations_taxons) |
        Q(modified_media__taxa__in=curations_taxons))

    queryset = queryset.distinct().order_by('-date_modified')

    if request.method == 'POST':
        action = request.POST['action']
        
        if action == 'entries_number':
            records_number = number_of_entries_per_page(request, 'entries_revision_media', request.POST['entries_number'])
        else:
            media_ids = request.POST.getlist('selected_media_ids')

            if media_ids:
                form = BashActionsForm(request.POST, view_name='revision_media_list')

                if form.is_valid():
                    medias = Media.objects.filter(id__in=media_ids)

                    is_published = medias.filter(status='published')
                    if is_published:
                        messages.error(request, 'Não é possível realizar ação em lotes de mídia já publicada')
                        return redirect('revision_media_list')
                    
                    error = execute_bash_action(request, medias, user, 'revision_media_list')
                    if error:
                        return redirect('revision_media_list')

                    # Send email
                    if form.cleaned_data['status_action'] != 'maintain':
                        authors = set()
                        specialists = set()
                        for media in medias:
                            authors.add(media.user)

                            for specialist in media.specialists.all():
                                specialists.add(specialist)

                        form.send_mail(request.user, authors, medias, 'Mídia publicada no Cifonauta', 'email_published_media_author.html')

                        specialists_user = set()
                        for specialist in specialists:
                            specialists_user.add(specialist.user_cifonauta)

                        form.send_mail(request.user, specialists_user, medias, 'Fluxo da mídia no Cifonauta', 'email_published_media_specialists.html')

                    messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
                else:
                    messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
            else:
                messages.warning(request, _('Nenhum registro foi selecionado'))

    query_dict = request.GET.copy()
    filtered_queryset = filter_medias(queryset, query_dict, curations)
    
    filter_form = DashboardFilterForm(query_dict, user_curations=curations)
    
    queryset_paginator = Paginator(filtered_queryset, records_number)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    form = BashActionsForm(view_name='revision_media_list')
    taxa_form = AddTaxaForm()
    location_form = AddLocationForm()

    context = {
        'records_number': records_number,
        'form': form,
        'filter_form': filter_form,
        'taxa_form': taxa_form,
        'location_form': location_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': user.curatorship_specialist.exists(),
        'is_curator': user.curatorship_curator.exists(),
        'list_page': True
    }

    return render(request, 'revision_media_list.html', context)


@never_cache
@media_curator_required
def revision_modified_media(request, media_id):
    media = get_object_or_404(Media, pk=media_id)
    modified_media = ModifiedMedia.objects.filter(media=media).first() 

    if request.method == 'POST':
        action = request.POST['action']
        form = ModifiedMediaForm(request.POST)

        specialists_user = set()
        for specialist in media.specialists.all():
            specialists_user.add(specialist.user_cifonauta)

        if media.user in specialists_user:
            specialists_user.remove(media.user)

        if action == 'discard':
            form.send_mail(request.user, media.user, media, 'Alteração de mídia no Cifonauta', 'email_modified_media.html', modification_accepted=False)
        
            form.send_mail(request.user, specialists_user, media, 'Alteração de mídia no Cifonauta', 'email_modified_media.html', modification_accepted=False, modified_media_specialists_message=True)

            modified_media.delete()
            messages.success(request, 'Alteração descartada com sucesso')
            return redirect('revision_media_list')

        if form.is_valid():
            form = ModifiedMediaForm(request.POST, instance=media, author_form=True) if modified_media.altered_by_author else ModifiedMediaForm(request.POST, instance=media)
            form.save()

            if not modified_media.altered_by_author:
                media.specialists.add(modified_media.modification_person)

            for taxon in form.cleaned_data['taxa']:
                if taxon.valid_taxon != None:
                    modified_media.taxa.add(taxon.valid_taxon)
                    modified_media.taxa.remove(taxon)


            form.send_mail(request.user, media.user, media, 'Alteração de mídia no Cifonauta', 'email_modified_media.html', modification_accepted=True)

            form.send_mail(request.user, specialists_user, media, 'Alteração de mídia no Cifonauta', 'email_modified_media.html', modification_accepted=True, modified_media_specialists_message=True)

            modified_media.delete()

            media.update_metadata()

            messages.success(request, 'Alterações aceitas com sucesso')
            return redirect('revision_media_list')
        else:
            messages.error(request, 'Houve um erro ao tentar realizar a ação')


    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    form = ModifiedMediaForm(instance=modified_media, author_form=True) if modified_media.altered_by_author else ModifiedMediaForm(instance=modified_media)
    
    context = {
        'modified_media_form': form,
        'media': media,
        'modified_media': modified_media,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'revision_modified_media.html', context)


@never_cache
@media_curator_required
def revision_media_details(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    if request.method == 'POST':
        action = request.POST.get('action', None)
        
        form = EditMetadataForm(request.POST, instance=media)
        
        if form.is_valid():
            media_instance = form.save()

            # Set user as curator (?)
            person = Person.objects.filter(user_cifonauta=request.user.id).first()
            media_instance.curators.add(person)

            action = request.POST.get('action')
            if action == 'publish':
                media_instance.status = 'published'
                media_instance.is_public = True
                media_instance.update_metadata()
            for taxon in form.cleaned_data['taxa']:
                if taxon.valid_taxon != None:
                    media_instance.taxa.add(taxon.valid_taxon)
                    media_instance.taxa.remove(taxon)

            #Update taxons
            not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
            for taxon in form.cleaned_data['taxa']:
                if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                    with Taxon.objects.disable_mptt_updates():
                        update = TaxonUpdater(taxon.name)
                    Taxon.objects.rebuild()
                    if update.status == 'not_exist':
                        curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                        curadory.taxons.add(taxon)
                    else:
                        curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                        curadory.taxons.add(taxon)
                if taxon.valid_taxon != None:
                    media_instance.taxa.add(taxon.valid_taxon)
                    media_instance.taxa.remove(taxon)
                    curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                    curadory.taxons.add(taxon.valid_taxon)

            # Save instance
            media_instance.save()

            if action == 'publish':
                # TODO: Move to its own method?
                form.send_mail(request.user, media.user, media, 'Mídia publicada no Cifonauta', 'email_published_media_author.html')
                specialists_user = set()
                for specialist in media.specialists.all():
                    specialists_user.add(specialist.user_cifonauta)
                form.send_mail(request.user, specialists_user, media, 'Fluxo da mídia no Cifonauta', 'email_published_media_specialists.html')
                messages.success(request, f'A mídia ({media.title}) foi publicada com sucesso')
            else:
                messages.success(request, f'A mídia ({media.title}) foi salva com sucesso')
                messages.warning(request, f'Você ainda não a publicou')

            return redirect('revision_media_list')
        else:
            messages.error(request, f'Houve um erro ao tentar salvar a mídia')

    else: 
        form = EditMetadataForm(instance=media)

    if media.state:
        form.fields['city'].queryset = City.objects.filter(state=media.state.id)
    else:
        form.fields['city'].queryset = City.objects.none()
    if media.country:
        form.fields['state'].queryset = State.objects.filter(country=media.country.id)
    else:
        form.fields['state'].queryset = State.objects.none()
    
    location_form = AddLocationForm()
    taxa_form = AddTaxaForm()

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'location_form': location_form,
        'taxa_form': taxa_form,
        'media': media,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'revision_media_details.html', context) 


@never_cache
@specialist_or_curator_required
def my_curations_media_list(request):
    records_number = number_of_entries_per_page(request, 'entries_media_from_curation')

    user = request.user

    curations_as_specialist = user.curatorship_specialist.all()
    curations_as_specialist_taxons = set()
    for curation in curations_as_specialist:
        curations_as_specialist_taxons.update(curation.taxons.all())


    curations_as_curator = user.curatorship_curator.all()
    curations_as_curator_taxons = set()
    for curation in curations_as_curator:
        curations_as_curator_taxons.update(curation.taxons.all())

    curations = curations_as_specialist | curations_as_curator
    curations = curations.distinct()

    curations_taxons = set()
    for curation in curations:
        curations_taxons.update(curation.taxons.all())

    curator_queryset = Media.objects.filter(Q(taxa__in=curations_as_curator_taxons))

    specialist_queryset = Media.objects.filter(Q(taxa__in=curations_as_specialist_taxons))    

    queryset = (curator_queryset | specialist_queryset).exclude(status='loaded').distinct().order_by('-pk')

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'entries_number':
            records_number = number_of_entries_per_page(request, 'entries_media_from_curation', request.POST['entries_number'])
        else:
            media_ids = request.POST.getlist('selected_media_ids')

            if media_ids:
                form = BashActionsForm(request.POST, view_name='my_curations_media_list')

                if form.is_valid():
                    medias = Media.objects.filter(id__in=media_ids)
                    
                    for media in medias:
                        if media.status != 'published':
                            messages.error(request, 'Não é possível realizar ação em lotes de mídias não publicadas')
                            return redirect('my_curations_media_list')
                        
                        if media.modified_media.all().exists():
                            messages.error(request, "Não é possível realizar ação em lotes de mídias com alterações pendentes.")
                            return redirect('my_curations_media_list')

                        is_media_curator = False
                        for taxa in media.taxa.all():
                            if taxa in curations_as_curator_taxons:
                                is_media_curator = True
                                break
                        if not is_media_curator:
                            messages.error(request, 'Não é possível realizar ação em lotes de mídias que você não é curador')
                            return redirect('my_curations_media_list')

                    error = execute_bash_action(request, medias, user, 'my_curations_media_list')
                    if error:
                        return redirect('my_curations_media_list')
                    
                    messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
                else:
                    messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
            else:
                messages.warning(request, _('Nenhum registro foi selecionado'))
    
    query_dict = request.GET.copy()
    filtered_queryset = filter_medias(queryset, query_dict, curations)
    
    filter_form = DashboardFilterForm(query_dict, user_curations=curations)


    queryset_paginator = Paginator(filtered_queryset, records_number)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    form = BashActionsForm(view_name='my_curations_media_list')
    taxa_form = AddTaxaForm()
    location_form = AddLocationForm()

    context = {
        'records_number': records_number,
        'form': form,
        'filter_form': filter_form,
        'taxa_form': taxa_form,
        'location_form': location_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': user.curatorship_specialist.exists(),
        'is_curator': user.curatorship_curator.exists(),
        'list_page': True
    }

    return render(request, 'my_curations_media_list.html', context)


@never_cache
@curations_media_required
def my_curations_media_details(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    modified_media = ModifiedMedia.objects.filter(media=media).first()
    user_person = Person.objects.filter(user_cifonauta=request.user.id).first()
    curations = Curadoria.objects.filter(taxons__in=media.taxa.all()).distinct()
    curations_as_curator = request.user.curatorship_curator.all()
    
    is_only_media_specialist = True
    for curation in curations_as_curator:
        if curation in curations:
            is_only_media_specialist = False
            break

    is_modification_owner = False
    if modified_media and modified_media.modification_person == user_person:
        is_modification_owner = True


    if request.method == 'POST':
        action = request.POST.get('action', None)
    
        if action == 'discard':
            modified_media.delete()
            messages.success(request, "Alterações discartadas com sucesso")
            return redirect('my_curations_media_details', media_id)

        if media.status != 'published':
            messages.error(request, f'Não foi possível fazer alteração')
            return redirect('my_curations_media_details', media_id)

        if modified_media and (not is_modification_owner or modified_media.altered_by_author):
            messages.error(request, "Não é possível realizar mudanças em uma mídia com alterações pendentes.")
            return redirect('my_curations_media_details', media_id)
        
        form = EditMetadataForm(request.POST, instance=media)

        if form.is_valid():

            if is_only_media_specialist:
                if modified_media:
                    if form.has_changed():
                        form = EditMetadataForm(request.POST, instance=modified_media)

                        form.save()
                        media.save()
                    else:
                        messages.error(request, 'Mudança igual à versão publicada no site')
                        messages.warning(request, 'Descarte a alteração pendente ou efetue uma alteração válida')
                else:
                    if form.has_changed():
                        new_modified_media = ModifiedMedia(
                            media=media, 
                            modification_person=user_person, 
                            altered_by_author=False
                        )

                        form = EditMetadataForm(request.POST, instance=new_modified_media)

                        form.save()
                    else:
                        messages.error(request, 'Nenhuma alteração identificada')
                
                messages.success(request, 'Informações alteradas com sucesso')
                messages.warning(request, 'As alterações serão avaliadas e podem ou não serem aceitas')
            else:
                form.save()

                #Update taxons
                not_worms_curatory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                for taxon in form.cleaned_data['taxa']:
                    print(taxon.name)
                    print(taxon.valid_taxon)
                    if taxon.rank == '' and taxon not in not_worms_curatory.taxons.all():
                        with Taxon.objects.disable_mptt_updates():
                            update = TaxonUpdater(taxon.name)
                        Taxon.objects.rebuild()
                        if update.status == 'not_exist':
                            curadory, created = Curadoria.objects.get_or_create(name='Não está na Worms')
                            curadory.taxons.add(taxon)
                        else:
                            curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                            curadory.taxons.add(taxon)
                    if taxon.valid_taxon != None:
                        media.taxa.add(taxon.valid_taxon)
                        media.taxa.remove(taxon)
                        curadory, created = Curadoria.objects.get_or_create(name='Todos os Táxons')
                        curadory.taxons.add(taxon.valid_taxon)
                media.save()

                media.curators.add(user_person)
                messages.success(request, f'A mídia ({media.title}) foi alterada com sucesso')
            
            return redirect('my_curations_media_details', media.id)
        else:
            messages.error(request, 'Houve um erro com as alterações feitas')
    else:
        form = EditMetadataForm(instance=media)

    if modified_media:
        if not messages.get_messages(request): # if it's not right after make changes to the media
            if is_modification_owner and not modified_media.altered_by_author:
                messages.warning(request, "Esta mídia tem alterações suas. Clique no botão abaixo para ver as alterações. Se você fizer novas alterações, as anteriores serão sobrepostas")
            elif modified_media and not is_modification_owner:
                messages.warning(request, "Esta mídia tem alterações pendentes. Não é possível fazer novas mudanças até que ela seja revisada")
        
        if is_modification_owner and modified_media.altered_by_author:
            url = reverse('my_media_details', args=[media_id])
            messages.warning(request, f'Esta mídia tem alterações suas como autor. Para vê-las, <a href="{url}">Clique aqui</a>')
            
        if not is_only_media_specialist:
            url = reverse('revision_modified_media', args=[media_id])
            messages.info(request, f'Para revisar as alterações, <a href="{url}">Clique aqui</a>')

    if media.status != 'published':
        messages.warning(request, 'Esta mídia ainda não pode ser alterada por aqui, apenas depois de publicada')

    if media.state:
        form.fields['city'].queryset = City.objects.filter(state=media.state.id)
    else:
        form.fields['city'].queryset = City.objects.none()
    if media.country:
        form.fields['state'].queryset = State.objects.filter(country=media.country.id)
    else:
        form.fields['state'].queryset = State.objects.none()
    
    
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    modified_media_form = ModifiedMediaForm(instance=media)
    location_form = AddLocationForm()
    taxa_form = AddTaxaForm()

    context = {
        'form': form,
        'modified_media_form': modified_media_form,
        'location_form': location_form,
        'taxa_form': taxa_form,
        'media': media,
        'modified_media': modified_media,
        'is_only_specialist': is_only_media_specialist,
        'is_modification_owner': is_modification_owner,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'my_curations_media_details.html', context) 

@never_cache
def download_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    root, extension = os.path.splitext(media.file.name)
    filename = f'Cifonauta_{media.datatype}_{media.id}{extension}'
    return FileResponse(open(media.file.path, 'rb'), as_attachment=True, filename=filename)

@never_cache
@curator_required
def tour_list(request):
    tours = Tour.objects.filter(creator=request.user)
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'tours': tours,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
        'list_page': True
    }

    return render(request, 'tour_list.html', context)


@never_cache
@curator_required
def tour_add(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            tour_instance = form.save(commit=False)

            tour_instance.save()

            selected_media_ids = request.POST.getlist('selected_media')
            medias = Media.objects.filter(id__in=selected_media_ids)
            tour_instance.media.set(medias)

            messages.success(request, 'Tour temático criado com sucesso')
            return redirect('tour_list')
        
        messages.error(request, 'Houve um erro ao tentar criar o tour temático')

    form = TourForm(initial={'creator': request.user.id})

    form.fields['creator'].queryset = UserCifonauta.objects.filter(id=request.user.id)

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'tour_add.html', context)


@never_cache
@tour_owner_required
def tour_details(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'delete':
            tour.delete()
            messages.success(request, "Tour excluído com sucesso")
            return redirect('tour_list')

        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            tour_instance = form.save(commit=False)

            tour_instance.save()

            selected_media_ids = request.POST.getlist('selected_media')
            medias = Media.objects.filter(id__in=selected_media_ids)
            tour_instance.media.set(medias)

            messages.success(request, f'Tour ({tour.name}) editado com sucesso')
        else:
            messages.error(request, 'Houve um erro ao tentar editar o tour')
    else:
        form = TourForm(instance=tour)

    form.fields['creator'].queryset = UserCifonauta.objects.filter(id=request.user.id)

    medias_related = tour.media.all()

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'tour': tour,
        'medias_related': medias_related,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'tour_details.html', context)


@never_cache
def get_tour_medias(request):
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        input_value = request.GET.get('input_value', '')

        curatorships = Curadoria.objects.filter(Q(specialists=request.user.id) | Q(curators=request.user.id))
        taxon_ids = []
        for curatorship in curatorships:
            taxon_ids.extend(curatorship.taxons.values_list('id', flat=True))
        medias = Media.objects.filter(taxa__id__in=taxon_ids, status='published').distinct()

        query = None

        if input_value:
            query = medias.annotate(
                title_lower=Lower(F('title'))
            ).filter(
                Q(title_lower__contains=input_value.lower())
            )[offset:offset + limit]
        else:
            query = medias.all()[offset:offset + limit]

        response = {
            'medias': [
                {
                    'id': media.id, 
                    'title': media.title,
                    'datatype': media.datatype,
                    'isRelated': True if Tour.objects.filter(creator=request.user.id, media=media) else False,
                    'coverpath': media.file_cover.url,
                    'size': media.scale,
                    } for media in query
            ],
        }

        return JsonResponse(response)
    
    except Exception as e:
        print('Error: ', e)
        return JsonResponse({})


# Home
def home_page(request):
    '''Home page showing image highlights.'''

    # Photos
    try:
        highlights = Media.objects.filter(highlight=True, is_public=True).order_by('?')
        main_image = highlights.filter(datatype='photo')[0]
        photo = highlights.filter(datatype='photo')[1]
        video = highlights.filter(datatype='video')[0]
    except:
        main_image, photo, video = '', '', ''

    # Tours
    try:
        tour = Tour.objects.order_by('?')[0]
        tour_image = tour.media.exclude(id=main_image.id).exclude(
                id=photo.id).order_by('?')[0]
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

            # Filter media_list by search_query
            media_list = search_media(media_list, query)

        # Operator
        operator = query_dict.get('operator', 'and')

        # Author
        if 'author' in query_dict:
            # Extract objects from query_dict
            get_authors = query_dict.getlist('author')
            # Get instances from the query_dict IDs
            authors = Person.objects.filter(id__in=get_authors)
            # Filter media by field and operator
            media_list = filter_request(media_list, authors, 'authors', operator)
            # Fill the form with proper values
            form_authors = list(get_authors)
        else:
            form_authors = []

        # Specialist
        if 'specialist' in query_dict:
            # Extract objects from query_dict
            get_specialists = query_dict.getlist('specialist')
            # Get instances from the query_dict IDs
            specialists = Person.objects.filter(id__in=get_specialists)
            # Filter media by field and operator
            media_list = filter_request(media_list, specialists, 'specialists', operator)
            # Fill the form with proper values
            form_specialists = list(get_specialists)
        else:
            form_specialists = []

        # Tag
        if 'tag' in query_dict:
            get_tags = query_dict.getlist('tag')
            tags = Tag.objects.filter(id__in=get_tags)
            media_list = filter_request(media_list, tags, 'tags', operator)
            form_tags = list(get_tags)
        else:
            form_tags = []

        # Taxon
        if 'taxon' in query_dict:
            get_taxa = query_dict.getlist('taxon')
            taxa = Taxon.objects.filter(id__in=get_taxa)
            media_list = filter_request(media_list, taxa, 'taxa', operator)
            form_taxa = list(get_taxa)
        else:
            form_taxa = []

        # Location
        if 'location' in query_dict:
            get_locations = query_dict.getlist('location')
            locations = Location.objects.filter(id__in=get_locations)
            media_list = filter_request(media_list, locations, 'location', operator)
            form_locations = list(get_locations)
        else:
            form_locations = []

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

        # Orderby rank when query, otherwise orderby random
        if query:
            orderby = 'rank'
        else:
            orderby = query_dict.get('orderby', 'random')
            if orderby == 'rank':
                orderby = 'random'

        # Order
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
            'specialist': form_specialists,
            'tag': form_tags,
            'location': form_locations,
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
        'content_block': True,
        'content_sidebar': True,
        }
    return render(request, 'search.html', context)


def org_page(request):
    '''Página mostrando a organização dos metadados.

    Além de buscar as descrições de cada categoria, mostra exemplos aleatórios de imagens.
    '''
    # TODO: Replace sizes tags by a Scale model
    # Tamanhos
    # sizes = Category.objects.get(name_en='Size')
    # Técnicas
    technique = Category.objects.get(name_en='Imaging technique')
    microscopy = Category.objects.get(name_en='Microscopy')
    # Estágios
    stage = Category.objects.get(name_en='Life stage')
    stages = stage.tags.all()
    # Modos
    mode = Category.objects.get(name_en='Life mode')
    # Habitat
    habitat = Category.objects.get(name_en='Habitat')
    # Diversos
    assorted = Category.objects.get(name_en='Miscellaneous')
    context = {
        # 'sizes': sizes,
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
    '''Individual page for media file with all the information.'''

    # Get object.
    media = get_object_or_404(Media.objects.select_related('location', 'city', 'state', 'country'), id=media_id)

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

    tags = media.tags.all()
    authors = media.authors.all()
    specialists = media.specialists.all()
    curators = media.curators.all()
    taxa = media.taxa.all()
    references = media.references.all()
    filename, file_extension = os.path.splitext(str(media.file_cover))

    context = {
        'media': media,
        'form': form,
        'admin_form': admin_form,
        'related': related,
        'tags': tags,
        'authors': authors,
        'taxa': taxa,
        'specialists': specialists,
        'curators': curators,
        'references': references,
        'file_extension': file_extension
        }

    if is_ajax(request):
        return render(request, 'media_page_ajax.html', context)
    else:
        return render(request, 'media_page.html', context)


def tour_page(request, slug):
    '''Tour page.'''
    tour = get_object_or_404(Tour, slug=slug)
    # TODO: Think better how references will be managed.
    references = tour.references.all()
    entries = tour.media.select_related('location', 'city', 'state', 'country')

    # Get first thumbnail.
    try:
        thumb = entries.values_list('file_cover', flat=True)[0]
    except:
        thumb = ''

    # Extract media metadata.
    authors, specialists, taxa, locations, cities, states, countries, tags = extract_set(entries)

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
    '''Taxonomic groups organized in a tree and species list.'''
    species = Taxon.objects.filter(rank_pt_br='Espécie').exclude(media__isnull=True).annotate(count=Count('media')).order_by('-count')[:20]
    context = {'species': species}
    return render(request, 'taxa_page.html', context)


def places_page(request):
    '''Página mostrando locais de maneira organizada.'''
    locations = Location.objects.exclude(media__isnull=True)
    cities = City.objects.exclude(media__isnull=True)
    states = State.objects.exclude(media__isnull=True)
    countries = Country.objects.exclude(media__isnull=True)

    context = {
        'locations': locations,
        'cities': cities,
        'states': states,
        'countries': countries,
        }
    return render(request, 'places_page.html', context)


def tags_page(request):
    '''Página mostrando tags organizados por categoria.'''
    cats = Category.objects.prefetch_related('tags')
    context = {
        'cats': cats,
        }
    return render(request, 'tags_page.html', context)


def authors_page(request):
    '''Page showing the full list of authors and specialists.'''

    # Get all person instances associated to media as authors
    authors = Person.objects.exclude(media_as_author__isnull=True)

    # Get person instances associated to media as specialists
    specialists = Person.objects.exclude(media_as_specialist__isnull=True)

    # Get person instances associated to media as curators
    curators = Person.objects.exclude(media_as_curator__isnull=True)

    context = {
        'authors': authors,
        'specialists': specialists,
	'curators': curators,
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


def extract_set(media_list):
    '''Extract other metadata from media list.

    Returns invididual querysets for each model.
    '''

    authors = Person.objects.filter(id__in=media_list.values_list('authors', flat=True))
    specialists = Person.objects.filter(id__in=media_list.values_list('specialists', flat=True))
    tags = Tag.objects.filter(id__in=media_list.values_list('tags', flat=True))
    taxa = Taxon.objects.filter(id__in=media_list.values_list('taxa', flat=True))
    locations = Location.objects.filter(id__in=media_list.values_list('location', flat=True))
    cities = City.objects.filter(id__in=media_list.values_list('city', flat=True))
    states = State.objects.filter(id__in=media_list.values_list('state', flat=True))
    countries = Country.objects.filter(id__in=media_list.values_list('country', flat=True))

    return authors, specialists, taxa, locations, cities, states, countries, tags


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

    # List for storing queries
    queries = []

    # Loop over objects
    for obj in objects:
        # If taxon, also get queries for descendants
        if field == 'taxa':
            # Store taxon queries separately (include current obj)
            taxa = [Q(**{field: obj})]
            children = obj.get_descendants()
            for child in children:
                taxa.append(Q(**{field: child}))
            # Reduce taxa queries to single Q with OR operator
            taxa_query = reduce(or_, taxa)
            # Append to main queries
            queries.append(taxa_query)
        else:
            queries.append(Q(**{field: obj}))

    # If OR, reduce queries to single Q with OR operator
    if operator == 'or':
        queries = [reduce(or_, queries)]

    # Loop over queries to filter media list
    for query in queries:
        media_list = media_list.filter(query)
    
    # Only keep unique media entries
    media_list = media_list.distinct()

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


def is_ajax(request):
    '''Handler function after deprecation of HttpRequest.is_ajax.'''
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

