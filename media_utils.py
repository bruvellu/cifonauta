#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Library for media utilities.

Common functions to read image metadata and create thumbnails.
'''

import logging
import os
import random
import re
import subprocess
from datetime import datetime
from django.utils import timezone
from shutil import copy2, move

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

# Get logger.
logger = logging.getLogger('cifonauta.utils')


def read_photo_metadata(filepath):
    '''Parses image metadata using GExiv2.'''
    metadata = GExiv2.Metadata(filepath)
    if not metadata.get_tags():
        return None
    else:
        return metadata


def read_iptc(abspath, charset='utf-8', new=False):
    '''Parses IPTC metadata from a photo with iptcinfo.py'''

    info = IPTCInfo(abspath, True, charset)
    if len(info.data) < 4:
        print('IPTC is empty for %s' % abspath)
        return None

    return info


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


def video_to_web(filepath, sitepath, metadata):
    '''Convert video for web using FFmpeg.

    # HD
    ffmpeg -y -i hd.m2ts -i marca.png -metadata title="A MP4 HD" -metadata author="AN AUTHOR"
    -b:v 600k -threads 0 -acodec libfaac -b:a 128k -ac 2 -ar 44100 -vcodec libx264
    -filter_complex "scale=512x288,overlay=0:main_h-overlay_h-0" hd.mp4

    # SD
    ffmpeg -y -i dv.avi -i marca.png -metadata title="A MP4 DV" -metadata author="AN AUTHOR"
    -b:v 600k -threads 0 -acodec libfaac -b:a 128k -ac 2 -ar 44100 -vcodec libx264
    -filter_complex "scale=512x384,overlay=0:main_h-overlay_h-0" '-aspect', '4:3',dv.mp4
    '''

    # FFMPEG command.
    video_call = [
            'ffmpeg', '-y',
            '-hide_banner',
            '-loglevel', 'error',
            '-threads', '0',
            '-i', filepath,
            '-i', 'marca.png',
            '-metadata', 'title={}'.format(metadata.title),
            '-metadata', 'artist={}'.format(metadata.author),
            '-b:v', '600k',
            '-filter_complex', 'scale=512:-2,overlay=0:main_h-overlay_h-0',
            sitepath
            ]

    # Audio codec.
    #video_call.extend(['-acodec', 'libfaac', '-b:a', '128k', '-ac', '2', '-ar', '44100'])

    # Video codec.
    #video_call.extend(['-vcodec', 'libx264'])

    # Add destination.
    #video_call.append(sitepath)

    # Execute.
    subprocess.call(video_call)


def grab_still(filepath, coverpath):
    '''Grab video's first frame.'''

    # Command to be called.
    ffmpeg_call = [
            'ffmpeg', '-y',
            '-hide_banner',
            '-loglevel', 'error',
            '-i', filepath,
            '-vframes', '1',
            '-filter_complex', 'scale=512:-2',
            '-ss', '1',
            '-f', 'image2',
            coverpath
            ]

    # Executing ffmpeg.
    try:
        subprocess.call(ffmpeg_call)
        logger.debug('Still criado em %s', coverpath)
        return coverpath
    except IOError:
        logger.warning('Erro ao criar still %s', coverpath)
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
                'ffmpeg', '-y', '-i', filepath, '-vframes', '1', '-filter_complex',
                'scale=512:288', '-aspect', '16:9', '-ss', '1', '-f', 'image2',
                stillpath
                ]
    else:
        ffmpeg_call = [
                'ffmpeg', '-y', '-i', filepath, '-vframes', '1', '-filter_complex',
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

def photo_to_web(filepath, sitepath, size=800):
    '''Resizes and optimizes the photo for the web.'''
    sitepath_jpg = '{}.jpg'.format(os.path.splitext(sitepath)[0])
    convert_call = ['convert', filepath, '-density', '72', '-format', 'jpg',
            '-quality', '70', '-resize', '{}x{}>'.format(size, size), sitepath_jpg]
    try:
        subprocess.call(convert_call)
        watermarker(sitepath_jpg)
        logger.debug('%s processed.', sitepath)
        return sitepath
    except:
        logger.critical('Error converting %s', filepath)
        return None

def watermarker(filepath):
    '''Insert watermark.'''
    # Watermark file.
    watermark = 'marca.png'
    # Put on the left lower side.
    mark_call = ['composite', '-gravity', 'southwest', watermark, filepath,
            filepath]
    try:
        subprocess.call(mark_call)
        logger.debug('Watermark added to %s', filepath)
        return True
    except:
        logger.warning('Error to add watermark on %s', filepath)
        return False

def get_exif_date(info):
    '''Extract creation date from GExiv2 object.'''
    try:
        date = info['Exif.Photo.DateTimeOriginal']
    except:
        try:
            date = info['Exif.Photo.DateTimeDigitized']
        except:
            try:
                date = info['Exif.Image.DateTime']
            except:
                return False
    return date

def get_date(info):
    '''Return the creation data ready for media metadata.'''
    # Extract date from EXIF.
    date = get_exif_date(info)
    if date:
        tz_date = timezone.make_aware(datetime.strptime(date, '%Y:%m:%d %H:%M:%S'))
    else:
        tz_date = timezone.make_aware(datetime.strptime('1900:01:01 01:01:01', '%Y:%m:%d %H:%M:%S'))
    return tz_date

def get_gps(info):
    '''Extract GPS coordinates from GExiv2 object.'''
    # Store values.
    gps = {}
    gps_data = {}

    if info and 'Exif.GPSInfo.GPSLatitude' in info.get_tags():
        # Latitude.
        lat_split = info['Exif.GPSInfo.GPSLatitude'].split() # ['23/1', '49/1', '59/1']
        gps['latdeg'] = int(lat_split[0].split('/')[0]) # ['23', '1']
        gps['latmin'] = int(lat_split[1].split('/')[0]) # ['49', '1']
        gps['latsec'] = int(lat_split[2].split('/')[0]) # ['59', '1']
        gps['latref'] = info['Exif.GPSInfo.GPSLatitudeRef']
        latitude = get_decimal(gps['latref'], gps['latdeg'], gps['latmin'],
                gps['latsec'])

        # Longitude.
        long_split = info['Exif.GPSInfo.GPSLongitude'].split() # ['23/1', '49/1', '59/1']
        gps['longdeg'] = int(long_split[0].split('/')[0])
        gps['longmin'] = int(long_split[1].split('/')[0])
        gps['longsec'] = int(long_split[2].split('/')[0])
        gps['longref'] = info['Exif.GPSInfo.GPSLongitudeRef']
        longitude = get_decimal(gps['longref'], gps['longdeg'], gps['longmin'],
                gps['longsec'])

        # Record values.
        gps_data['geolocation'] = '{} {}°{}\'{}" {} {}°{}\'{}"'.format(
                gps['latref'], gps['latdeg'], gps['latmin'], gps['latsec'],
                gps['longref'], gps['longdeg'], gps['longmin'], gps['longsec'])
        gps_data['latitude'] = '{}'.format(latitude)
        gps_data['longitude'] = '{}'.format(longitude)
    else:
        logger.debug('No GPS data.')
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
    dimensions = codecs[-1]
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

def create_filename(filename, authors):
    '''Create filename with author initials and unique ID.'''
    logger.debug('Renomeando %s', filename)
    if authors:
        initials = get_initials(authors)
    else:
        initials = 'cbm'
    unique_id = create_id()
    new_filename = initials + '_' + unique_id + os.path.splitext(filename)[1].lower()
    return new_filename

def get_initials(authors):
    '''Extract author initials.

    Input is list of authors. Split each name by spaces and save first letter.
    Concatenate initials and join them by a dash.
    '''
    initials = '-'.join([''.join([sil[:1] for sil in word.strip().split(' ')]) for word in authors]).lower()
    return initials

def create_id():
    '''Create unique ID for filename.'''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    unique_id = ''.join([random.choice(chars) for x in range(6)])
    return unique_id

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
