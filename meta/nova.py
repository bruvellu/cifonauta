# -*- coding: utf-8 -*-

from meta.models import *

print u'Criando metadados...'
filepath = u'/home/nelas/CEBIMar/banco/imagens/web/foto007.jpg'
title = u'Praia com costão'
caption = u'Lindo costão.'
author, dummy = Author.objects.get_or_create(name=u'Alvaro E. Migotto')
taxon, dummy = Taxon.objects.get_or_create(name=u'Crustacea')
genus, dummy = Genus.objects.get_or_create(name=u'')
sp, dummy = Species.objects.get_or_create(name=u'')
size, dummy = Size.objects.get_or_create(range=u'')
source, dummy = Source.objects.get_or_create(name=u'Leandro M. Vieira')
rights, dummy = Rights.objects.get_or_create(name=u'CEBIMar-USP')
sublocal, dummy = Sublocal.objects.get_or_create(name=u'Praia do Segredo')
city, dummy = City.objects.get_or_create(name=u'Ubatuba')
state, dummy = State.objects.get_or_create(name=u'SP')
country, dummy = Country.objects.get_or_create(name=u'Brasil')
print u'Pronto! Criando nova imagem...'
new_image = Image(
        image=filepath,
        title=title,
        caption=caption,
        author=author,
        taxon=taxon,
        genus=genus,
        sp=sp,
        size=size,
        source=source,
        rights=rights,
        sublocal=sublocal,
        city=city,
        state=state,
        country=country,
        )
print u'Pronto! Salvando...'
new_image.save()
print u'Pronto, imagem salva!'
