# -*- coding: utf-8 -*-

from fabric.api import *

env.hosts = ['143.107.42.231:/home/nelas/.local/lib/python/weblarvae/']

def test():
    local('./manage.py test meta', capture=False)

def local_reset():
    local('./reset.py', capture=False)

def site_reset():
    run('./reset.py')

def sync():
    local('rsync -ah -L --delete --progress --exclude-from=\'.exclude\' -e ssh /home/nelas/CEBIMar/weblarvae 143.107.42.231:/home/nelas/.local/lib/python/', capture=False)

programs = 'python --version; psql --version; django-admin.py --version; convert --version'

def versions():
    local(programs, capture=False)
    with cd('.local/lib/python/weblarvae/'):
        run(programs)
