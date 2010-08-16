from django import forms

    
class SearchForm(forms.Form):
    query = forms.CharField(
            label=u'Buscar por',
            widget=forms.TextInput(attrs={'size': 32}),
            help_text=u'(digite um ou mais termos)',
            )
