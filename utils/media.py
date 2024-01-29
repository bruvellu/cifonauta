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
from PIL import Image
import pyexiv2
import piexif

# Get logger
logger = logging.getLogger('cifonauta.utils')


def resize_image(filepath, dimension, quality):
    '''Uses Pillow's thumbnail method to scale images.'''
    image = Image.open(filepath)
    image.thumbnail((dimension, dimension))
    try:
        image.convert('RGB').save(filepath, format='jpeg', quality=quality)
        return True
    except:
        logger.critical(f'Could not save {filepath}!')
        return False


def resize_video(input_path, dimension, bitrate, output_path):
    '''Uses FFmpeg to scale and convert videos.'''
    # min(width, iw) prevents upscaling
    # lanczos is a better resizing algorithm
    ffmpeg_call = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                   '-threads', '0', '-i', input_path,
                   '-b:v', f'{bitrate}k', '-filter:v',
                   f'scale=\'min({dimension},iw)\':-2:flags=lanczos',
                   output_path]
    try:
        subprocess.call(ffmpeg_call)
        return True
    except:
        logger.critical(f'Could not save {output_path}!')
        return False


def extract_video_cover(input_path, dimension, output_path):
    '''Uses FFmpeg to scale and convert videos.'''
    ffmpeg_call = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                   '-i', input_path, '-vframes', '1',
                   '-filter:v', f'scale={dimension}:-2',
                   '-ss', '1', '-f', 'image2', output_path]
    try:
        subprocess.call(ffmpeg_call)
        return True
    except:
        logger.critical(f'Could not save {output_path}!')
        return False


#TODO: Remove?
def read_photo_metadata(filepath):
    '''Parses image metadata using GExiv2.'''
    metadata = GExiv2.Metadata(filepath)
    if not metadata.get_tags():
        return None
    else:
        return metadata


#TODO: Keep for the watermark
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

#TODO: Clean up from here

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

        # Make sure sec has only two digits.
        if len(str(gps['latsec'])) > 2:
            gps['latsec'] = int(str(gps['latsec'])[:2])

        latitude = get_decimal(gps['latref'], gps['latdeg'], gps['latmin'],
                gps['latsec'])

        # Longitude.
        long_split = info['Exif.GPSInfo.GPSLongitude'].split() # ['23/1', '49/1', '59/1']
        gps['longdeg'] = int(long_split[0].split('/')[0])
        gps['longmin'] = int(long_split[1].split('/')[0])
        gps['longsec'] = int(long_split[2].split('/')[0])
        gps['longref'] = info['Exif.GPSInfo.GPSLongitudeRef']

        # Make sure sec has only two digits.
        if len(str(gps['longsec'])) > 2:
            gps['longsec'] = int(str(gps['longsec'])[:2])

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

