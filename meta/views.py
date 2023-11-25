# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.db.models.functions import Lower
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.aggregates import StringAgg
from functools import reduce
from media_utils import Metadata
from operator import or_, and_
from PIL import Image

from .models import *
from .forms import *

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from .decorators import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from user.models import UserCifonauta
from cifonauta.settings import MEDIA_EXTENSIONS, FILENAME_REGEX
from django.core.files import File
from django.utils.translation import get_language, get_language_info
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache

from dotenv import load_dotenv
load_dotenv()


@never_cache
def dashboard(request):
    is_specialist = Curadoria.objects.filter(Q(specialists=request.user)).exists()
    is_curator = Curadoria.objects.filter(Q(curators=request.user)).exists()

    context = {
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'dashboard.html', context)


@never_cache
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
                

                # Create empty Media instance for new UUID
                media = Media()
                # Rename file name with UUID and lowercase extension
                file.name = f'{media.uuid}{extension}'

                # Define file field of Media instance
                media.file = file
                # Define user field of Media instance
                media.user = request.user

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
def upload_media_step2(request):
    medias = Media.objects.filter(user=request.user, status='loaded')
    user_person = Person.objects.get(user_cifonauta=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel':
            medias.delete()
            messages.success(request, 'Upload de mídias cancelado com sucesso')
            return redirect('upload_media_step1')
        elif action == 'coauthor':
            form = CoauthorRegistrationForm(request.POST)
            if form.is_valid():
                coauthor_instance = form.save(commit=False)

                split_name = coauthor_instance.name.lower().split(' ')

                preps = ('de', 'da', 'do', 'das', 'dos', 'e')
                name = [name.capitalize() if name not in preps else name for name in split_name]
                name = ' '.join(name)
                coauthor_instance.name = name
                
                form.save()
                messages.success(request, f'Coautor {name} adicionado com sucesso')
                return redirect('upload_media_step2')
            else:
                messages.error(request, 'Houve um erro ao tentar salvar coautor')
                return redirect('upload_media_step2')
        
        form = UploadMediaForm(request.POST, request.FILES)
        
        if form.is_valid():
            if form.cleaned_data['terms'] == False:
                    messages.error(request, 'Você precisa aceitar os termos')
                    return redirect('upload_media_step2')
            
            if user_person not in form.cleaned_data['authors']:
                    messages.error(request, f'O usuário logado ({user_person.name}) deve ser incluído como autor')
                    return redirect('upload_media_step2')
                
            if form.cleaned_data['country'].id == 1 and not (form.cleaned_data['state'] and form.cleaned_data['city']):
                messages.error(request, 'Você precisa selecionar um estado e uma cidade')
                return redirect('upload_media_step2')
            
            for media in medias:
                file = media.file.name.split('/')[-1]
                ext = file.split('.')[-1]
                filename = file.split('.')[0]

                media_file = File(media.file, name=f'{filename}.{ext}')
                media.sitepath = media_file
                media_file = File(media.file, name=f'{filename}_cover.{ext}')
                media.coverpath = media_file

                media.title = form.cleaned_data['title']
                media.caption = form.cleaned_data['caption']
                media.taxa.set(form.cleaned_data['taxa'])
                media.authors.set(form.cleaned_data['authors'])
                media.date_created = form.cleaned_data['date_created']
                media.country = form.cleaned_data['country']
                media.state = form.cleaned_data['state']
                media.city = form.cleaned_data['city']
                media.location = form.cleaned_data['location']
                media.geolocation = form.cleaned_data['geolocation']
                media.license = form.cleaned_data['license']
                media.terms = form.cleaned_data['terms']

                media.status = 'draft'
                media.save()

                if not media.is_video():
                    coverpath = Image.open(media.coverpath.path)
                    coverpath.thumbnail((1280, 720))
                    coverpath.save(media.coverpath.path, quality=40)

                    sitepath = Image.open(media.sitepath.path)
                    sitepath.thumbnail((1280, 720))
                    sitepath.save(media.sitepath.path)
            
            messages.success(request, 'Suas mídias foram salvas com sucesso')
            return redirect('upload_media_step1')

        messages.error(request, 'Erro ao tentar salvar mídias')
        return redirect('upload_media_step2')
    
    # metadata = None
    # for media in medias:
    #     if media.media.url.endswith('jpg'):
    #         metadata = Metadata(media.media.path)
    #         try:
    #             read_metadata = metadata.read_metadata()
    #         except:
    #             metadata = None
    #         finally:
    #             break        
    
    # if metadata:
    #     co_authors = []
    #     co_authors_meta = read_metadata['source'].split(',')
    #     for co_author in co_authors_meta:
    #         if co_author.strip() != '':
    #             try:
    #                 co_authors.append(Person.objects.filter(name=co_author.strip()).get().id)
    #             except:
    #                 messages.error(request, f'O Co-Autor {co_author.strip()} não está cadastrado.')
    #     try:
    #         location = Location.objects.filter(name=read_metadata['sublocation']).get().id
    #     except:
    #         location = ''
    #     form = UploadMediaForm(initial={
    #         'author': request.user.id,
    #         'title': read_metadata['headline'],
    #         'caption': read_metadata['description_pt'],
    #         'date': read_metadata['datetime'],
    #         'geolocation': read_metadata['gps'],
    #         'location': location,
    #         'license': read_metadata['source'],
    #         'co_author': co_authors,
    #         'geolocation': read_metadata['gps']
    #     })
    # else:
    form = UploadMediaForm(initial={'authors': user_person.id})

    form.fields['state'].queryset = State.objects.none()
    form.fields['city'].queryset = City.objects.none()

    registration_form = CoauthorRegistrationForm()
    
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'registration_form': registration_form,
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
def edit_metadata(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    if request.method == 'POST':
        form = EditMetadataForm(request.POST, instance=media)
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
    if form.is_valid():
        media_instance = form.save(commit=False)
        try:
            user = str(form.cleaned_data['user'])
            authors = str(form.cleaned_data['authors']).split(';')
            metadata =  {
            'software': str(form.cleaned_data['software']),
            'headline': str(form.cleaned_data['title']),
            'instructions': str(form.cleaned_data['size']),
            'license': {
                'license_type': str(form.cleaned_data['license']),
                'user': user,
                'authors': authors,
                },
            'keywords': {
                'Estágio de vida': str(form.cleaned_data['life_stage']),
                'Habitat': str(form.cleaned_data['habitat']),
                'Microscopia': str(form.cleaned_data['microscopy']),
                'Modo de vida': str(form.cleaned_data['life_style']),
                'Técnica fotográfica': str(form.cleaned_data['photographic_technique']),
                'Diversos': str(form.cleaned_data['several'])
            },
            'source': str(form.cleaned_data['specialist']),
            'credit': str(form.cleaned_data['credit']),
            'description_pt': str(form.cleaned_data['caption']),
            'description_en': '',
            'gps': str(form.cleaned_data['geolocation']),
            'datetime': str(form.cleaned_data['date_created']),
            'title_pt': str(form.cleaned_data['title']),
            'title_en': '',
            'country': str(form.cleaned_data['country']),
            'state': str(form.cleaned_data['state']),
            'city': str(form.cleaned_data['city']),
            'sublocation': str(form.cleaned_data['location'])
                }
            meta = Metadata(file=f'./site_media/{str(media.file)}')
            meta.edit_metadata(metadata)
        except:
            pass
        media_instance.status = 'submitted'
        media_instance.taxa.set(form.cleaned_data['taxa'])
        media_instance.authors.set(form.cleaned_data['authors'])

        person = Person.objects.filter(user_cifonauta=request.user.id).first()
        media_instance.specialists.add(person)

        media_instance.save()

        form.send_mail(request.user, [media], 'Edição de mídia do Cifonauta', 'edited_media_email.html')

        messages.success(request, 'Edição de mídia realizado com sucesso')

        return redirect('curadory_medias')

    media = get_object_or_404(Media, pk=media_id)
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'media': media,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'update_media.html', context) 


@never_cache
def curadoria_media_list(request):
    user = request.user
    curations = user.curatorship_specialist.all()
    curations_taxons = []

    for curadoria in curations:
        taxons = curadoria.taxons.all()
        curations_taxons.extend(taxons)

    queryset = Media.objects.filter(status='draft')
    queryset = queryset.filter(taxa__in=curations_taxons)
    
    # Apply distinct() to eliminate duplicates
    queryset = queryset.distinct()

    filtered_queryset = queryset
    filter_form = DashboardFilterForm()

    if request.method == "POST":
        media_ids = request.POST.getlist('selected_media_ids')

        if media_ids:
            form = SpecialistActionForm(request.POST)

            if form.is_valid():
                medias = Media.objects.filter(id__in=media_ids)
                
                if form.cleaned_data['taxa_action'] != 'maintain':
                    for media in medias:
                        media.taxa.set(form.cleaned_data['taxa'])
                if form.cleaned_data['status_action'] != 'maintain':
                    medias.update(status='submitted')

                person = Person.objects.filter(user_cifonauta=request.user.id).first()
                
                user_medias = {}
                for media in medias:
                    media.specialists.add(person)
                    user_id = media.user.id

                    if user_id not in user_medias:
                        user_medias[user_id] = [media]
                    else:
                        user_medias[user_id].append(media)
                
                for medias in user_medias.values():
                    form.send_mail(request.user, medias, 'Edição de mídia do Cifonauta', 'edited_media_email.html')
                


                messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
            else:
                messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
        else:
            messages.warning(request, _('Nenhum registro foi selecionado'))
    elif request.method == "GET":
        search = request.GET.get('search')
        if search:
            filtered_queryset = filtered_queryset.filter(title__icontains=search)
        

        curation_ids = request.GET.getlist('curations')
        if curation_ids:
            filtered_curations = curations.filter(id__in=curation_ids).distinct()

            taxons = set()
            for curation in filtered_curations:
                taxons.update(curation.taxons.all())

            filtered_queryset = filtered_queryset.filter(taxa__in=taxons)
        

        alphabetical_order = request.GET.get('alphabetical_order')
        if alphabetical_order:
            filtered_queryset = filtered_queryset.order_by('title')
        
        filter_form = DashboardFilterForm({
            'search': search,
            'curations': curation_ids,
            'alphabetical_order': alphabetical_order,
        })

    queryset_paginator = Paginator(filtered_queryset, 12)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    form = SpecialistActionForm()
    # Options are: mantain status or send to revision
    form.fields['status_action'].choices = (form.fields['status_action'].choices[0], form.fields['status_action'].choices[1])

    context = {
        'form': form,
        'filter_form': filter_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': user.curatorship_specialist.exists(),
        'is_curator': user.curatorship_curator.exists(),
    }

    return render(request, 'curadoria_media_list.html', context)
    

@never_cache
def update_my_medias(request, pk):
    media = get_object_or_404(Media, pk=pk)
    modified_media = ModifiedMedia.objects.filter(media=media).first()

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'discard':
            modified_media.delete()
            messages.success(request, "Alterações discartadas com sucesso")
            return redirect('update_media', media.pk)

        form = UpdateMyMediaForm(request.POST)
        if form.is_valid():
            if media.status == 'published':
                if modified_media:
                    altered_fields = []
                    for field in form.fields.keys():
                        if not hasattr(modified_media, field):
                            continue

                        if field == "authors" or field == "taxa":
                            model_m2m_value = list(getattr(modified_media, field).all())
                            form_m2m_value = list(form.cleaned_data[field])

                            if model_m2m_value != form_m2m_value or form_m2m_value != list(getattr(media, field).all()):
                                altered_fields.append(field)
                        else:
                            model_field_value = getattr(modified_media, field)
                            form_field_value = form.cleaned_data[field]

                            if model_field_value != form_field_value or form_field_value != getattr(media, field):
                                altered_fields.append(field)

                    fields_equal_to_original = 0

                    for field in altered_fields:
                        if field == "authors" or field == "taxa":
                            form_m2m_value = list(form.cleaned_data[field])

                            if list(getattr(media, field).all()) == form_m2m_value:
                                fields_equal_to_original += 1
                        else:
                            form_field_value = form.cleaned_data[field]

                            if getattr(media, field) == form_field_value:
                                fields_equal_to_original += 1
                    
                    if len(altered_fields) == fields_equal_to_original:
                        messages.error(request, 'Mudança igual à versão publicada no site')
                        messages.warning(request, 'Descarte a alteração pendente ou efetue uma alteração válida')
                        return redirect('update_media', media.pk)

                    modified_media.title = form.cleaned_data['title']
                    modified_media.caption = form.cleaned_data['caption']
                    modified_media.authors.set(form.cleaned_data['authors'])
                    modified_media.taxa.set(form.cleaned_data['taxa'])
                    modified_media.date = form.cleaned_data['date_created']
                    modified_media.location = form.cleaned_data['location']
                    modified_media.city = form.cleaned_data['city']
                    modified_media.state = form.cleaned_data['state']
                    modified_media.country = form.cleaned_data['country']
                    modified_media.geolocation = form.cleaned_data['geolocation']
                    modified_media.license = form.cleaned_data['license']

                    modified_media.save()
                else:
                    has_difference = False
                    for field in form.fields.keys():
                        if field != "taxa" and field != "authors":
                            media_value = getattr(media, field)

                            if media_value != form.cleaned_data[field]:
                                has_difference = True
                                break
                        else:
                            media_m2m_value = None

                            media_m2m_value = list(getattr(media, field).all())
                            form_m2m_value = list(form.cleaned_data[field])

                            if media_m2m_value != form_m2m_value:
                                has_difference = True
                                break

                    if not has_difference:
                        messages.error(request, 'Nenhuma alteração identificada')
                        return redirect('update_media', media.pk)

                    new_modified_media = ModifiedMedia(media=media)
                    new_modified_media.title = form.cleaned_data['title']
                    new_modified_media.caption = form.cleaned_data['caption']
                    new_modified_media.date = form.cleaned_data['date_created']
                    new_modified_media.location = form.cleaned_data['location']
                    new_modified_media.city = form.cleaned_data['city']
                    new_modified_media.state = form.cleaned_data['state']
                    new_modified_media.country = form.cleaned_data['country']
                    new_modified_media.geolocation = form.cleaned_data['geolocation']
                    new_modified_media.user = form.cleaned_data['user']
                    new_modified_media.license = form.cleaned_data['license']

                    new_modified_media.save()

                    new_modified_media.authors.set(form.cleaned_data['authors'])
                    new_modified_media.taxa.set(form.cleaned_data['taxa'])
                
                messages.success(request, 'Informações alteradas com sucesso')
                messages.warning(request, 'As alterações serão avaliadas e podem ou não serem aceitas')
            else:
                if media.status == "submitted":
                    media.status = "draft"

                media.title = form.cleaned_data['title']
                media.caption = form.cleaned_data['caption']
                media.authors.set(form.cleaned_data['authors'])
                media.taxa.set(form.cleaned_data['taxa'])
                media.date_created = form.cleaned_data['date_created']
                media.location = form.cleaned_data['location']
                media.city = form.cleaned_data['city']
                media.state = form.cleaned_data['state']
                media.country = form.cleaned_data['country']
                media.geolocation = form.cleaned_data['geolocation']
                media.license = form.cleaned_data['license']

                media.save()

                messages.success(request, 'Informações alteradas com sucesso')
            
            return redirect('my_medias')

        messages.error(request, 'Houve um erro com as alterações feitas')
        return redirect('update_media', media.pk)

    if modified_media and not messages.get_messages(request):
        messages.warning(request, "Esta mídia tem alterações pendentes")

    form = UpdateMyMediaForm(instance=media)
    if media.state:
        form.fields['city'].queryset = City.objects.filter(state=media.state.id)
    else:
        form.fields['city'].queryset = City.objects.none()
    if media.country:
        form.fields['state'].queryset = State.objects.filter(country=media.country.id)
    else:
        form.fields['state'].queryset = State.objects.none()
    form.fields['user'].queryset = UserCifonauta.objects.filter(id=request.user.id)
    if media.status == 'published':
        license_choices = [choice[0] for choice in Media.LICENSE_CHOICES]
        license_index = license_choices.index(media.license)
        form.fields['license'].choices = Media.LICENSE_CHOICES[:license_index + 1]

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    modified_media_form = ModifiedMediaForm(instance=media)

    field_names = modified_media_form.fields.keys()
    modified_media_fields = []
    for field_name in field_names:
        modified_media_fields.append(modified_media_form[field_name])

    context = {
        'media': media,
        'modified_media': modified_media,
        'modified_media_fields': modified_media_fields,
        'form': form,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'update_media.html', context)
    

@never_cache
def my_medias(request):
    user = request.user
    queryset = Media.objects.filter(user=user).exclude(status='loaded').order_by('-pk')

    filtered_queryset = queryset
    filter_form = DashboardFilterForm()

    if request.method == "POST":
        media_ids = request.POST.getlist('selected_media_ids')

        if media_ids:
            form = MyMediasActionForm(request.POST)

            if form.is_valid():
                has_published_media = Media.objects.filter(id__in=media_ids, status='published').exists()
                if has_published_media:
                    messages.error(request, _('Não é possível aplicar ações em mídias já publicadas'))
                    return redirect('my_medias')
                
                medias = Media.objects.filter(id__in=media_ids)
                
                if form.cleaned_data['taxa_action'] != 'maintain':
                    for media in medias:
                        media.taxa.set(form.cleaned_data['taxa'])
                medias.update(status='draft')
                
                messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
            else:
                messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
        else:
            messages.warning(request, _('Nenhum registro foi selecionado'))
    elif request.method == "GET":
        search = request.GET.get('search')
        if search:
            filtered_queryset = filtered_queryset.filter(title__icontains=search)
        

        curation_ids = request.GET.getlist('curations')
        if curation_ids:
            filtered_curations = Curadoria.objects.filter(id__in=curation_ids)

            taxons = set()
            for curation in filtered_curations:
                taxons.update(curation.taxons.all())

            filtered_queryset = filtered_queryset.filter(taxa__in=taxons).distinct()
        

        alphabetical_order = request.GET.get('alphabetical_order')
        if alphabetical_order:
            filtered_queryset = filtered_queryset.order_by('title')
        
        filter_form = DashboardFilterForm({
            'search': search,
            'curations': curation_ids,
            'alphabetical_order': alphabetical_order,
        })

    user = request.user
    queryset = Media.objects.filter(user=user).exclude(status='loaded').order_by('-pk')
    
    form = MyMediasActionForm()

    is_specialist = user.curatorship_specialist.exists()
    is_curator = user.curatorship_curator.exists()

    queryset_paginator = Paginator(filtered_queryset, 12)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    context = {
        'form': form,
        'filter_form': filter_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'my_medias.html', context)


def manage_users(request):
    users = UserCifonauta.objects.all().exclude(id=request.user.id)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'enable-authors':
            user_ids = request.POST.getlist('selected_authors')
            if len(user_ids) == 0:
                messages.error(request, 'Nenhum usuário selecionado para realizar ação')
                return redirect('manage_users')
            author_action = request.POST.get('author_action')
            users_action = UserCifonauta.objects.filter(id__in=user_ids)

            if author_action == 'turn_author':
                users_action.update(is_author=True)
            elif author_action == 'disable_author':
                for user in users_action:
                    if user.uploaded_media.all():
                        messages.error(request, f'O usuário "{user.first_name} {user.last_name}" possui mídia relacionada')
                        return redirect('manage_users')
                    
                users_action.update(is_author=False)
            else:
                messages.warning(request, "Nenhuma ação selecionada")
                return redirect('manage_users')
            messages.success(request, "Os autores foram atualizados com sucesso")
        else:
            specialist_ids = request.POST.getlist('specialist_ids')
            curatorship_id = request.POST.get('curatorship_id')

            specialists = UserCifonauta.objects.filter(id__in=specialist_ids)
            curatorship = Curadoria.objects.filter(id=curatorship_id).first()
            curatorship.specialists.set(specialists)

            messages.success(request, "Os especialistas foram atualizados com sucesso")
            
    curatorships = Curadoria.objects.filter(curators=request.user.id)

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'users': users,
        'curatorships': curatorships,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }
    return render(request, 'manage_users.html', context)        
    

