# -*- coding: utf-8 -*-

from django.db.models import signals
from django.template.defaultfilters import slugify

from external.mendeley import mendeley

# Não é signal, apenas função acessória.
def citation_html(ref):
    '''Retorna citação formatada em HTML.

    Citação é gerada através do objeto que o Mendeley API retorna com os 
    campos.
    '''
    citation = u''
    keys = ['year', 'authors', 'title', 'publication_outlet', 'volume',
            'issue', 'pages', 'doi', 'pmid', 'url']
    # Padroniza None para keys que não existem.
    for key in keys:
        # Verifica se doi existe e inclui na citação.
        if key == 'doi':
            if 'identifiers' in ref:
                if 'doi' in ref['identifiers']:
                    citation += u', doi:<a href="http://dx.doi.org/%s">%s</a>' % (ref['identifiers']['doi'], ref['identifiers']['doi'])
        # Verifica se pmid existe e inclui na citação.
        elif key == 'pmid':
            if 'identifiers' in ref:
                if 'pmid' in ref['identifiers']:
                    citation += u', pmid:<a href="http://www.ncbi.nlm.nih.gov/pubmed/%s">%s</a>' % (ref['identifiers']['pmid'], ref['identifiers']['pmid'])
        elif key in ref:
            # Ano.
            if key == 'year':
                citation += u'<strong>%s</strong> ' % ref['year']
            # Autores.
            elif key == 'authors':
                authors = []
                for author in ref['authors']:
                    names = author.split()
                    last = names.pop()
                    initials = [name[:1] for name in names]
                    initials = ''.join(initials)
                    final = u'%s %s' % (last, initials)
                    authors.append(final)
                authors = ', '.join(authors)
                citation += u'%s.' % authors
            # Título.
            elif key == 'title':
                citation += u' %s.' % ref['title']
            # Revista.
            elif key == 'publication_outlet':
                citation += u' %s' % ref['publication_outlet']
            elif key == 'volume':
                citation += u', %s' % ref['volume']
            elif key == 'issue':
                citation += u'(%s)' % ref['issue']
            elif key == 'pages':
                citation += u': %s' % ref['pages']
            elif key == 'url':
                citation += u'<br><a href="%s">%s</a>' % (ref['url'], ref['url'])
    return citation

def citation_pre_save(signal, instance, sender, **kwargs):
    '''Cria citação em HTML a partir da bibkey.

    Usa o ID da entrada (= Mendeley ID) para pegar os dados da referência via 
    Mendeley API.
    Manda o objeto para função que gera o html com a citação da referência.
    Salva a citação no banco.

    EXEMPLO DE REFERÊNCIA DO MENDELEY API:
    {
        "title":"Embryonic, larval, and juvenile development of the sea biscuit Clypeaster subdepressus (Echinodermata: Clypeasteroida).",
        "type":"Journal Article",
        "volume":"5",
        "issue":"3",
        "url":"http:\/\/www.ncbi.nlm.nih.gov\/pubmed\/20339592",
        "pages":"e9654",
        "year":"2010",
        "abstract":"Sea biscuits and sand dollars diverged from other irregular echinoids approximately 55 million years ago and rapidly dispersed to oceans worldwide.",
        "authors":[
            "Bruno Cossermelli Vellutini",
            "Alvaro Esteves Migotto"
            ],
        "editors":[],
        "tags":["phd"],
        "keywords":[],
        "publication_outlet":"PloS one",
        "identifiers":{
            "doi":"10.1371\/journal.pone.0009654",
            "issn":"1932-6203",
            "pmid":"20339592"
            },
        "discipline":{
            "discipline":"Biological Sciences",
            "subdiscipline":"Embryology"}
            }
    '''
    ref_id = instance.name
    ref = mendeley.document_details(ref_id)
    citation = citation_html(ref)
    instance.citation = citation

def slug_pre_save(signal, instance, sender, **kwargs):
    '''Cria slug antes de salvar.'''
    if not instance.slug:
        slug = slugify(instance.name)
        instance.slug = slug

def update_count(signal, instance, sender, **kwargs):
    '''Atualiza o contador de fotos e vídeos.'''
    #TODO Incluir os outros modelos!
    ## Many 2 Many
    # Authors
    authors = instance.author_set.all()
    if authors:
        for author in authors:
            author.counter()
    # Sources
    sources = instance.source_set.all()
    if sources:
        for source in sources:
            source.counter()
    # Taxa
    taxa = instance.taxon_set.all()
    if taxa:
        for taxon in taxa:
            taxon.counter()
    # Tags
    tags = instance.tag_set.all()
    if tags:
        for tag in tags:
            tag.counter()
    # References
    references = instance.reference_set.all()
    if references:
        for reference in references:
            reference.counter()
    # Tours
    tours = instance.tour_set.all()
    if tours:
        for tour in tours:
            tour.counter()

    ## Foreign Key
    # Size
    if instance.size:
        instance.size.counter()
    # Sublocation
    if instance.sublocation:
        instance.sublocation.counter()
    # City
    if instance.city:
        instance.city.counter()
    # State
    if instance.state:
        instance.state.counter()
    # Country
    if instance.country:
        instance.country.counter()
