#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *

# Arquivo que vai guardar.
resetfile = open('reset0.py', 'w')

# Tags
tags = Tag.objects.all()
resetfile.write('tags = [\n')
for tag in tags:
    resetfile.write(
            '\t{\'name\': u\'%s\', \'description\': u\'%s\', \'parent\': u\'%s\'},\n' %
            (tag.name, tag.description, tag.parent))
resetfile.write(']\n')

# TagsCategories
tags = TagCategory.objects.all()
resetfile.write('tagcats = [\n')
for tag in tags:
    resetfile.write(
            '\t{\'name\': u\'%s\', \'description\': u\'%s\', \'parent\': u\'%s\'},\n' %
            (tag.name, tag.description, tag.parent))
resetfile.write(']\n')

# Taxa 
tags = Taxon.objects.all()
resetfile.write('taxa = [\n')
for tag in tags:
    resetfile.write(
            '\t{\'name\': u\'%s\', \'common\': u\'%s\', \'parent\': u\'%s\'},\n' %
            (tag.name, tag.common, tag.parent))
resetfile.write(']\n')

# Genera
tags = Genus.objects.all()
resetfile.write('genera = [\n')
for tag in tags:
    resetfile.write(
            '\t{\'name\': u\'%s\', \'common\': u\'%s\', \'parent\': u\'%s\'},\n' %
            (tag.name, tag.common, tag.parent))
resetfile.write(']\n')

# Species
tags = Species.objects.all()
resetfile.write('species = [\n')
for tag in tags:
    resetfile.write(
            '\t{\'name\': u\'%s\', \'common\': u\'%s\', \'parent\': u\'%s\'},\n' %
            (tag.name, tag.common, tag.parent))
resetfile.write(']\n')
# Fechando o arquivo
resetfile.close()
