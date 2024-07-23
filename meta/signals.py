# -*- coding: utf-8 -*-

import os
from django.db.models.signals import pre_save, post_save, m2m_changed, pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import translation
from meta.models import Media, Person, Tag, Category, Taxon, Location, City, State, Country, Reference, Tour, Curadoria


@receiver(pre_save, sender=Person)
@receiver(pre_save, sender=Tag)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=Taxon)
@receiver(pre_save, sender=Location)
@receiver(pre_save, sender=City)
@receiver(pre_save, sender=State)
@receiver(pre_save, sender=Country)
@receiver(pre_save, sender=Reference)
@receiver(pre_save, sender=Tour)
def slugify_name(sender, instance, *args, **kwargs):
    '''Create slug using the name field of several models.'''
    if not instance.slug:
        # Force slug in Portuguese, for now
        translation.activate('pt_br')
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Media)
def normalize_title_and_caption(sender, instance, *args, **kwargs):
    '''Normalize title and caption fields from Media before saving.'''
    instance.title_pt_br = instance.normalize_title(instance.title_pt_br)
    instance.title_en = instance.normalize_title(instance.title_en)
    instance.caption_pt_br = instance.normalize_caption(instance.caption_pt_br)
    instance.caption_en = instance.normalize_caption(instance.caption_en)

@receiver(post_save, sender=Media)
def update_search_vector(sender, instance, created, *args, **kwargs):
    '''Update search_vector field with current metadata after saving.'''
    sender.objects.filter(id=instance.id).update(search_vector=instance.update_search_vector())

# Delete file from folder when the media is deleted on website
@receiver(pre_delete, sender=Media)
def delete_files_from_folder(sender, instance, **kwargs):
    # List of files to be deleted
    to_delete = [instance.file,
                 instance.file_large,
                 instance.file_medium,
                 instance.file_small,
                 instance.file_cover]
    # Loop over and delete, if file exists
    for file in to_delete:
        if file:
            try:
                os.remove(file.path)
            except FileNotFoundError:
                print('{file} not found. Probably already deleted.')


@receiver(m2m_changed, sender=Curadoria.taxons.through)
def get_taxons_descendants(sender, instance, action, model, pk_set, **kwargs):
    m2m_changed.disconnect(get_taxons_descendants, sender=Curadoria.taxons.through)
    
    taxon = Taxon.objects.filter(id__in=pk_set)
    descendants = taxon.get_descendants()

    if action == "pre_add":
        instance.taxons.add(*descendants)
    elif action == "pre_remove":
        instance.taxons.remove(*descendants)

    m2m_changed.connect(get_taxons_descendants, sender=Curadoria.taxons.through)




# Não é signal, apenas função acessória.
# FIXME Trocar de lugar, eventualmente.
def citation_html(reference):
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
            if 'identifiers' in reference:
                if 'doi' in reference['identifiers']:
                    citation += u', doi:<a href="http://dx.doi.org/%s">%s</a>' % (reference['identifiers']['doi'], reference['identifiers']['doi'])
        # Verifica se pmid existe e inclui na citação.
        elif key == 'pmid':
            if 'identifiers' in reference:
                if 'pmid' in reference['identifiers']:
                    citation += u', pmid:<a href="http://www.ncbi.nlm.nih.gov/pubmed/%s">%s</a>' % (reference['identifiers']['pmid'], reference['identifiers']['pmid'])
        elif key in reference:
            # Ano.
            if key == 'year':
                citation += u'<strong>%s</strong> ' % reference['year']
            # Autores.
            elif key == 'authors':
                authors = []
                for author in reference['authors']:
                    forenames = author['forename'].split()
                    initials = [name[:1] for name in forenames]
                    initials = ''.join(initials)
                    final = u'%s %s' % (author['surname'], initials)
                    authors.append(final)
                authors = ', '.join(authors)
                citation += u'%s.' % authors
            # Título.
            elif key == 'title':
                citation += u' <em>%s</em>.' % reference['title']
            # Revista.
            elif key == 'publication_outlet':
                citation += u' %s' % reference['publication_outlet']
            elif key == 'volume':
                citation += u', %s' % reference['volume']
            elif key == 'issue':
                citation += u'(%s)' % reference['issue']
            elif key == 'pages':
                citation += u': %s' % reference['pages']
            elif key == 'url':
                # Lidar com múltiplos urls por citação.
                first_url = reference['url'].split('\n')[0]
                citation += u', url:<a href="%s">%s</a>' % (first_url,
                        first_url)
    return citation


# FIXME: No longer functional.
# @receiver(pre_save, sender=Reference)
def create_citation(sender, instance, *args, **kwargs):
    '''Cria citação em HTML a partir da bibkey.

    Usa o ID da entrada (= Mendeley ID) para pegar os dados da referência via
    Mendeley API.
    Manda o objeto para função que gera o html com a citação da referência.
    Salva a citação no banco.

    Notar que múltiplos urls são separados por um \n

    Nome de autor agora é dicionário com 'forename' e 'surname'

    EXEMPLO DE REFERÊNCIA DO MENDELEY API:
    {
        "title":"Embryonic, larval, and juvenile development of the sea biscuit Clypeaster subdepressus (Echinodermata: Clypeasteroida).",
        "type":"Journal Article",
        "volume":"5",
        "issue":"3",
        "url":"http:\/\/www.ncbi.nlm.nih.gov\/pubmed\/20339592\nhttp:\/\/www.ncbi.nlm.nih.gov\/pubmed\/20339592",
        "pages":"e9654",
        "year":"2010",
        "abstract":"Sea biscuits and sand dollars diverged from other irregular echinoids approximately 55 million years ago and rapidly dispersed to oceans worldwide.",
        "authors":[
            {"forename": "Bruno Cossermelli", "surname": "Vellutini"},
            {"forename": "Alvaro Esteves", "surname": "Migotto"}
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
    reference_id = instance.name
    reference = mendeley.document_details(reference_id)
    citation = citation_html(reference)
    instance.citation = citation




def makestats(signal, instance, sender, **kwargs):
    '''Cria objeto stats se não existir.'''
    if not instance.stats:
        from meta.models import Stats
        newstats = Stats()
        newstats.save()
        instance.stats = newstats


def set_position(signal, instance, sender, **kwargs):
    '''Create object with tour position.'''
    from meta.models import TourPosition
    media = instance.media.all()
    for item in media:
        try:
            query = TourPosition.objects.get(media=item, tour=instance)
        except:
            tp = TourPosition(media=item, tour=instance)
            tp.save()