def get_users(request):
    curatorships = Curadoria.objects.filter(curators=request.user.id)
    users = UserCifonauta.objects.filter(is_author=True).exclude(id=request.user.id)

    response = {
        'users': [
            {
                'name': f'{user.first_name} {user.last_name}',
                'id': user.id,
                'curatorship_ids': [str(curatorship.id) for curatorship in curatorships.filter(Q(specialists=user.id))]
            } for user in users
        ]
    }

    return JsonResponse(response)


def manage_users(request):
    users = UserCifonauta.objects.all().exclude(id=request.user.id)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'enable-authors':
            user_ids = request.POST.getlist('selected_authors')
            if len(user_ids) == 0:
                messages.error(request, 'Nenhum usuário selecionado para realizar ação')
                return redirect('manage_users')
            author_action = request.POST.get('author_action')
            users_action = UserCifonauta.objects.filter(id__in=user_ids)

            if author_action == 'turn_author':
                users_action.update(is_author=True)
            elif author_action == 'disable_author':
                for user in users_action:
                    if user.uploaded_media.all():
                        messages.error(request, f'O usuário "{user.first_name} {user.last_name}" possui mídia relacionada')
                        return redirect('manage_users')
                    
                users_action.update(is_author=False)
            else:
                messages.warning(request, "Nenhuma ação selecionada")
                return redirect('manage_users')
            messages.success(request, "Os autores foram atualizados com sucesso")
        else:
            specialist_ids = request.POST.getlist('specialist_ids')
            curatorship_id = request.POST.get('curatorship_id')

            specialists = UserCifonauta.objects.filter(id__in=specialist_ids)
            curatorship = Curadoria.objects.filter(id=curatorship_id).first()
            curatorship.specialists.set(specialists)

            messages.success(request, "Os especialistas foram atualizados com sucesso")
            
    curatorships = Curadoria.objects.filter(curators=request.user.id)

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'users': users,
        'curatorships': curatorships,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }
    return render(request, 'manage_users.html', context)        
    

