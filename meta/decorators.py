from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from .models import Curadoria, Media
from django.shortcuts import get_object_or_404

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


def media_owner_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('pk')

        media = Media.objects.get(pk=media_id)

        if media.author == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('my_media_list')

    return _wrapped_view

    
def tour_owner_required(view_func):
    @wraps(view_func)
    @authentication_required
    def _wrapped_view(request, *args, **kwargs):
        tour_id = kwargs.get('pk')

        tour = Tour.objects.get(pk=tour_id)

        if tour.creator == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('tour_list')

    return _wrapped_view