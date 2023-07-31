from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('Login')  
            return redirect(f'{login_url}?next={request.path}')
        
        # Original view
        return view_func(request, *args, **kwargs)

    return _wrapped_view