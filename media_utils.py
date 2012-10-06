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
import pyexiv2
import random
import re
import subprocess

from shutil import copy2, move

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

# build_call
# process_video
# create_meta?
# process image
# optimize
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

def get_exif(filepath):
    '''Extrai o exif da foto usando o pyexiv2 0.3.0.'''
    logger.debug('Extraindo EXIF de %s', filepath)
    exif = pyexiv2.ImageMetadata(filepath)
    exif.read()
    return exif

def get_exif_date(exif):
    '''Extrai a data em que foi criada a foto do EXIF.'''
    try:
        date = exif['Exif.Photo.DateTimeOriginal']
    except:
        try:
            date = exif['Exif.Photo.DateTimeDigitized']
        except:
            try:
                date = exif['Exif.Image.DateTime']
            except:
                return False
    return date.value

def get_date(exif):
    '''Retorna a data da foto já pronta para metadados.'''
    # Extrai data do exif.
    date = get_exif_date(exif)
    # Faz parsing do valor extraído.
    try:
        date_string = date.strftime('%Y-%m-%d %I:%M:%S')
    except:
        date_string = ''
    if date_string and date_string != '0000:00:00 00:00:00':
        return date
    else:
        return '1900-01-01 01:01:01'

def get_gps(exif):
    '''Extrai coordenadas guardadas no EXIF.'''
    # Para guardar valores.
    gps = {}
    gps_data = {}

    try:
        # Latitude.
        gps['latref'] = exif['Exif.GPSInfo.GPSLatitudeRef'].value
        gps['latdeg'] = exif['Exif.GPSInfo.GPSLatitude'].value[0]
        gps['latmin'] = exif['Exif.GPSInfo.GPSLatitude'].value[1]
        gps['latsec'] = exif['Exif.GPSInfo.GPSLatitude'].value[2]
        latitude = get_decimal(gps['latref'], gps['latdeg'], gps['latmin'], 
                gps['latsec'])

        # Longitude.
        gps['longref'] = exif['Exif.GPSInfo.GPSLongitudeRef'].value
        gps['longdeg'] = exif['Exif.GPSInfo.GPSLongitude'].value[0]
        gps['longmin'] = exif['Exif.GPSInfo.GPSLongitude'].value[1]
        gps['longsec'] = exif['Exif.GPSInfo.GPSLongitude'].value[2]
        longitude = get_decimal(gps['longref'], gps['longdeg'], gps['longmin'], 
                gps['longsec'])

        # Gravando valores prontos.
        gps_data['geolocation'] = '%s %d°%d\'%d" %s %d°%d\'%d"' % (
                gps['latref'], gps['latdeg'], gps['latmin'], gps['latsec'],
                gps['longref'], gps['longdeg'], gps['longmin'], gps['longsec'])
        gps_data['latitude'] = '%f' % latitude
        gps_data['longitude'] = '%f' % longitude
    except:
        logger.debug('Foto sem dados de GPS.')
        # Gravando valores prontos.
        gps_data['geolocation'] = ''
        gps_data['latitude'] = ''
        gps_data['longitude'] = ''
    return gps_data

def get_decimal(ref, deg, min, sec):
    '''Descobre o valor decimal das coordenadas.'''
    decimal_min = (min * 60.0 + sec) / 60.0
    decimal = (deg * 60.0 + decimal_min) / 60.0
    negatives = ['S', 'W']
    if ref in negatives:
        decimal = -decimal
    return decimal


def get_info(video):
    '''Pega informações do vídeo na marra e retorna dicionário.

    Os valores são extraídos do stderr do ffmpeg usando expressões 
    regulares.
    '''
    try:
        call = subprocess.Popen(['ffmpeg', '-i', video],
                stderr=subprocess.PIPE)
    except:
        logger.warning('Não conseguiu abrir o arquivo %s', video)
        return None
    # Necessário converter pra string pra ser objeto permanente.
    info = str(call.stderr.read())
    # Encontra a duração do arquivo.
    length_re = re.search('(?<=Duration: )\d+:\d+:\d+', info)
    # Encontra o codec e dimensões.
    precodec_re = re.search('(?<=Video: ).+, .+, \d+x\d+', info)
    # Processando os outputs brutos.
    #XXX Melhorar isso e definir o formato oficial dos valores.
    # Exemplo (guardar em segundos e converter depois):
    #   >>> import datetime
    #   >>> str(datetime.timedelta(seconds=666))
    #   '0:11:06'
    duration = length_re.group(0)
    codecs = precodec_re.group(0).split(', ')
    codec = codecs[0].split(' ')[0]
    dimensions = codecs[2]
    # Salvando valores limpos em um dicionário.
    details = {
            'duration': duration,
            'dimensions': dimensions,
            'codec': codec,
            }
    return details

def dir_ready(*dirs):
    '''Verifica se diretório(s) existe(m), criando caso não exista.'''
    for dir in dirs:
        if os.path.isdir(dir) is False:
            logger.debug('Criando diretório %s', dir)
            os.makedirs(dir)

def check_file(filepath):
    '''Checa se arquivo existe.'''
    media_file = os.path.isfile(filepath)
    return media_file

def rename_file(filename, authors):
    '''Renomeia arquivo com iniciais e identificador.'''
    logger.debug('Renomeando %s', filename)
    if authors:
        initials = get_initials(authors)
    else:
        initials = 'cbm'
    id = create_id()
    new_filename = initials + '_' + id + '.' + filename.split('.')[1].lower()
    return new_filename

def get_initials(authors):
    '''Extrai iniciais dos autores.

    Faz split por vírgulas, caso tenha mais de 1 autor; para cada autor faz
    split por espaços em branco e pega apenas a primeira letra; junta iniciais
    em sequência; junta autores separados por hífen.

    Não está muito legível, mas é isso aí.
    '''
    initials = '-'.join([''.join([sil[:1] for sil in word.strip().split(' ')]) for word in authors.split(',')]).lower()
    return initials

def create_id():
    '''Cria identificador único para nome do arquivo.'''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    id = ''.join([random.choice(chars) for x in xrange(6)])
    return id

def fix_filename(root, filename):
    '''Checa validade do nome do arquivo.'''
    # Verifica a existência de pontos extras.
    dotcount = filename.count('.')
    if dotcount == 0:
        filepath = os.path.join(root, filename)
        logger.warning('%s sem extensão!', filepath)
    elif dotcount > 1:
        splitname = filename.split('.')
        extension = splitname.pop()
        basename = ''.join(splitname)
        fixedname = basename + '.' + extension
        filepath = os.path.join(root, fixedname)
        oldpath = os.path.join(root, filename)
        try:
            move(oldpath, filepath)
            logger.debug('Corrigido: %s >> %s', filename, fixedname)
        except:
            logger.warning('%s não foi corrigido!', oldpath)
            filepath = oldpath
    else:
        filepath = os.path.join(root, filename)
    return filepath
