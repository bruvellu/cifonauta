# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from meta.models import Taxon


class Command(BaseCommand):
    help = 'Translate rank names in batch.'

    def handle(self, *args, **options):

        # Get all taxa.
        taxa = Taxon.objects.all()

        for taxon in taxa:
            self.stdout.write('%s id=%d' % (taxon.name, taxon.id))
            if taxon.rank_pt_br and taxon.rank_en:
                continue
            elif taxon.rank_pt_br and not taxon.rank_en:
                taxon.rank_en = translate_pt2en(taxon.rank_pt_br)
                taxon.save()
                self.stdout.write('Translated %s -> %s!' % (taxon.rank_pt_br, taxon.rank_en))
            elif not taxon.rank_pt_br and taxon.rank_en:
                taxon.rank_pt_br = translate_en2pt(taxon.rank_en)
                taxon.save()
                self.stdout.write('Translated %s -> %s!' % (taxon.rank_en, taxon.rank_pt_br))
            else:
                continue

        self.stdout.write('Finished translation.')


def translate_en2pt(rank):
    '''Translate rank to portuguese.'''

    en2pt = {
            u'Subform': u'Subforma',
            u'Superorder': u'Superordem',
            u'Variety': u'Variedade',
            u'Infraorder': u'Infraordem',
            u'Section': u'Seção',
            u'Subclass': u'Subclasse',
            u'Subsection': u'Subseção',
            u'Kingdom': u'Reino',
            u'Infrakingdom': u'Infrareino',
            u'Division': u'Divisão',
            u'Subtribe': u'Subtribo',
            u'Aberration': u'Aberração',
            u'InfraOrder': u'Infraordem',
            u'Subkingdom': u'Subreino',
            u'Infraclass': u'Infraclasse',
            u'Subfamily': u'Subfamília',
            u'Class': u'Classe',
            u'Superfamily': u'Superfamília',
            u'Subdivision': u'Subdivisão',
            u'Morph': u'Morfotipo',
            u'Race': u'Raça',
            u'Unspecified': u'Não especificado',
            u'Suborder': u'Subordem',
            u'Genus': u'Gênero',
            u'Order': u'Ordem',
            u'Subvariety': u'Subvariedade',
            u'Tribe': u'Tribo',
            u'Subgenus': u'Subgênero',
            u'Form': u'Forma',
            u'Family': u'Família',
            u'Subphylum': u'Subfilo',
            u'Stirp': u'Estirpe',
            u'Phylum': u'Filo',
            u'Superclass': u'Superclasse',
            u'Subspecies': u'Subespécie',
            u'Species': u'Espécie',
            }

    try:
        rank_pt = en2pt[rank]
        return rank_pt
    except:
        rank_pt = translate_pt2en(rank)
        return rank_pt


def translate_pt2en(rank):
    '''Translate rank to english.'''

    pt2en = {
            u'Subforma': u'Subform',
            u'Superordem': u'Superorder',
            u'Variedade': u'Variety',
            u'Infraordem': u'Infraorder',
            u'Seção': u'Section',
            u'Subclasse': u'Subclass',
            u'Subseção': u'Subsection',
            u'Reino': u'Kingdom',
            u'Infrareino': u'Infrakingdom',
            u'Divisão': u'Division',
            u'Subtribo': u'Subtribe',
            u'Aberração': u'Aberration',
            u'Infraordem': u'InfraOrder',
            u'Subreino': u'Subkingdom',
            u'Infraclasse': u'Infraclass',
            u'Subfamília': u'Subfamily',
            u'Classe': u'Class',
            u'Superfamília': u'Superfamily',
            u'Subdivisão': u'Subdivision',
            u'Morfotipo': u'Morph',
            u'Raça': u'Race',
            u'Não especificado': u'Unspecified',
            u'Subordem': u'Suborder',
            u'Gênero': u'Genus',
            u'Ordem': u'Order',
            u'Subvariedade': u'Subvariety',
            u'Tribo': u'Tribe',
            u'Subgênero': u'Subgenus',
            u'Forma': u'Form',
            u'Família': u'Family',
            u'Subfilo': u'Subphylum',
            u'Estirpe': u'Stirp',
            u'Filo': u'Phylum',
            u'Superclasse': u'Superclass',
            u'Subespécie': u'Subspecies',
            u'Espécie': u'Species',
            }

    try:
        rank_en = pt2en[rank]
        return rank_en
    except:
        rank_en = translate_en2pt(rank)
        return rank_en

