# -*- coding: utf-8 -*-

from django import forms
from meta.models import *
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class SearchForm(forms.Form):
    query = forms.CharField(
            label=_('Buscar por'),
            widget=forms.TextInput(attrs={'size': 32}),
            help_text=_('(digite um ou mais termos)'),
            )

METAS = (
        (u'author', u'Autor'),
        (u'taxon', u'Táxon'),
        (u'size', u'Tamanho'),
        (u'sublocation', u'Local'),
        (u'city', u'Cidade'),
        (u'state', u'Estado'),
        (u'country', u'País'),
        )

class RelatedForm(forms.Form):
    type = forms.ChoiceField(choices=METAS, label=_('Navegando por'))
    # TODO Incluir um checkbox para mostrar apenas highlights?

ITEMS = (
        (16, 16),
        (40, 40),
        (80, 80),
        (120, 120),
        (220, 220),
        (460, 460),
        (900, 900),
        )

ORDER = (
        ('asc', _('ascendente')),
        ('desc', _('descendente')),
        )

ORDER_BY = (
        ('id', _('id')),
        ('view_count', _('visitas')),
        ('date', _('data da imagem')),
        ('pub_date', _('data de publicação')),
        ('timestamp', _('data de modificação')),
        ('random', _('aleatório')),
        )

class DisplayForm(forms.Form):
    '''Formulário para alterar parâmetros dos resultados de buscas.

    Pode ser alterado por qual metadado as imagens serão ordenadas, se esta ordem será ascendente ou descendente, o número de resultados por página e se é para mostrar apenas os destaques.
    '''
    n = forms.ChoiceField(choices=ITEMS, label=_('Ítens por página'))
    orderby = forms.ChoiceField(choices=ORDER_BY, label=_('Ordenar por'))
    order = forms.ChoiceField(choices=ORDER, label=_('Ordem'))
    highlight = forms.BooleanField(required=False, initial=False, label=_('Somente destaques'))

class FixTaxaForm(forms.Form):
    '''Formulário que mostra os táxons órfãos.
    
    Seleciona táxons que não tem pai, cujo ranking não é Reino, ou táxons sem 
    ranking.
    '''
    def get_orphans():
        '''Pega táxons sem parent e sem ranking.

        Faz o processamento para serem carregadas no formulário.
        '''
        # TODO Ver se esse rank=Reino direto não compromete o funcionamento.
        taxa = Taxon.objects.filter(Q(parent__isnull=True) & ~Q(rank='Reino') | 
                Q(rank=''))
        semitaxa = [(taxon.name, u'%s (id=%s)' % (taxon.name, taxon.id)) for 
                taxon in taxa]
        orphans = tuple(semitaxa)
        return orphans

    review = forms.MultipleChoiceField(choices=get_orphans(), 
            widget=forms.CheckboxSelectMultiple(attrs={'class':'check-taxon'}), 
            required=False, label=_('Revisar táxons'))