class Metadata():
    
    CONSTANTES = {
        'headline': {
            'iptc': 'Iptc.Application2.Headline'
        },
        'instructions': {
            'iptc': 'Iptc.Application2.SpecialInstructions',
        },
        'source': {
            'iptc': 'Iptc.Application2.Source',
            'xmp': 'Xmp.photoshop.Source'
        },
        'credit': {
            'iptc': 'Iptc.Application2.Credit',
            'xmp': 'Xmp.photoshop.Credit'
        },
        'license': {
            'xmp': {
                'name': 'Xmp.cc.AttributionName',
                'url': 'Xmp.cc.AttributionURL',
                'text': 'Xmp.cc.License'
            }
        },
        'keywords': {
            'iptc': 'Iptc.Application2.Keywords'
        },
        'description_pt': {
            'exif': 'Exif.Image.ImageDescription',
            'xmp': 'Xmp.dc.Description-pt-BR'
        },
        'description_en': {
            'xmp': 'Xmp.dc.Description-en-US'
        },
        'title_pt': {
            'xmp': 'Xmp.dc.Title-pt-BR',
            'iptc': 'Iptc.Application2.ObjectName'
        },
        'title_en': {
            'xmp': 'Xmp.dc.Title-en-US'
        },
        'datetime': {
            'exif': 'Exif.Image.DateTime',
            'iptc': 'Iptc.Application2.ReleaseDate'
        },
        'country': {
            'iptc': 'Iptc.Application2.CountryName'
        },
        'state': {
            'iptc': 'Iptc.Application2.ProvinceState'
        },
        'city': {
            'iptc': 'Iptc.Application2.City'
        },
        'sublocation': {
            'iptc': 'Iptc.Application2.SubLocation'
        },
        'software': {
            'exif': 'Exif.Image.Software'
        },
        'authors': {
            'exif': 'Exif.Image.Artist'
        },
        'datetime_original': {
            'exif': 'Exif.Image.DateTimeOriginal'
        },
        'created_date': {
            'exif': 'Exif.Image.CreateDate',
            'iptc': 'Iptc.Application2.DateCreated'
        },

    }

    def __init__(self, file):
        self.file = file
        
    #TODO: Confusing to use media here, it's only the metadata
    def read_media(self):
        self.media = pyexiv2.ImageMetadata(self.file)
        self.media.read()

    def insert_xmp(self, key, value):
        if value != None:
            tag = self.CONSTANTES[key]['xmp']
            self.media[tag] = value
    
    def insert_xmp_license(self, key, value):
        try:
            pyexiv2.xmp.register_namespace('http://creativecommons.org/ns/', 'cc')
        except KeyError:
            pass
        tag = self.CONSTANTES['license']['xmp'][key]
        self.media[tag] = value
    
    def insert_exif(self, key, value):
        if value != None:
            tag = self.CONSTANTES[key]['exif']
            self.media[tag] = value
    
    def insert_exif_gps(self, value):
        if value != '':
            gps = {}
            gps[1] = value[0].encode()
            gps[2] = ((int(value[2:4]), 1), (int(value[5:7]), 1), (int(value[8:10]), 1))
            gps[3] = value[12].encode()
            gps[4] = ((int(value[14:16]), 1), (int(value[17:19]), 1), (int(value[20:22]), 1))
            exif_dict = {'GPS': gps}

            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, self.file)

    
    def insert_iptc(self, key, value:list):
        if value != None:
            tag = self.CONSTANTES[key]['iptc']
            self.media[tag] = value
    
    def insert_metadata(self, metadata:dict):
        metadata_keys = metadata.keys()

        if 'gps' in metadata_keys:
            gps = metadata['gps']
            self.insert_exif_gps(gps)
        
        self.read_media()
        self.insert_exif('software', 'Cifonauta - CEBIMar/USP')

        if 'headline' in metadata_keys:
            self.insert_iptc('headline', [metadata['headline']])

        if 'instructions' in metadata_keys:
            SCALE_CHOICES = {'micro': '<0,1 mm',
                     'tiny': '0,1–1,0 mm',
                     'visible': '1,0–10 mm',
                     'large': '10–100 mm',
                     'huge': '>100 mm'}
            if metadata['instructions'] in SCALE_CHOICES.keys():
                self.insert_iptc('instructions', [SCALE_CHOICES[metadata['instructions']]])
        
        if 'source' in metadata_keys:
            self.insert_iptc('source', [metadata['source']])
            self.insert_xmp('source', metadata['source'])

        if 'credit' in metadata_keys:
            self.insert_iptc('credit', [metadata['credit']])
            self.insert_xmp('credit', metadata['credit'])

        if 'license' in metadata_keys:
            RIGHTS = {
            "cc0": {
                "license_link": "https://creativecommons.org/publicdomain/zero/1.0/deed.pt_BR",
                "license_name": "CC0",
                "license_text": "Sem Direito de Autor nem Direitos Conexos, onde a pessoa que associou um trabalho a este resumo dedicou o trabalho ao domínio público, renunciando a todos os seus direitos sob as leis de direito de autor e/ou de direitos conexos referentes ao trabalho, em todo o mundo, na medida permitida por lei. Você pode copiar, modificar, distribuir e executar o trabalho, mesmo para fins comerciais, tudo sem pedir autorização. A CC0 não afeta, de forma alguma, os direitos de patente ou de marca de qualquer pessoa, nem os direitos que outras pessoas possam ter no trabalho ou no modo como o trabalho é utilizado, tais como direitos de imagem ou de privacidade. Desde que nada seja expressamente afirmado em contrário, a pessoa que associou este resumo a um trabalho não fornece quaisquer garantias sobre o mesmo e exonera-se de responsabilidade por quaisquer usos do trabalho, na máxima medida permitida pela lei aplicável. Ao utilizar ou citar o trabalho, não deve deixar implícito que existe apoio do autor ou do declarante."
                },
            "cc_by": {
                "license_link": "https://creativecommons.org/licenses/by/4.0/",
                "license_name": "CC BY",
                "license_text": "Você é livre para compartilhar e adaptar o conteúdo para qualquer finalidade, até mesmo comercial. Esta licença é aceitável para Trabalhos Culturais Gratuitos. O licenciante não pode revogar essas liberdades enquanto você seguir os termos da licença. Você deve dar o devido crédito , fornecer um link para a licença e indicar se foram feitas alterações . Você pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso. Sem restrições adicionais, logo, você não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                },
            "cc_by_nd": {
                "license_link": "https://creativecommons.org/licenses/by-nd/4.0/",
                "license_name": "CC BY-ND",
                "license_text": "Você é livre para: Compartilhar – copie e redistribua o material em qualquer meio ou formato para qualquer finalidade, até mesmo comercial. Você deve dar o devido crédito , fornecer um link para a licença e indicar se foram feitas alterações , pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso. Se você remixar, transformar ou desenvolver o material, não poderá distribuir o material modificado. Sem restrições adicionais, logo, não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                },
            "cc_by_sa": {
                "license_link": "https://creativecommons.org/licenses/by-sa/4.0/",
                "license_name": "CC BY-SA",
                "license_text": "Você é livre para: compartilhar e adaptar. Você deve dar o devido crédito , fornecer um link para a licença e indicar se foram feitas alterações, pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso. Se você remixar, transformar ou desenvolver o material, deverá distribuir suas contribuições sob a mesma licença do original. Sem restrições adicionais, logo, não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                },
            "cc_by_nc": {
                "license_link": "https://creativecommons.org/licenses/by-nc/4.0/",
                "license_name": "CC BY-NC",
                "license_text": "Você é livre para: compartilhar e adaptar.  Você deve dar o devido crédito , fornecer um link para a licença e indicar se foram feitas alterações . Você pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso, e não é permitido usar o material para fins comerciais. Sem restrições adicionais, logo, não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                },
            "cc_by_nc_sa": {
                "license_link": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                "license_name": "CC BY-NC-SA",
                "license_text": "Você é livre para: compartilhar. Deve-se dar o devido crédito, fornecer um link para a licença e indicar se foram feitas alterações. Você pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso. Não pode usar o material para fins comerciais e se remixar, transformar ou desenvolver o material, não poderá distribuir o material modificado. No geral, não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                },
            "cc_by_nc_nd": {
                "license_link": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
                "license_name": "CC BY-NC-ND",
                "license_text": "Você é livre para: compartilhar e editar. Devendo-se dar o devido crédito, fornecer um link para a licença e indicar se foram feitas alterações. Você pode fazê-lo de qualquer maneira razoável, mas não de forma que sugira que o licenciante endossa você ou seu uso, além de não poder usar o material para fins comerciais. Se você remixar, transformar ou desenvolver o material, deverá distribuir suas contribuições sob a mesma licença do original. Sem restrições adicionais, logo, não pode aplicar termos legais ou medidas tecnológicas que restrinjam legalmente outras pessoas de fazer qualquer coisa que a licença permita."
                }
            }
            license_name = RIGHTS[metadata['license']]['license_name']
            license_link = RIGHTS[metadata['license']]['license_link']
            license_text = RIGHTS[metadata['license']]['license_text']

            self.insert_xmp_license('name', license_name)
            self.insert_xmp_license('url', license_link)
            self.insert_xmp_license('text', license_text)

        if 'keywords' in metadata_keys:
            self.insert_iptc('keywords', metadata['keywords'])

        if 'description_pt' in metadata_keys:
            self.insert_exif('description_pt', metadata['description_pt'])
            self.insert_xmp('description_pt', metadata['description_pt'])

        if 'description_en' in metadata_keys:
            self.insert_xmp('description_en', metadata['description_en'])

        if 'title_pt' in metadata_keys:
            self.insert_xmp('title_pt', metadata['title_pt'])

        if 'authors' in metadata_keys:
            self.insert_exif('authors', metadata['authors'])
        if 'title_en' in metadata_keys:
            self.insert_xmp('title_en', metadata['title_en'])
        
        
        self.media.write()

    def read_metadata(self):
        metadata = {}

        keys = [('title_pt', 'xmp'),
                ('title_en', 'xmp'),
                ('description_pt', 'xmp'),
                ('description_en', 'xmp'),
                ('authors', 'exif')]
        
        metadata['gps'] = self.read_exif_gps()

        self.read_media()

        date = self.read_exif('datetime')
        if date == '':
            date = self.read_exif('datetime_original')
        if date == '':
            date = self.read_exif('create_date')
        if date == '':
            date = self.read_iptc('datetime')
        if date == '':
            date = self.read_iptc('create_date')

        metadata['datetime'] = date

        for key in keys:
            if key[1] == 'xmp':
                metadata[key[0]] = self.read_xmp(key[0])
            elif key[1] == 'exif':
                metadata[key[0]] = self.read_exif(key[0])
        
        if metadata['title_pt'] == '':
            metadata['title_pt'] = self.read_exif('title_pt')
        if metadata['title_pt'] == '':
            metadata['title_pt'] = self.read_iptc('title_pt')
        
        return metadata

    def read_xmp(self, key):
        try:
            value = self.media[self.CONSTANTES[key]['xmp']].raw_value
        except:
            value = ''
        return value

    def read_exif(self, key):
        try:
            value = self.media[self.CONSTANTES[key]['exif']].raw_value
        except:
            value = ''
        return value

    def read_iptc(self, key):
        try:
            value = self.media[self.CONSTANTES[key]['iptc']].raw_value
        except:
            value = ''
        if type(value) == list:
            value = value[0]
        return value

    def read_exif_gps(self):
        image = Image.open(self.file)
        try:
            exif_dict = piexif.load(image.info['exif'])
        except:
            return ''
        try:
            gps = exif_dict['GPS']
        except KeyError:
            return ''
        else:
            gps_hexa = f"{gps[1].decode()} {gps[2][0][0]}\u00ba{int(gps[2][1][0])}'{int(gps[2][2][0])}\u0022 {gps[3].decode()} {gps[4][0][0]}\u00ba{int(gps[4][1][0])}'{int(gps[4][2][0])}\u0022"
            latitude = gps[2][0][0] + gps[2][1][0]/60 + gps[2][2][0]/3600
            if gps[1] == b'S':
                latitude = -latitude
            longitude = gps[4][0][0] + gps[4][1][0]/60 + gps[4][2][0]/3600
            if gps[3] == b'W':
                longitude = -longitude
            latitude = f"{latitude:.11f}"
            longitude = f"{longitude:.11f}"
            return {
                'geolocation': gps_hexa,
                'latitude': latitude,
                'longitude': longitude}


def number_of_entries_per_page(request, session_name, value=None):
    if value and int(value) > 0:
        request.session[session_name] = value
    try:
        return request.session[session_name]
    except:
        return 12


def validate_specialist_action_form(request, medias):
    for media in medias:
        if not media.title_pt_br:
            return ['Título [pt-br]', 'Este campo é obrigatório.']
        if not media.title_en:
            return ['Título [en]', 'Este campo é obrigatório.']


def format_name(name):
    preps = ('de', 'da', 'do', 'das', 'dos', 'e', 'no', 'na')
    split_name = name.lower().split(' ')

    name = [word.capitalize() if word not in preps else word for word in split_name]
    name = ' '.join(name)

    return name
