#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *


def check(photos, videos):
    '''Checa para ver se os IDs passados são válidos.'''
    # Fotos.
    for id in photos:
        isok = Image.objects.filter(id=id).exists()
        if not isok:
            print 'Não existe foto com id=%s!' % id
            sys.exit(2)
    for id in videos:
        isok = Video.objects.filter(id=id).exists()
        if not isok:
            print 'Não existe vídeo com id=%s!' % id
            sys.exit(2)
    print 'id estão beleza, continuando...'
    return True


def compile_paths(media):
    '''Agrega arquivos que serão excluídos.'''
    to_be_removed = [
            #media.old_filepath,
            media.source_filepath,
            media.thumb_filepath.path,
            media.thumb_filepath.path.replace('site_media', 'local_media'),
            ]
    print
    print 'VOCÊ ESTÁ PRESTES A DELETAR A IMAGEM:'''
    print '\t', media.datatype, media.id, ' - ', media.title
    if media.caption:
        print '\t', media.caption
    print '\t', ', '.join([author.name for author in media.author_set.all()])
    if media.highlight:
        print '\tÉ um destaque!'
    if media.cover:
        print '\tÉ uma imagem de capa!'
    if media.datatype == 'video':
        to_be_removed.append(media.large_thumb.path)
        to_be_removed.append(media.large_thumb.path.replace(
            'site_media', 'local_media'))
        to_be_removed.append(media.mp4_filepath.path)
        to_be_removed.append(media.mp4_filepath.path.replace(
            'site_media', 'local_media'))
        to_be_removed.append(media.ogg_filepath.path)
        to_be_removed.append(media.ogg_filepath.path.replace(
            'site_media', 'local_media'))
        #XXX Gambiarra, acabei de descobrir q o .webm fica cortado!
        to_be_removed.append(media.webm_filepath.path + 'm')
        to_be_removed.append(media.webm_filepath.path.replace(
            'site_media', 'local_media') + 'm')
        to_be_removed.append(media.source_filepath.split('.')[0] + '.txt')
    else:
        to_be_removed.append(media.web_filepath.path)
        to_be_removed.append(media.web_filepath.path.replace(
            'site_media', 'local_media'))
    print '\tESTES ARQUIVOS SERÃO REMOVIDOS:'''
    for path in to_be_removed:
        print '\t', path
    print

    return to_be_removed


def delete(media, force=False):
    '''Executa a deleção.'''
    to_be_removed = compile_paths(media)
    if force:
        proceed = 's'
    else:
        proceed = raw_input('Deseja continuar? (s ou n): ')
    if proceed == 's':
        print '\nDeletando objeto...'
        media.delete()
        for path in to_be_removed:
            try:
                print 'Deletando', path
                os.remove(path)
            except:
                print 'NÃO CONSEGUI DELETAR O ARQUIVO:'
                print path
                jump = raw_input('Continuar? (s ou n): ')
                if jump == 'n':
                    sys.exit(2)
    try:
        original_file = os.readlink(media.source_filepath)
        original = raw_input('\nDeseja apagar o arquivo original? (s ou n):\n%s ' % original_file)
        if original == 's':
            os.remove(original_file)
    except:
        print 'Arquivo original já não existe...'


def prepare(photos, videos):
    '''Prepara a deleção.'''
    for id in photos:
        photo = Image.objects.get(id=id)
        delete(photo)
    for id in videos:
        video = Video.objects.get(id=id)
        delete(video)


def get_orphans(entries):
    '''Get orphans and duplicates from a queryset.

    Works for photos and videos, returns 2 lists.'''
    #TODO! Use only one get_orphans function, remove from meta.views.
    # Cria lista de órfãs e dic de duplicadas.
    orphaned = []
    duplicates = []
    dups = {}
    # Le o link com o caminho para o arquivo original.
    # Se o original não existir, é orfã.
    for entry in entries:
        try:
            original = os.readlink(entry.source_filepath)
            if dups.has_key(original):
                dups[original].append(entry)
            else:
                dups[original] = [entry]
        except OSError:
            orphaned.append(entry)
        else:
            pass
    # Coloca na lista tudo é duplicado.
    for k, v in dups.iteritems():
        if len(v) > 1:
            duplicates.append({'path': k, 'replicas': v})
    return orphaned, duplicates


def main(argv):
    '''Remove imagem do banco de dados e seus arquivos permanentemente.'''
    videos, photos = [], []
    batch_remove = False
    force_remove = False

    try:
        opts, args = getopt.getopt(argv, 'hp:v:af', [
            'help',
            'photo',
            'video',
            'all',
            'force',
            ])
    except getopt.GetoptError:
        print 'Algo de errado nos argumentos...'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print '''Usage: ./remove.py -p 2352,87 -v 314\n*Delete photos with id 2352 and 87 and video with id 314.'''
            sys.exit()
        elif opt in ('-p', '--photo'):
            for id in arg.split(','):
                photos.append(id)
        elif opt in ('-v', '--video'):
            for id in arg.split(','):
                videos.append(id)
        elif opt in ('-a', '--all'):
            batch_remove = True
        elif opt in ('-f', '--force'):
            force_remove = True

    if batch_remove:
        photos = Image.objects.all()
        orphaned_photos, duplicated_photos = get_orphans(photos)
        videos = Video.objects.all()
        orphaned_videos, duplicated_videos = get_orphans(videos)
        orphaned = orphaned_photos
        duplicates = duplicated_photos
        orphaned.extend(orphaned_videos)
        duplicates.extend(duplicated_videos)

        # Delete orphaned and duplicates.
        for orphan in orphaned:
            delete(orphan, force=force_remove)
        for duplicate in duplicates:
            delete(duplicate, force=force_remove)

    else:
        ready = check(photos, videos)
        if ready:
            prepare(photos, videos)

# Início do programa
if __name__ == '__main__':
    main(sys.argv[1:])
