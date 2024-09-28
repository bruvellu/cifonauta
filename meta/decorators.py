from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from .models import Media, Person, Tour
from django.db.models import Q

def authentication_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        login_url = reverse('Login')
        return redirect(f'{login_url}?next={request.path}')

    return _wrapped_view


def author_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_author:
            return view_func(request, *args, **kwargs)
        
        return redirect('home')

    return _wrapped_view


def specialist_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        is_specialist = user.curatorship_specialist.exists()
        if is_specialist:
            return view_func(request, *args, **kwargs)
        
        return redirect('dashboard')

    return _wrapped_view

    
def loaded_media_required(view_func):
    @wraps(view_func)
    @authentication_required
    @author_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        medias = Media.objects.filter(user=user, status='loaded')

        if medias:
            return view_func(request, *args, **kwargs)
        
        return redirect('upload_media_step1')

    return _wrapped_view

    
def media_specialist_required(view_func):
    @wraps(view_func)
    @authentication_required
    @specialist_required
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('media_id')

        user = request.user
        curations = user.curatorship_specialist.all()
        curations_taxa = set()

        for curation in curations:
            taxa = curation.taxa.all()
            curations_taxa.update(taxa)

        queryset_ids = Media.objects.filter(status='draft').filter(taxa__in=curations_taxa).values_list('id', flat=True)

        if media_id in queryset_ids:
            return view_func(request, *args, **kwargs)
        
        return redirect('editing_media_list')

    return _wrapped_view


def curator_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        is_curator = user.curatorship_curator.exists()
        if is_curator:
            return view_func(request, *args, **kwargs)
        
        return redirect('dashboard')

    return _wrapped_view


def media_curator_required(view_func):
    @wraps(view_func)
    @authentication_required
    @curator_required
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('media_id')

        user = request.user
        curations = user.curatorship_curator.all()
        curations_taxa = set()

        for curation in curations:
            taxa = curation.taxa.all()
            curations_taxa.update(taxa)

        queryset_ids = Media.objects.filter(
            Q(status='submitted') & Q(taxa__in=curations_taxa) |
            Q(modified_media__taxa__in=curations_taxa)
        ).values_list('id', flat=True)
        
        if media_id in queryset_ids:
            return view_func(request, *args, **kwargs)
        
        return redirect('revision_media_list')

    return _wrapped_view


def media_owner_required(view_func):
    @wraps(view_func)
    @authentication_required
    @author_required
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('pk')

        media = Media.objects.get(pk=media_id)

        if request.user == media.user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('my_media_list')

    return _wrapped_view

    
def tour_owner_required(view_func):
    @wraps(view_func)
    @authentication_required
    @curator_required
    def _wrapped_view(request, *args, **kwargs):
        tour_id = kwargs.get('pk')

        tour = Tour.objects.get(pk=tour_id)

        if tour.creator == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('tour_list')

    return _wrapped_view


def specialist_or_curator_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        is_curator = user.curatorship_curator.exists()
        is_specialist = user.curatorship_specialist.exists()

        if is_specialist or is_curator:
            return view_func(request, *args, **kwargs)
        
        return redirect('dashboard')

    return _wrapped_view


def curations_media_required(view_func):
    @wraps(view_func)
    @authentication_required
    @specialist_or_curator_required
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('media_id')
        user = request.user

        curations_as_specialist = user.curatorship_specialist.all()
        curations_as_specialist_taxa = set()
        for curation in curations_as_specialist:
            curations_as_specialist_taxa.update(curation.taxa.all())

        curations_as_curator = user.curatorship_curator.all()
        curations_as_curator_taxa = set()
        for curation in curations_as_curator:
            curations_as_curator_taxa.update(curation.taxa.all())

        curations = curations_as_specialist | curations_as_curator
        curations = curations.distinct()

        curations_taxa = set()
        for curation in curations:
            curations_taxa.update(curation.taxa.all())

        curator_queryset_ids = Media.objects.filter(Q(taxa__in=curations_as_curator_taxa)).values_list('id', flat=True)

        specialist_queryset_ids = Media.objects.filter(Q(taxa__in=curations_as_specialist_taxa)) .values_list('id', flat=True)   

        queryset_ids = (curator_queryset_ids | specialist_queryset_ids).exclude(status='loaded').distinct()
        
        if media_id in queryset_ids:
            return view_func(request, *args, **kwargs)
        
        return redirect('my_curations_media_list')

    return _wrapped_view
