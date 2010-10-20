# -*- coding: utf-8 -*-

from fabric.api import *

env.hosts = ['143.107.42.231']

def test():
    local('./manage.py test meta', capture=False)

def local_reset():
    local('./reset.py', capture=False)

def site_reset():
    with cd('.local/lib/python/weblarvae/'):
        run('reset.py')

def clean_local_media():
    local('rm -r source_media/*')
    local ('rm -r site_media/photos/*')
    local('rm -r site_media/videos/*')
    local('rm -r local_media/*')

def clean_site_media():
    run('rm -r source_media/*')
    run('rm -r site_media/photos/*')
    run('rm -r site_media/videos/*')
    run('rm -r local_media/*')

def sync():
    local('rsync -ah -L --delete --progress --exclude-from=\'.exclude\' -e ssh /home/nelas/CEBIMar/weblarvae 143.107.42.231:/home/nelas/.local/lib/python/', capture=False)

programs = 'python --version; psql --version; django-admin.py --version; convert --version'

def versions():
    local(programs, capture=False)
    with cd('.local/lib/python/weblarvae/'):
        run(programs)