def get_users(request):
    curatorships = Curadoria.objects.filter(curators=request.user.id)
    users = UserCifonauta.objects.filter(is_author=True).exclude(id=request.user.id)

    response = {
        'users': [
            {
                'name': user.first_name + user.last_name,
                'id': user.id,
                'curatorship_ids': [str(curatorship.id) for curatorship in curatorships.filter(Q(specialists=user.id))]
            } for user in users
        ]
    }
    
    return JsonResponse(response)


@never_cache
def revision_media(request):
    user = request.user

    curations = user.curatorship_curator.all()
    curations_taxons = []

    for curadoria in curations:
        taxons = curadoria.taxons.all()
        curations_taxons.extend(taxons)

    queryset = Media.objects.filter(
        Q(status='submitted') & Q(taxa__in=curations_taxons) |
        Q(modified_media__taxa__in=curations_taxons))

    queryset = queryset.distinct()

    filtered_queryset = queryset
    filter_form = DashboardFilterForm()

    if request.method == 'POST':
        media_ids = request.POST.getlist('selected_media_ids')

        if media_ids:
            form = SpecialistActionForm(request.POST)

            if form.is_valid():
                medias = Media.objects.filter(id__in=media_ids)
                
                if form.cleaned_data['taxa_action'] != 'maintain':
                    for media in medias:
                        media.taxa.set(form.cleaned_data['taxa'])
                if form.cleaned_data['status_action'] != 'maintain':
                    medias.update(status='published', date_published=timezone.now(), is_public=True) #TODO: Remove is_public
                
                person = Person.objects.filter(user_cifonauta=request.user.id).first()

                user_medias = {}
                for media in medias:
                    media.curators.add(person)

                    user_id = media.user.id

                    if user_id not in user_medias:
                        user_medias[user_id] = [media]
                    else:
                        user_medias[user_id].append(media)
                
                for medias in user_medias.values():
                    form.send_mail(request.user, medias, 'Revisão de mídia do Cifonauta', 'published_media_email.html')

                messages.success(request, _('As ações em lote foram aplicadas com sucesso'))
            else:
                messages.error(request, _('Houve um erro ao tentar aplicar as ações em lote'))
        else:
            messages.warning(request, _('Nenhum registro foi selecionado'))
    elif request.method == "GET":
        search = request.GET.get('search')
        if search:
            filtered_queryset = filtered_queryset.filter(title__icontains=search)
        

        curation_ids = request.GET.getlist('curations')
        if curation_ids:
            filtered_curations = curations.filter(id__in=curation_ids)

            taxons = set()
            for curation in filtered_curations:
                taxons.update(curation.taxons.all())

            filtered_queryset = filtered_queryset.filter(taxa__in=taxons).distinct()
        

        alphabetical_order = request.GET.get('alphabetical_order')
        if alphabetical_order:
            filtered_queryset = filtered_queryset.order_by('title')
        
        filter_form = DashboardFilterForm({
            'search': search,
            'curations': curation_ids,
            'alphabetical_order': alphabetical_order,
        })
    

    queryset_paginator = Paginator(filtered_queryset, 12)
    page_num = request.GET.get('page')
    page = queryset_paginator.get_page(page_num)

    form = SpecialistActionForm()
    # Options are: mantain status or publish media
    form.fields['status_action'].choices = (form.fields['status_action'].choices[0], form.fields['status_action'].choices[2])

    context = {
        'form': form,
        'filter_form': filter_form,
        'object_exists': queryset.exists(),
        'entries': page,
        'is_specialist': user.curatorship_specialist.exists(),
        'is_curator': user.curatorship_curator.exists(),
    }

    return render(request, 'media_revision.html', context)


