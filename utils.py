# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import translation 


class AdminLocaleURLMiddleware:
    '''Força interface da admin em português.'''
    def process_request(self, request):
        if request.path.startswith('/admin'):
            request.LANG = getattr(settings, 'ADMIN_LANGUAGE_CODE', settings.LANGUAGE_CODE)
            translation.activate(request.LANG)
            request.LANGUAGE_CODE = request.LANG
