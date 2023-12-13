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
import piexif
from iptcinfo3 import IPTCInfo
"""
The "python-xmp-toolkit" library can cause problems if the "Exempi" tool cannot be found.
In this case the metadata will not be saved in XMP format
"""
try:
    from libxmp import XMPFiles, consts, XMPError
    from libxmp.utils import file_to_dict
except:
    print('Warning: python-xmp-toolkit not imported')
    pass


"""import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2"""

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

    def __init__(self, file):

        self.file = file

    def _insert_metadata_exif(self, field, val):
        image = Image.open(self.file)

        #Software
        try:
            exif_dict = piexif.load(image.info['exif'])
        except KeyError:
            exif_dict = {'0th': {}, 'GPS': {}}
            
        finally:
            if field == 'software':
                exif_dict['0th'][piexif.ImageIFD.Software] = val
            elif field == 'image_description':
                exif_dict['0th'][piexif.ImageIFD.ImageDescription] = val
            elif field == 'gps':
                pass
            elif field == 'datetime':
                exif_dict['0th'][piexif.ImageIFD.DateTime] = val
            elif field == 'copyright':
                exif_dict['0th'][piexif.ImageIFD.Copyright] = val
            elif field == 'creators':
                exif_dict['0th'][piexif.ImageIFD.Artist] = val
            elif field == 'keywords':
                exif_dict['0th'][piexif.ImageIFD.XPKeywords] = val
            exif_dict.pop('thumbnail', None)
            exif_bytes = piexif.dump(exif_dict)

            #Saving EXIF
            image.save(self.file, exif=exif_bytes)

    def _insert_metadata_iptc(self, field, val=None, clear=False):

        info = IPTCInfo(self.file, force=True)

        info[field] = val
        
        # Saving IPTC
        info.save_as(self.file)
        os.remove(f'{self.file}~')


    def _insert_metadata_xmp(self, field, val, license=False):
    
        #XMP Config
        try:
            self.xmpfile = XMPFiles( file_path=self.file, open_forupdate=True)
            xmp = self.xmpfile.get_xmp()
            if license:
                xmp.register_namespace('http://creativecommons.org/ns#', 'cc')
                xmp.set_property(consts.XMP_NS_CC, field, val)
            else:
                xmp.set_property(consts.XMP_NS_DC, field, val)

            #Saving metadata
            if self.xmpfile.can_put_xmp(xmp):
                self.xmpfile.put_xmp(xmp)
            self.xmpfile.close_file()
        except:
            pass

    def edit_metadata(self, metadata:dict):
    
        self._RIGHTS = {
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
        
        self.xmp_erro = False
        
        self.metadata = metadata

        self._insert_metadata_exif('software', 'CebimarUSP')

        for k, v in self.metadata.items():
            if v != '' and v != ' ' and v != None:
                match k:
                    case "headline":
                        self._insert_metadata_xmp(k.capitalize(), v)
                        self._insert_metadata_iptc(k, v)
                    case "instructions":
                        self._insert_metadata_iptc('special instructions', v)
                        self._insert_metadata_xmp('Instructions', v)
                    case "source":
                        self._insert_metadata_iptc(k, v)
                    case "credit":
                        self._insert_metadata_iptc('credit', v)
                    case 'license':
                        license_type = v['license_type']
                        creators = ", ".join(v["authors"])
                        self._insert_metadata_xmp('License', self._RIGHTS[license_type]["license_name"], license=True)
                        self._insert_metadata_xmp('AttributionURL', self._RIGHTS[license_type]["license_link"], license=True)
                        self._insert_metadata_xmp('Rights', self._RIGHTS[license_type]["license_text"], license=True)
                        self._insert_metadata_xmp('Creators', creators)
                        license_exif = f'{self._RIGHTS[license_type]["license_name"]}: {self._RIGHTS[license_type]["license_text"]}. {self._RIGHTS[license_type]["license_link"]}'
                        self._insert_metadata_exif('copyright', license_exif.encode())
                        self._insert_metadata_exif('creators', creators.encode())

                    case 'keywords':
                        if len(v) > 0:
                            keywords = []
                            subject = []
                            for k1, v2 in v.items():
                                keywords.append(f'{k1}: {", ".join(v2)}')
                                subject.append(f'{k1}: {", ".join(v2)}')
                            subject = '; '.join(subject)
                            self._insert_metadata_xmp('Subject', subject)
                            self._insert_metadata_iptc(k, keywords)
                    case 'description_pt':
                        self._insert_metadata_exif('image_description', v.encode())
                        self._insert_metadata_xmp('DescriptionPT', v)
                        self._insert_metadata_iptc('caption/abstract', v)
                        
                    case 'title_pt':
                        self._insert_metadata_xmp('TitlePT', v)
                        self._insert_metadata_iptc('object name', v)
                    case 'gps':
                        self._insert_metadata_exif('gps', v)
                        self._insert_metadata_iptc('content location name', f'GPScoordinates: {v}')
                    case 'datetime':
                        self._insert_metadata_iptc('date created', v)
                        self._insert_metadata_xmp('DateCreated', v)
                        self._insert_metadata_exif('datetime', v.encode())
                    case 'country':
                        self._insert_metadata_xmp('Country', v)
                        self._insert_metadata_iptc('country/primary location name', v)
                    case 'state':
                        self._insert_metadata_xmp('State', v)
                        self._insert_metadata_iptc('province/state', v)
                    case 'city':
                        self._insert_metadata_xmp('City', v)
                        self._insert_metadata_iptc('city', v)
                    case 'sublocation':
                        self._insert_metadata_iptc('sub-location', v)

    def _read_iptc(self, field):
        info = IPTCInfo(self.file, force=True)
        meta = info[field]
        if meta == None:
            meta = ''
        return meta
    
    def _read_xmp(self, field):
        try:
            xmpfile = XMPFiles( file_path=self.file)
            xmp = xmpfile.get_xmp()
            if field in 'License AttributionURL':
                meta = xmp.get_property(consts.XMP_NS_CC, field)
            else:
                meta = xmp.get_property(consts.XMP_NS_DC, field)
        except:
            meta = ''
        return meta

    def _read_exif(self, field):
        image = Image.open(self.file)
        try:
            exif_dict = piexif.load(image.info['exif'])
        except:
            return ''
        else:
            if field == 'datetime':
                meta = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
                if meta == '':
                    meta = exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]
                return meta
            try:
                meta = exif_dict[field]
            except:
                meta = ''
            finally:
                if field == 'GPS':
                    gps = meta
                    meta = f"{gps[1].decode()} {gps[2][0][0]}\u00ba{int(gps[2][1][0])}'{int(gps[2][2][0])}\u0022 {gps[3].decode()} {gps[4][0][0]}\u00ba{int(gps[4][1][0])}'{int(gps[4][2][0])}\u0022"
                    print(meta)
                return meta
            
        
    def read_metadata(self):
        keys_metadata = {
            'software': {'exif': piexif.ImageIFD.Software},
            'headline': {'xmp': 'headline', 'iptc': 'headline'},
            'instructions': {'xmp': 'Instructions', 'iptc': 'special instructions'},
            'source': {'iptc': 'source'},
            'credit': {'iptc': 'source'},
            'license_name': {'xmp': 'License'},
            'license_link': {'xmp': 'AttributionURL'},
            'license_text': {'xmp': 'Rights'},
            'copyright': {'exif': piexif.ImageIFD.Copyright},
            'keywords': {'xmp': 'subject', 'iptc': 'keywords'},
            'creator': {'exif': piexif.ImageIFD.Artist, 'xmp': 'Creator', 'iptc': 'Creator'},
            'title_pt': {'xmp': 'TitlePT', 'iptc': 'object name'},
            'description_pt': {'exif': piexif.ImageIFD.ImageDescription,'xmp': 'DescriptionPT', 'iptc': 'caption/abstract'},
            'gps': {'exif': 'GPS', 'iptc': 'content location name'},
            'datetime': {'xmp': 'date_created', 'iptc': 'DateCreated', 'exif': 'datetime'},
            'country': {'xmp': 'Country', 'iptc': 'country/primary location name'},
            'state': {'xmp': 'State', 'iptc': 'province/state'},
            'city': {'xmp': 'City', 'iptc': 'city'},
            'sublocation': {'iptc': 'sub-location'}
        }
        
        metadata = {k: '' for k in keys_metadata.keys()}
        for meta_type in ['xmp', 'iptc', 'exif']:
            for k, v in keys_metadata.items():
                if metadata[k] == '' or metadata[k] == None:
                    try:
                        if meta_type == 'xmp':
                            meta = self._read_xmp(v[meta_type])
                        elif meta_type == 'iptc':
                            meta = self._read_iptc(v[meta_type])
                        elif meta_type == 'exif':
                            meta = self._read_exif(v[meta_type])
                        
                        try:
                            if type(meta) == list:
                                for i, m in enumerate(meta):
                                    meta[i] = m.decode(errors='ignore')
                            else:
                                meta = meta.decode(errors='ignore')
                        except AttributeError:
                            pass
                        metadata[k] = meta
                        if k == 'datetime':
                            print(meta)
                            print(meta_type)
                        
                    except KeyError:
                        pass
        return metadata