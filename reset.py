#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *

zero, new = Taxon.objects.get_or_create(name=u'')
zero, new = Genus.objects.get_or_create(name=u'')
zero, new = Species.objects.get_or_create(name=u'')
zero, new = Source.objects.get_or_create(name=u'')
zero, new = Size.objects.get_or_create(name=u'')
zero, new = Rights.objects.get_or_create(name=u'')
zero, new = Sublocation.objects.get_or_create(name=u'')
zero, new = City.objects.get_or_create(name=u'')
zero, new = State.objects.get_or_create(name=u'')
zero, new = Country.objects.get_or_create(name=u'')

tags = [
	{'name': u'juvenil', 'description': u'Organismo que ainda não atingiu a capacidade reprodutiva, embora seja morfologicamente semelhante a um adulto.', 'parent': u'Estágio de vida'},
	{'name': u'macrofotografia', 'description': u'Detalhe tirado com câmera convencional; muitas vezes de organismos em aquários.', 'parent': u'Técnica'},
	{'name': u'paisagem', 'description': u'Mostra um ambiente.', 'parent': u'Técnica'},
	{'name': u'adulto', 'description': u'Organismo com capacidade reprodutiva plena.', 'parent': u'Estágio de vida'},
	{'name': u'demersal', 'description': u'Que vive próximo ao fundo do mar, embora possua capacidade de natação ativa.', 'parent': u'Pelágicos'},
	{'name': u'mev', 'description': u'Microscopia eletrônica de varredura.', 'parent': u'Microscopia'},
	{'name': u'3d', 'description': u'Imagens processadas digitalmente para mostrar a tridimensionalidade.', 'parent': u'Microscopia'},
	{'name': u'dic', 'description': u'Contraste de interferência diferencial (ou Nomarski).', 'parent': u'Microscopia'},
	{'name': u'luz polarizada', 'description': u'', 'parent': u'Microscopia'},
	{'name': u'campo claro', 'description': u'', 'parent': u'Microscopia'},
	{'name': u'campo escuro', 'description': u'', 'parent': u'Microscopia'},
	{'name': u'confocal', 'description': u'', 'parent': u'Microscopia'},
	{'name': u'avifauna', 'description': u'', 'parent': u'Diversos'},
	{'name': u'bentônico', 'description': u'Organismos que vivem no leito dos oceanos e mares, fixos ou não a um substrato.', 'parent': u'Bentônicos'},
	{'name': u'gameta', 'description': u'Célula reprodutiva madura (espermatozóide ou óvulo).', 'parent': u'Estágio de vida'},
	{'name': u'embrião', 'description': u'Organismo em desenvolvimento, antes de deixar o ovo ou o útero materno.', 'parent': u'Estágio de vida'},
	{'name': u'larva', 'description': u'Estágio pós-embrionário, distinto do estado adulto quanto a forma, modo de vida, comportamento ou hábitos alimentares. Não se reproduz sexuadamente.', 'parent': u'Estágio de vida'},
	{'name': u'planctônico', 'description': u'Que vive disperso na coluna d’água, com muito pouca ou nenhuma capacidade de locomoção.', 'parent': u'Pelágicos'},
	{'name': u'nectônico', 'description': u'Que vive disperso na coluna d’água, mas com capacidade de natação.', 'parent': u'Pelágicos'},
	{'name': u'simbiose', 'description': u'', 'parent': u'Diversos'},
	{'name': u'neustônico', 'description': u'Que vive muito próximo da superfície da água', 'parent': u'Pelágicos'},
	{'name': u'pleustônico', 'description': u'Que flutua na superfície da água, como algumas plantas e a caravela-portuguesa.', 'parent': u'Pelágicos'},
	{'name': u'infauna', 'description': u'Que vive dentro de sedimento inconsolidado.', 'parent': u'Bentônicos'},
	{'name': u'epifauna', 'description': u'Que vive na superfície do substrato.', 'parent': u'Bentônicos'},
	{'name': u'intersticial', 'description': u'Que vive entre os interstícios dos grãos de sedimento.', 'parent': u'Bentônicos'},
	{'name': u'epibionte', 'description': u'Que vive na superfície de outro.', 'parent': u'Bentônicos'},
	{'name': u'macrofauna', 'description': u'Animal cuja menor dimensão é maior ou igual a 0,5 mm.', 'parent': u'Bentônicos'},
	{'name': u'meiofauna', 'description': u'Animal cuja menor dimensão é menor que 0,5 mm e maior que  0,1 mm.', 'parent': u'Bentônicos'},
	{'name': u'microfauna', 'description': u'Animal menor que 0,1 mm.', 'parent': u'Bentônicos'},
	{'name': u'praia', 'description': u'Faixa de terra coberta de lama, areia ou seixos, às margens de um corpo de água.', 'parent': u'Habitat'},
	{'name': u'costão rochoso', 'description': u'Ambiente de transição entre os meios marinho e terrestre, formado por rochas.', 'parent': u'Habitat'},
	{'name': u'manguezal', 'description': u'Ecossistema costeiro de transição entre os ambientes terrestre e marinho, dominado por espécies vegetais típicas, geralmente associado a locais onde há encontro de águas de rios e do mar.', 'parent': u'Habitat'},
	{'name': u'estuário', 'description': u'Desembocadura ou foz de um rio.', 'parent': u'Habitat'},
	{'name': u'infralitoral', 'description': u'Região costeira permanentemente submersa.', 'parent': u'Habitat'},
	{'name': u'espécie introduzida', 'description': u'Espécie que foi acidental ou deliberadamente transportada para fora de sua área normal de distribuição.', 'parent': u'Diversos'},
	{'name': u'espécie invasora', 'description': u'Espécie cujo estabelecimento e dispersão ameaçam a diversidade biológica da região em que foi introduzida.', 'parent': u'Diversos'},
	{'name': u'cebimar-usp', 'description': u'Instalações do CEBIMar USP.', 'parent': u'Diversos'},
	{'name': u'lecitotrófica', 'description': u'Larva que se desenvolve apenas com reservas internas de vitelo.', 'parent': u'Diversos'},
	{'name': u'planctotrófica', 'description': u'Larva que captura seu alimento.', 'parent': u'Diversos'},
	{'name': u'submersa', 'description': u'Tirado embaixo d’água com caixa-estanque.', 'parent': u'Técnica'},
	{'name': u'espécie ameaçada', 'description': u'', 'parent': u'Diversos'},
]
tagcats = [
	{'name': u'Técnica', 'description': u'', 'parent': None},
	{'name': u'Bentônicos', 'description': u'Organismos que vivem no leito dos oceanos e mares, fixos ou não a um substrato.', 'parent': u'Modo de vida'},
	{'name': u'Pelágicos', 'description': u'Organismos que vivem na coluna d’água.', 'parent': u'Modo de vida'},
	{'name': u'Microscopia', 'description': u'', 'parent': u'Técnica'},
	{'name': u'Diversos', 'description': u'Marcadores que não se encaixam nas outras categorias. Podem ser termos comuns frequentemente procurados.', 'parent': None},
	{'name': u'Habitat', 'description': u'Também indicamos os habitats de cada organismo, quando possível.', 'parent': None},
	{'name': u'Modo de vida', 'description': u'Cada estágio de vida de um organismo pode ter um modo de vida diferente. Por isso, essa classificação refere-se ao modo de vida da fase ilustrada na imagem. Sempre que possível, as imagens foram classificadas nas categorias abaixo:', 'parent': None},
	{'name': u'Estágio de vida', 'description': u'Nem sempre os organismos fotografados são indivíduos adultos.', 'parent': None},
]
taxa = [
	{'name': u'Aves', 'common': u'', 'parent': u'Vertebrata'},
	{'name': u'Pycnogonida', 'common': u'', 'parent': u'Arthropoda'},
	{'name': u'Kinorhyncha', 'common': u'', 'parent': u'Metazoa'},
	{'name': u'Annelida', 'common': u'Anelídeos', 'parent': u'Metazoa'},
	{'name': u'Arthropoda', 'common': u'Artrópodes', 'parent': u'Metazoa'},
	{'name': u'Echinodermata', 'common': u'Equinodermos', 'parent': u'Metazoa'},
	{'name': u'Nematoda', 'common': u'', 'parent': u'Metazoa'},
	{'name': u'Placozoa', 'common': u'', 'parent': u'Metazoa'},
	{'name': u'Vertebrata', 'common': u'Vertebrados', 'parent': u'Metazoa'},
	{'name': u'Rotifera', 'common': u'Rotíferos', 'parent': u'Arthropoda'},
	{'name': u'Oligochaeta', 'common': u'Oligoquetos', 'parent': u'Annelida'},
	{'name': u'Hirudinea', 'common': u'Hirudíneos', 'parent': u'Annelida'},
	{'name': u'Asteroidea', 'common': u'Asteróides', 'parent': u'Echinodermata'},
	{'name': u'Porifera', 'common': u'Poríferos', 'parent': u'Metazoa'},
	{'name': u'Holothuroidea', 'common': u'Holoturóides', 'parent': u'Echinodermata'},
	{'name': u'Echiura', 'common': u'Equiúros', 'parent': u'Metazoa'},
	{'name': u'Mollusca', 'common': u'Moluscos', 'parent': u'Metazoa'},
	{'name': u'Sipuncula', 'common': u'Sipuncúlidos', 'parent': u'Metazoa'},
	{'name': u'Entoprocta', 'common': u'', 'parent': u'Metazoa'},
	{'name': u'Nemertea', 'common': u'', 'parent': u'Metazoa'},
	{'name': u'Platyhelminthes', 'common': u'Platelmintos', 'parent': u'Metazoa'},
	{'name': u'Metazoa', 'common': u'Metazoários', 'parent': None},
	{'name': u'Chaetognatha', 'common': u'Quetognatos', 'parent': u'Metazoa'},
	{'name': u'Hemichordata', 'common': u'Hemicordados', 'parent': u'Metazoa'},
	{'name': u'Acari', 'common': u'Ácaros', 'parent': u'Arthropoda'},
	{'name': u'Polychaeta', 'common': u'Poliquetos', 'parent': u'Annelida'},
	{'name': u'Bivalvia', 'common': u'Bivalves', 'parent': u'Mollusca'},
	{'name': u'Phoronida', 'common': u'Foronídeos', 'parent': u'Metazoa'},
	{'name': u'Crustacea', 'common': u'Crustáceos', 'parent': u'Arthropoda'},
	{'name': u'Ctenophora', 'common': u'Ctenóforos', 'parent': u'Metazoa'},
	{'name': u'Echinoidea', 'common': u'Equinóides', 'parent': u'Echinodermata'},
	{'name': u'Bryozoa', 'common': u'briozoários', 'parent': u'Metazoa'},
]
genera = [
	{'name': u'Discoporella', 'common': u'', 'parent': None},
	{'name': u'Clypeaster', 'common': u'', 'parent': None},
	{'name': u'Bolinopsis', 'common': u'', 'parent': None},
	{'name': u'Arbacia', 'common': u'', 'parent': None},
	{'name': u'Beroe', 'common': u'', 'parent': None},
	{'name': u'Brachidontes', 'common': u'', 'parent': None},
	{'name': u'Eunice', 'common': u'', 'parent': None},
	{'name': u'Cyprys', 'common': u'', 'parent': None},
	{'name': u'Ocyropsis', 'common': u'', 'parent': None},
	{'name': u'Thysanocardia', 'common': u'', 'parent': None},
	{'name': u'Vallicula', 'common': u'', 'parent': None},
	{'name': u'Watersipora', 'common': u'', 'parent': None},
	{'name': u'Phascolosoma', 'common': u'', 'parent': None},
	{'name': u'Mnemiopsis', 'common': u'', 'parent': None},
	{'name': u'Phragmatopoma', 'common': u'', 'parent': None},
	{'name': u'Lytechinus', 'common': u'', 'parent': None},
	{'name': u'Platypodiella', 'common': u'', 'parent': None},
	{'name': u'Themiste', 'common': u'', 'parent': None},
	{'name': u'Leucothea', 'common': u'', 'parent': None},
	{'name': u'Polygordius', 'common': u'', 'parent': None},
	{'name': u'Echinaster', 'common': u'', 'parent': None},
	{'name': u'Catenicella', 'common': u'', 'parent': None},
	{'name': u'Encope', 'common': u'', 'parent': None},
	{'name': u'Zoobotryon', 'common': u'', 'parent': None},
	{'name': u'Steganoporella', 'common': u'', 'parent': None},
	{'name': u'Parasagitta', 'common': u'', 'parent': None},
	{'name': u'Sipunculus', 'common': u'', 'parent': None},
	{'name': u'Trichoplax', 'common': u'', 'parent': None},
	{'name': u'Saccoglossus', 'common': u'', 'parent': None},
	{'name': u'Doris', 'common': u'', 'parent': u'Mollusca'},
]
species = [
	{'name': u'buskii', 'common': u'', 'parent': u'Steganoporella'},
	{'name': u'crystallina', 'common': u'', 'parent': u'Ocyropsis'},
	{'name': u'multiformis', 'common': u'', 'parent': u'Vallicula'},
	{'name': u'multicornis', 'common': u'', 'parent': u'Leucothea'},
	{'name': u'emarginata', 'common': u'', 'parent': u'Encope'},
	{'name': u'variegatus', 'common': u'', 'parent': u'Lytechinus'},
	{'name': u'leidyi', 'common': u'', 'parent': u'Mnemiopsis'},
	{'name': u'fredrici', 'common': u'', 'parent': u'Parasagitta'},
	{'name': u'subdepressus', 'common': u'', 'parent': u'Clypeaster'},
	{'name': u'umbellata', 'common': u'', 'parent': u'Discoporella'},
	{'name': u'caudata', 'common': u'', 'parent': u'Phragmatopoma'},
	{'name': u'vitrea', 'common': u'', 'parent': u'Bolinopsis'},
	{'name': u'alutacea', 'common': u'', 'parent': u'Themiste'},
	{'name': u'solisianus', 'common': u'', 'parent': u'Brachidontes'},
	{'name': u'catharinae', 'common': u'', 'parent': u'Thysanocardia'},
	{'name': u'ovata', 'common': u'', 'parent': u'Beroe'},
	{'name': u'lixula', 'common': u'', 'parent': u'Arbacia'},
	{'name': u'brasiliensis', 'common': u'', 'parent': u'Echinaster'},
	{'name': u'bromophenolosus', 'common': u'', 'parent': u'Saccoglossus'},
	{'name': u'adhaerens', 'common': u'', 'parent': u'Trichoplax'},
	{'name': u'phalloides', 'common': u'', 'parent': u'Sipunculus'},
	{'name': u'sebastiani', 'common': u'', 'parent': u'Eunice'},
	{'name': u'stephensoni', 'common': u'', 'parent': u'Phascolosoma'},
	{'name': u'contei', 'common': u'', 'parent': u'Catenicella'},
]



