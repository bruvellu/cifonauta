# -*- coding: utf-8 -*-

from django import forms

    
class SearchForm(forms.Form):
    query = forms.CharField(
            label=u'Buscar por',
            widget=forms.TextInput(attrs={'size': 32}),
            help_text=u'(digite um ou mais termos)',
            )

METAS = (
        (u'author', u'Autor'),
        (u'taxon', u'Táxon'),
        (u'genus', u'Gênero'),
        (u'species', u'Espécie'),
        (u'size', u'Tamanho'),
        (u'sublocation', u'Local'),
        (u'city', u'Cidade'),
        (u'state', u'Estado'),
        (u'country', u'País'),
        )

class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label='Navegando por')
    #TODO Incluir um checkbox para mostrar apenas highlights?
