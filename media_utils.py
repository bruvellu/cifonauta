#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# media_utils.py @ CIFONAUTA
# Copyleft 2010-2011 - Bruno C. Vellutini | organelas.com
#
#TODO Definir licença.
#
# Atualizado: 16 Feb 2011 01:09AM
'''Biblioteca de apoio para arquivos multimídia.

Guarda funções úteis para a manipulação de fotos e imagens. Criar thumbnails, 
extrair duração, otimizar, etc.

Centro de Biologia Marinha da Universidade de São Paulo.
'''

import logging
import os
import subprocess
from shutil import copy2

# Instancia logger.
logger = logging.getLogger('cifonauta.utils')

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010-2011, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.1'
__maintainer__ = 'Bruno Vellutini'
__email__ = 'organelas@gmail.com'
__status__ = 'Development'

# dir_ready
# get_info
# build_call
# process_video
# create_meta?
# get_exif
# get_gps
# get_decimal
# resolve
# get_date
# process image
# optimize
# check_file
# rename_file
# get_initials
# create_id
# prepare_meta

#TODO Checar se o ImageMagick está instalado.
#TODO Checar se o FFmpeg está instalado.


def create_thumb(filepath, destination):
    '''Cria thumbnail para foto.'''
    # Confere argumentos.
    if not os.path.isfile(filepath):
        logger.critical('%s não é um arquivo válido.', filepath)
    if not os.path.isdir(destination):
        logger.critical('%s não é um destino válido.', destination)

    # Define nome do thumbnail.
    filename = os.path.basename(filepath)

    # Checa se nome do arquivo tem pontos.
    if filename.count('.') > 1:
        logger.critical('Mais de um "." em %s', filename)
    else:
        filename = filename.split('.')[0] + '.jpg'

    # Define caminho para pasta local.
    localpath = os.path.join(destination, filename)

    # Define comando a ser executado.
    magick_call = [
            'convert', '-define', 'jpeg:size=200x150', filepath, '-thumbnail', 
            '120x90^', '-gravity', 'center', '-extent', '120x90', localpath
            ]

    # Executando o ImageMagick
    try:
        subprocess.call(magick_call)
        logger.debug('Thumb criado em %s', localpath)
        return localpath
    except IOError:
        logger.warning('Erro ao criar thumb %s', localpath)
        return None

def create_still(filepath, destination):
    '''Cria still para o vídeo e thumbnail em seguida.'''
    # Confere argumentos.
    if not os.path.isfile(filepath):
        logger.critical('%s não é um arquivo válido.', filepath)
    if not os.path.isdir(destination):
        logger.critical('%s não é um destino válido.', destination)

    # Define nome do thumbnail.
    filename = os.path.basename(filepath)

    # Checa se nome do arquivo tem pontos.
    if filename.count('.') > 1:
        logger.critical('Mais de um "." em %s', filename)
    else:
        thumbname = filename.split('.')[0] + '.jpg'
        stillname = filename.split('.')[0] + '_still.jpg'

    # Define caminho para pasta local.
    thumbpath = os.path.join(destination, thumbname)
    stillpath = os.path.join(destination, stillname)

    # Define comando a ser executado.
    if filepath.endswith('m2ts'):
        ffmpeg_call = [
                'ffmpeg', '-i', filepath, '-vframes', '1', '-vf', 
                'scale=512:288', '-aspect', '16:9', '-ss', '1', '-f', 'image2',
                stillpath
                ]
    else:
        ffmpeg_call = [
                'ffmpeg', '-i', filepath, '-vframes', '1', '-vf', 
                'scale=512:384', '-ss', '1', '-f', 'image2', stillpath
                ]

    # Executando o ffmpeg
    try:
        subprocess.call(ffmpeg_call)
        logger.debug('Still criado em %s', stillpath)
        # Copia still para servir de template para thumb.
        copy2(stillpath, thumbpath)
        # Cria thumbnail normal.
        thumbpath = create_thumb(thumbpath, destination)
        return thumbpath, stillpath
    except IOError:
        logger.warning('Erro ao criar still %s', stillpath)
        return None, None

def convert_to_web(filepath, finalpath):
    '''Redimensiona e otimiza fotos para a rede.'''
    convert_call = ['convert', filepath, '-density', '72', '-format', 'jpg',
            '-quality', '70', '-resize', '800x800>', finalpath]
    try:
        subprocess.call(convert_call)
        logger.debug('%s processado com sucesso.', finalpath)
        return finalpath
    except:
        logger.critical('Erro ao converter %s', filepath)
        return None

def watermarker(filepath):
    '''Insere marca d'água em foto.'''
    # Arquivo com marca d'água.
    watermark = u'marca.png'
    # Constrói chamada para canto esquerdo embaixo.
    mark_call = ['composite', '-gravity', 'southwest', watermark, filepath, 
            filepath]
    try:
        subprocess.call(mark_call)
        logger.debug('Marca d\'água adicionada em %s', filepath)
        return True
    except:
        logger.warning('Erro ao adicionar marca em %s', filepath)
        return False