####################################################

for tagcat in tagcats:
    print tagcat
    if tagcat['parent'] and tagcat['parent'] != u'None':
        tagcat_parent, new = TagCategory.objects.get_or_create(
                name=tagcat['parent'])
    else:
        tagcat_parent = None
    if tagcat['description'] == u'None':
        tagcat_description = u''
    else:
        tagcat_description = tagcat['description']
    zero, new = TagCategory.objects.get_or_create(name=tagcat['name'])
    zero.description=tagcat_description
    zero.parent=tagcat_parent
    zero.save()

for tag in tags:
    print tag
    if tag['parent'] and tag['parent'] != u'None':
        tag_parent, new = TagCategory.objects.get_or_create(
                name=tag['parent'])
    else:
        tag_parent = None
    if tag['description'] == u'None':
        tag_description = u''
    else:
        tag_description = tag['description']
    zero, new = Tag.objects.get_or_create(name=tag['name'])
    zero.description=tag_description
    zero.parent=tag_parent
    zero.save()

for taxon in taxa:
    print taxon
    if taxon['parent'] and taxon['parent'] != u'None':
        taxon_parent, new = Taxon.objects.get_or_create(
                name=taxon['parent'])
    else:
        taxon_parent = None
    if taxon['common'] == u'None':
        taxon_common = u''
    else:
        taxon_common = taxon['common']
    zero, new = Taxon.objects.get_or_create(name=taxon['name'])
    zero.common=taxon_common
    zero.parent=taxon_parent
    zero.save()

#for genus in genera:
#    print genus
#    if genus['parent'] and genus['parent'] != u'None':
#        genus_parent, new = Genus.objects.get_or_create(
#                name=genus['parent'])
#    else:
#        genus_parent = None
#    if genus['common'] == u'None':
#        genus_common = u''
#    else:
#        genus_common = genus['common']
#    zero, new = Genus.objects.get_or_create(name=genus['name'])
#    zero.common=genus_common
#    zero.parent=genus_parent
#    zero.save()
#
#for sp in species:
#    print sp
#    if sp['parent'] and sp['parent'] != u'None':
#        sp_parent, new = Species.objects.get_or_create(
#                name=sp['parent'])
#    else:
#        sp_parent = None
#    if sp['common'] == u'None':
#        sp_common = u''
#    else:
#        sp_common = sp['common']
#    zero, new = Species.objects.get_or_create(name=sp['name'])
#    zero.common=sp_common
#    zero.parent=sp_parent
#    zero.save()
#
