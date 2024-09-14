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
    instance.acknowledgments_pt_br = instance.normalize_caption(instance.acknowledgments_pt_br)
    instance.acknowledgments_en = instance.normalize_caption(instance.acknowledgments_en)

@receiver(pre_save, sender=Taxon)
def synchronize_taxa_media(sender, instance, *args, **kwargs):
    '''Synchronize media between valid/invalid taxa.'''

    # Add valid media to invalid taxon
    if instance.is_valid and instance.synonyms.all():
        for invalid in instance.synonyms.all():
            invalid.media.add(*instance.media.all())
            print(f'Media from {instance} (is_valid={instance.is_valid}) to {invalid} (is_valid={invalid.is_valid})')

    # Add invalid media to valid taxon
    elif not instance.is_valid and instance.valid_taxon:
        instance.valid_taxon.media.add(*instance.media.all())
        print(f'Media from {instance} (is_valid={instance.is_valid}) to {instance.valid_taxon} (is_valid={instance.valid_taxon.is_valid})')


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

#TODO: Create a proper trigger for adding descendants to curation

#TODO: This is being triggered when a curation is added to a taxon and it causes an error because the sender is a Taxon instance
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
