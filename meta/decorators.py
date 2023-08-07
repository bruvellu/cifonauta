from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from .models import Curadoria, Media
from django.shortcuts import get_object_or_404

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('Login')  
            return redirect(f'{login_url}?next={request.path}')
        
        # Original view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def custom_author_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if user.is_author:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home') 

    return _wrapped_view


def custom_specialist_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        is_specialist = Curadoria.objects.filter(specialists=user).exists()

        if is_specialist:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home') 

    return _wrapped_view


def custom_curator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        is_curator = Curadoria.objects.filter(curators=user).exists()

        if is_curator:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home') 

    return _wrapped_view


def media_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        media_id = kwargs.get('pk')

        media = Media.objects.get(pk=media_id)

        if media.author == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return _wrapped_view