@never_cache
def modified_media_revision(request, pk):
    media = get_object_or_404(Media, pk=pk)
    modified_media = ModifiedMedia.objects.filter(media=media).first()

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'discard':
            modified_media.delete()
            messages.success(request, 'Alteração descartada com sucesso')
            return redirect('media_revision')

        media.title = modified_media.title
        media.caption = modified_media.caption
        media.date_created = modified_media.date
        media.location = modified_media.location
        media.city = modified_media.city
        media.state = modified_media.state
        media.country = modified_media.country
        media.geolocation = modified_media.geolocation
        media.license = modified_media.license
        
        media.save()

        media.taxa.set(modified_media.taxa.all())
        media.authors.set(modified_media.authors.all())

        modified_media.delete()

        messages.success(request, 'Alterações aceitas com sucesso')
        return redirect('media_revision')

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    form = ModifiedMediaForm()

    field_names = form.fields.keys()
    fields = []
    for field_name in field_names:
        fields.append({
            'name': field_name,
            'label': form[field_name].label,
            'required': form[field_name].field.required
        })
    
    context = {
        'fields': fields,
        'media': media,
        'modified_media': modified_media,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'modified_media_revision.html', context)


@never_cache
def revision_media_detail(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    if request.method == 'POST':
        form = EditMetadataForm(request.POST, instance=media)
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
    if form.is_valid():
        media_instance = form.save(commit=False)
        try:
            author = str(form.cleaned_data['author'])
            co_authors = str(form.cleaned_data['co_author']).split(';')
            metadata =  {
            'software': str(form.cleaned_data['software']),
            'headline': str(form.cleaned_data['title']),
            'instructions': str(form.cleaned_data['size']),
            'license': {
                'license_type': str(form.cleaned_data['license']),
                'author': author,
                'co_authors': co_authors,
                },
            'keywords': {
                'Estágio de vida': str(form.cleaned_data['life_stage']),
                'Habitat': str(form.cleaned_data['habitat']),
                'Microscopia': str(form.cleaned_data['microscopy']),
                'Modo de vida': str(form.cleaned_data['life_style']),
                'Técnica fotográfica': str(form.cleaned_data['photographic_technique']),
                'Diversos': str(form.cleaned_data['several'])
            },
            'source': str(form.cleaned_data['specialist']),
            'credit': str(form.cleaned_data['credit']),
            'description_pt': str(form.cleaned_data['caption']),
            'description_en': '',
            'gps': str(form.cleaned_data['geolocation']),
            'datetime': str(form.cleaned_data['date_created']),
            'title_pt': str(form.cleaned_data['title']),
            'title_en': '',
            'country': str(form.cleaned_data['country']),
            'state': str(form.cleaned_data['state']),
            'city': str(form.cleaned_data['city']),
            'sublocation': str(form.cleaned_data['location'])
                }
            if not media.is_video:
                Metadata(file=f'./site_media/{str(media.file)}', metadata=metadata)
        except:
            pass
        media_instance.status = 'published'
        media_instance.is_public = True
        media_instance.taxa.set(form.cleaned_data['taxa'])
        media_instance.authors.set(form.cleaned_data['authors'])

        person = Person.objects.filter(user_cifonauta=request.user.id).first()
        media_instance.curators.add(person)
        
        media_instance.save()

        form.send_mail(request.user, [media], 'Revisão de mídia do Cifonauta', 'published_media_email.html')

        messages.success(request, f'A mídia {media.title} foi publicada com sucesso')
        return redirect('media_revision')
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'media': media,
        'is_specialist': is_specialist,
        'is_curator': is_curator,
    }

    return render(request, 'media_revision_detail.html', context) 


@never_cache
def dashboard_tour_list(request):
    tours = Tour.objects.filter(creator=request.user)
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'tours': tours,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'dashboard_tour_list.html', context)


@never_cache
def dashboard_tour_add(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            tour_instance = form.save(commit=False)

            tour_instance.save()

            selected_media_ids = request.POST.getlist('selected_media')
            medias = Media.objects.filter(id__in=selected_media_ids)
            tour_instance.media.set(medias)

            messages.success(request, 'Tour temático criado com sucesso')
            return redirect('dashboard_tour_list')
        
        messages.error(request, 'Houve um erro ao tentar criar o tour temático')

    form = TourForm(initial={'creator': request.user.id})

    curatorships = Curadoria.objects.filter(Q(specialists=request.user.id) | Q(curators=request.user.id))
    taxon_ids = []
    for curatorship in curatorships:
        taxon_ids.extend(curatorship.taxons.values_list('id', flat=True))
    medias = Media.objects.filter(taxa__id__in=taxon_ids, status='published').distinct()
    
    form.fields['creator'].queryset = UserCifonauta.objects.filter(id=request.user.id)

    initial_medias = [*medias][:20]
    
    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'initial_medias': initial_medias,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'dashboard_tour_add.html', context)


@never_cache
def dashboard_tour_edit(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'delete':
            tour.delete()
            messages.success(request, "Tour excluído com sucesso")
            return redirect('dashboard_tour_list')

        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            tour_instance = form.save(commit=False)

            tour_instance.save()

            selected_media_ids = request.POST.getlist('selected_media')
            medias = Media.objects.filter(id__in=selected_media_ids)
            tour_instance.media.set(medias)

            messages.success(request, f'Tour {tour.name} editado com sucesso')
        else:
            messages.error(request, 'Houve um erro ao tentar editar o tour')

    form = TourForm(instance=tour)

    curatorships = Curadoria.objects.filter(Q(specialists=request.user.id) | Q(curators=request.user.id))
    taxon_ids = []
    for curatorship in curatorships:
        taxon_ids.extend(curatorship.taxons.values_list('id', flat=True))
    medias = Media.objects.filter(taxa__id__in=taxon_ids, status='published').distinct()
    
    form.fields['creator'].queryset = UserCifonauta.objects.filter(id=request.user.id)

    medias_related = tour.media.all()

    initial_medias = [*medias][:20]

    is_specialist = request.user.curatorship_specialist.exists()
    is_curator = request.user.curatorship_curator.exists()

    context = {
        'form': form,
        'tour': tour,
        'initial_medias': initial_medias,
        'medias_related': medias_related,
        'is_specialist': is_specialist,
        'is_curator': is_curator
    }

    return render(request, 'dashboard_tour_edit.html', context)


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
                    'coverpath': media.coverpath.url,
                    'size': media.size,
                    } for media in query
            ],
        }

        return JsonResponse(response)
    
    except:
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

            # Get language.
            language = get_language()

            # Change search config based on language
            if language == 'en':
                langconfig = 'english'
                # search_vectors = SearchVector('title_en', weight='A', config=langconfig) + \
                                 # SearchVector('caption_en', weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('taxon__name', delimiter=' '), weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('person__name', delimiter=' '), weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('tag__name_en', delimiter=' '), weight='C', config=langconfig) + \
                                 # SearchVector('location__name', weight='D', config=langconfig) + \
                                 # SearchVector('city__name', weight='D', config=langconfig) + \
                                 # SearchVector('state__name', weight='D', config=langconfig) + \
                                 # SearchVector('country__name', weight='D', config=langconfig)
            elif language == 'pt-br':
                langconfig = 'portuguese_unaccent'
                # search_vectors = SearchVector('title_pt_br', weight='A', config=langconfig) + \
                                 # SearchVector('caption_pt_br', weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('taxon__name', delimiter=' '), weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('person__name', delimiter=' '), weight='B', config=langconfig) + \
                                 # SearchVector(StringAgg('tag__name_pt_br', delimiter=' '), weight='C', config=langconfig) + \
                                 # SearchVector('location__name', weight='D', config=langconfig) + \
                                 # SearchVector('city__name', weight='D', config=langconfig) + \
                                 # SearchVector('state__name', weight='D', config=langconfig) + \
                                 # SearchVector('country__name', weight='D', config=langconfig)

            # Create SearchQuery
            search_query = SearchQuery(query, config=langconfig)

            # Create SearchRank
            search_rank = SearchRank(F('search_vector'), search_query)

            # Filter media_list by search_query
            media_list = media_list.annotate(rank=search_rank).filter(search_vector=search_query)

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
    # Tamanhos
    sizes = Category.objects.get(name_en='Size')
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
    size = media.get_size()
    authors = media.authors.all()
    specialists = media.specialists.all()
    taxa = media.taxa.all()
    references = media.references.all()
    filename, file_extension = os.path.splitext(str(media.coverpath))

    context = {
        'media': media,
        'form': form,
        'admin_form': admin_form,
        'related': related,
        'tags': tags,
        'size': size,
        'authors': authors,
        'taxa': taxa,
        'specialists': specialists,
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
        thumb = entries.values_list('coverpath', flat=True)[0]
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
    locations = Location.objects.order_by('name')
    cities = City.objects.order_by('name')
    states = State.objects.order_by('name')
    countries = Country.objects.order_by('name')
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
    authors = Person.objects.filter(media_as_author__isnull=False).distinct()

    # Get person instances associated to media as specialists who are not authors
    specialists = Person.objects.filter(media_as_specialist__isnull=False).filter(media_as_author__isnull=True).distinct()

    context = {
        'authors': authors,
        'specialists': specialists,
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

