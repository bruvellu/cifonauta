#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CIFONAUTA
# Copyleft 2010 - Bruno C. Vellutini | organelas.ccom
#
#TODO Definir licença.
#
# Atualizado: 09 Oct 2010 03:09AM
'''Gerenciador do banco de imagens do CEBIMar-USP.

Este programa gerencia os arquivos do banco de imagens do CEBIMar lendo seus
metadados, reconhecendo marquivos modificados e atualizando o website.

Centro de Biologia Marinha da Universidade de São Paulo.
'''

import os
import sys
import subprocess
import time
import getopt
import pickle

from datetime import datetime
from shutil import copy
from iptcinfo import IPTCInfo
import pyexiv2

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.8'
__maintainer__ = 'Bruno Vellutini'
__email__ = 'organelas at gmail dot com'
__status__ = 'Development'

# Diretório com os arquivos 
source_dir = u'source_media'
# Arquivo com marca d'água
watermark = u'marca.png'


class Database:
    '''Define objeto que interage com o banco de dados.'''
    def __init__(self):
        pass

    def search_db(self, media):
        '''Busca o registro no banco de dados pelo nome do arquivo.
        
        Se encontrar, compara a data de modificação do arquivo e do registro.
        Se as datas forem iguais pula para próximo arquivo, se forem diferentes
        atualiza o registro.
        '''
        print '\nVerificando se o arquivo está no banco de dados...'
        
        try :
            if media.type == "photo":
                record = Image.objects.get(web_filepath__icontains=media.filename)
            elif media.type == "video":
                try:
                    record = Video.objects.get(
                            webm_filepath__icontains=media.filename.split('.')[0])
                except:
                    try:
                        record = Video.objects.get(mp4_filepath__icontains=media.filename.split('.')[0])
                    except:
                        try:
                            record = Video.objects.get(ogg_filepath__icontains=media.filename.split('.')[0])
                        except:
                            print 'Não bateu nenhum!'
                            return False
            print 'Bingo! Registro de %s encontrado.' % media.filename
            print 'Comparando a data de modificação do arquivo com o registro...'
            if record.timestamp != media.timestamp:
                print 'Arquivo mudou!'
                return 1
            else:
                print 'Arquivo não mudou!'
                return 2
        except Image.DoesNotExist:
            print 'Registro não encontrado.'
            return False

    def update_db(self, media, update=False):
        '''Cria ou atualiza registro no banco de dados.'''
        print '\nAtualizando o banco de dados...'
        # Instancia metadados pra não dar conflito.
        media_meta = media.meta
        print media_meta
        # Guarda objeto com infos taxonômicas
        taxa = media_meta['taxon']
        del media_meta['taxon']
        genus_sp = media_meta['genus_sp']
        del media_meta['genus_sp']
        # Guarda objeto com autores
        authors = media_meta['author']
        # Guarda objeto com tags
        tags = media_meta['tags']
        del media_meta['tags']

        # Não deixar entrada pública se faltar título ou autor
        if media_meta['title'] == '' or not media_meta['author']:
            print 'Mídia sem título ou autor!'
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Deleta para inserir autores separadamente.
        del media_meta['author']

        # Transforma valores em instâncias dos modelos
        toget = ['size', 'source', 'rights', 'sublocation',
                'city', 'state', 'country']
        for k in toget:
            media_meta[k] = self.get_instance(k, media_meta[k])
            print k, media_meta[k].id, media_meta[k]

        if not update:
            media_meta['view_count'] = 0
            if media.type == 'photo':
                entry = Image(**media_meta)
            elif media.type == 'video':
                entry = Video(**media_meta)
            # Tem que salvar para criar id, usado na hora de salvar as tags
            entry.save()
        else:
            if media.type == 'photo':
                entry = Image.objects.get(web_filepath__icontains=media.filename)
            elif media.type == 'video':
                entry = Video.objects.get(webm_filepath__icontains=media.filename.split('.')[0])
            for k, v in media_meta.iteritems():
                setattr(entry, k, v)

        # Atualiza autores
        entry = self.update_sets(entry, 'author', authors)

        # Atualiza táxons
        entry = self.update_sets(entry, 'taxon', taxa)
        
        # Atualiza gêneros e espécies
        genera = []
        spp = []
        for binomius in genus_sp:
            # Faz o link entre espécie e gênero
            sp = self.get_instance('species', binomius['sp'])
            sp.parent = self.get_instance('genus', binomius['genus'])
            sp.save()
            genera.append(binomius['genus'])
            spp.append(binomius['sp'])
        entry = self.update_sets(entry, 'genus', genera)
        entry = self.update_sets(entry, 'species', spp)

        # Atualiza marcadores
        entry = self.update_sets(entry, 'tag', tags)

        # Salvando modificações
        entry.save()

        print 'Registro no banco de dados atualizado!'

    def get_instance(self, table, value):
        '''Retorna o id a partir do nome.'''
        metadatum, new = eval('%s.objects.get_or_create(name="%s")' %
                (table.capitalize(), value))
        return metadatum

    def update_sets(self, entry, field, meta):
        '''Atualiza campos many to many do banco de dados.'''
        meta_instances = [self.get_instance(field, value) for value in meta]
        eval('entry.%s_set.clear()' % field)
        [eval('entry.%s_set.add(value)' % field) for value in meta_instances]
        return entry


class Movie:
    '''Define objetos para instâncias dos vídeos.'''
    def __init__(self, filepath):
        self.source_filepath = filepath
        self.filename = os.path.basename(filepath)
        self.timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.type = 'video'

        # Diretórios
        self.site_dir = u'site_media/videos'
        self.site_thumb_dir = u'site_media/videos/thumbs'
        self.local_dir = u'local_media/videos'
        self.local_thumb_dir = u'local_media/videos/thumbs'

        # Verifica existência dos diretórios.
        dir_ready(self.site_dir, self.site_thumb_dir,
                self.local_dir, self.local_thumb_dir)

    def create_meta(self, charset='utf-8'):
        '''Define as variáveis dos metadados do vídeo.'''
        print 'Lendo os metadados de %s e criando variáveis.' % self.filename
        #TODO Incorporar leitura de metadados e delegação dos valores.
        # Testar com o ffmpeg, arquivo de texto, etc.

        self.meta = {
                'source_filepath': os.path.abspath(self.source_filepath),
                'timestamp': self.timestamp,
                'title': u'',
                'tags': u'',
                'author': u'',
                'city': u'',
                'sublocation': u'',
                'state': u'',
                'country': u'',
                'taxon': u'',
                'rights': u'',
                'caption': u'',
                'genus_sp': u'',
                'size': u'',
                'source': u'',
                'date': '1900-01-01 01:01:01',
                'geolocation': u'',
                'latitude': u'',
                'longitude': u''
                }

        text_path = self.source_filepath.split('.')[0] + '.txt'
        try:
            meta_text = open(text_path, 'rb')
            print 'Arquivo de info existe!'
        except:
            meta_text = ''

        print self.meta
        if meta_text:
            meta_dic = pickle.load(meta_text)
            meta_text.close()
        self.meta.update(meta_dic)
        print self.meta

        #TODO incluir filepath de arquivos e thumbs no meta
        web_paths, thumb_filepath, large_thumb = self.process_video()
        print web_paths

        # Prepara alguns campos para banco de dados
        self.meta = prepare_meta(self.meta)

        for k, v in web_paths.iteritems():
            self.meta[k] = v
        self.meta['thumb_filepath'] = thumb_filepath
        self.meta['large_thumb'] = large_thumb

        return self.meta

    def process_video(self):
        '''Redimensiona o vídeo, inclui marca d'água e comprime.'''
        print '\nProcessando o vídeo...'
        web_paths = {}
        try:
            try:
                # WebM
                webm_name = self.filename.split('.')[0] + '.webm'
                webm_filepath = os.path.join(self.local_dir, webm_name)
                subprocess.call([
                    'ffmpeg', '-y', '-i', self.source_filepath, '-aspect',
                    '4:3', '-metadata', 'title="%s"' % self.meta['title'],
                    '-metadata', 'author="%s"' % self.meta['author'], '-s',
                    '480x360', '-pass', '1', '-vcodec', 'libvpx', '-b', '300k',
                    '-g', '15', '-bf', '2', '-vpre', 'veryslow_firstpass',
                    '-threads', '2', webm_filepath])
                subprocess.call(['ffmpeg', '-y', '-i', self.source_filepath,
                    '-aspect', '4:3', '-metadata', 'title="%s"' %
                    self.meta['title'], '-metadata', 'author="%s"' %
                    self.meta['author'], '-s', '480x360', '-pass', '2',
                    '-vcodec', 'libvpx', '-b', '300k', '-g', '15', '-bf', '2',
                    '-vpre', 'veryslow', '-acodec', 'libvorbis', '-ab', '128k',
                    '-ar', '44100', '-threads', '2', webm_filepath])
                try:
                    # Copia imagem para pasta web
                    webm_site_filepath = os.path.join(self.site_dir, webm_name)
                    copy(webm_filepath, webm_site_filepath)
                except:
                    print 'Não conseguiu copiar para o site.'
                web_paths['webm_filepath'] = webm_site_filepath
            except:
                print 'Processamento do WebM não funcionou!'
            try:
                # MP4
                mp4_name = self.filename.split('.')[0] + '.mp4' 
                mp4_filepath = os.path.join(self.local_dir, mp4_name)
                subprocess.call([
                    'ffmpeg', '-y', '-i', self.source_filepath, '-aspect',
                    '4:3', '-metadata', 'title="%s"' % self.meta['title'],
                    '-metadata', 'author="%s"' % self.meta['author'], '-s',
                    '480x360', '-pass', '1', '-vcodec', 'libx264', '-b', '300k',
                    '-g', '15', '-bf', '2', '-vpre', 'veryslow_firstpass',
                    '-threads', '2', mp4_filepath])
                subprocess.call(['ffmpeg', '-y', '-i', self.source_filepath,
                    '-aspect', '4:3', '-metadata', 'title="%s"' %
                    self.meta['title'], '-metadata', 'author="%s"' %
                    self.meta['author'], '-s', '480x360', '-pass', '2',
                    '-vcodec', 'libx264', '-b', '300k', '-g', '15', '-bf', '2',
                    '-vpre', 'veryslow', '-acodec', 'libfaac', '-ab', '128k',
                    '-ar', '44100', '-threads', '2', mp4_filepath])
                try:
                    # Copia imagem para pasta web
                    mp4_site_filepath = os.path.join(self.site_dir, mp4_name)
                    copy(mp4_filepath, mp4_site_filepath)
                except:
                    print 'Não conseguiu copiar para o site.'
                web_paths['mp4_filepath'] = mp4_site_filepath
            except:
                print 'Processamento do x264 não funcionou!'
            try:
                # OGG
                ogg_name = self.filename.split('.')[0] + '.ogv' 
                ogg_filepath = os.path.join(self.local_dir, ogg_name)
                subprocess.call([
                    'ffmpeg', '-y', '-i', self.source_filepath, '-aspect',
                    '4:3', '-metadata', 'title="%s"' % self.meta['title'],
                    '-metadata', 'author="%s"' % self.meta['author'], '-s',
                    '480x360', '-pass', '1', '-vcodec', 'libtheora', '-b', '300k',
                    '-g', '15', '-bf', '2', '-vpre', 'veryslow_firstpass',
                    '-threads', '2', ogg_filepath])
                subprocess.call(['ffmpeg', '-y', '-i', self.source_filepath,
                    '-aspect', '4:3', '-metadata', 'title="%s"' %
                    self.meta['title'], '-metadata', 'author="%s"' %
                    self.meta['author'], '-s', '480x360', '-pass', '2',
                    '-vcodec', 'libtheora', '-b', '300k', '-g', '15', '-bf',
                    '2', '-vpre', 'veryslow', '-acodec', 'libvorbis', '-ab',
                    '128k', '-ar', '44100', '-threads', '2', ogg_filepath])
                try:
                    # Copia imagem para pasta web
                    ogg_site_filepath = os.path.join(self.site_dir, ogg_name)
                    copy(ogg_filepath, ogg_site_filepath)
                except:
                    print 'Não conseguiu copiar para o site.'
                web_paths['ogg_filepath'] = ogg_site_filepath
            except:
                print 'Processamento do OGG não funcionou!'

            #TODO qt-faststart input.foo output.foo

        except IOError:
            print '\nOcorreu algum erro na conversão da imagem. Verifique se o ' \
                    'ImageMagick está instalado.'
        else:
            print 'Vídeos convertidos com sucessos! Criando thumbnails...'
            thumb_filepath, large_thumb_filepath = self.create_thumbs()
            return web_paths, thumb_filepath, large_thumb_filepath


    def create_thumbs(self):
        '''Cria thumbnails para os novos vídeos.'''
        # Troca extensão para png.
        thumbname = self.filename.split('.')[0] + '.png'
        large_thumbname = self.filename.split('.')[0] + '.jpg'
        # Define caminho para pasta local.
        local_filepath = os.path.join(self.local_thumb_dir, thumbname)
        local_filepath_large = os.path.join(self.local_thumb_dir, large_thumbname)
        try:
            # Cria thumb grande a partir de 1 frame no segundo 5
            subprocess.call(['ffmpeg', '-i', self.source_filepath,
                '-vframes', '1', '-s', '480x360', '-ss', '5', '-f',
                'image2', local_filepath_large])
            # Cria thumb normal (pequeno)
            subprocess.call(['convert', '-define', 'jpeg:size=200x150',
                local_filepath_large, '-thumbnail', '120x90^', '-gravity',
                'center', '-extent', '120x90', 'PNG8:%s' % local_filepath])
        except IOError:
            #TODO Criar entrada no log.
            print 'Não consegui criar o thumbnail...'
        # Copia thumbs da pasta local para site
        copy(local_filepath, self.site_thumb_dir)
        copy(local_filepath_large, self.site_thumb_dir)
        # Define caminho para o thumb do site.
        site_filepath = os.path.join(self.site_thumb_dir, thumbname)
        site_filepath_large = os.path.join(self.site_thumb_dir, large_thumbname)
        return site_filepath, site_filepath_large

class Photo:
    '''Define objeto para instâncias das fotos.'''
    def __init__(self, filepath):
        self.source_filepath = filepath
        self.filename = os.path.basename(filepath)
        self.timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
        self.type = 'photo'

        # Diretórios
        self.site_dir = u'site_media/photos'
        self.site_thumb_dir = u'site_media/photos/thumbs'
        self.local_dir = u'local_media/photos'
        self.local_thumb_dir = u'local_media/photos/thumbs'

        # Verifica existência dos diretórios.
        dir_ready(self.site_dir, self.site_thumb_dir,
                self.local_dir, self.local_thumb_dir)

    def create_meta(self, charset='utf-8'):
        '''Define as variáveis extraídas dos metadados da imagem.

        Usa a biblioteca do arquivo iptcinfo.py para padrão IPTC e pyexiv2 para EXIF.
        '''
        print 'Lendo os metadados de %s e criando variáveis.' % self.filename
        # Criar objeto com metadados
        info = IPTCInfo(self.source_filepath, True, charset)
        # Checando se o arquivo tem dados IPTC
        if len(info.data) < 4:
            print '%s não tem dados IPTC!' % self.filename

        self.meta = {
                'source_filepath': os.path.abspath(self.source_filepath),
                'title': info.data['object name'], # 5
                'tags': info.data['keywords'], # 25
                'author': info.data['by-line'], # 80
                'city': info.data['city'], # 90
                'sublocation': info.data['sub-location'], # 92
                'state': info.data['province/state'], # 95
                'country': info.data['country/primary location name'], # 101
                'taxon': info.data['headline'], # 105
                'rights': info.data['copyright notice'], # 116
                'caption': info.data['caption/abstract'], # 120
                'genus_sp': info.data['original transmission reference'], # 103
                'size': info.data['special instructions'], # 40
                'source': info.data['source'], # 115
                'timestamp': self.timestamp,
                }

        # Prepara alguns campos para banco de dados
        self.meta = prepare_meta(self.meta)
                
        # Extraindo metadados do EXIF
        exif = self.get_exif(self.source_filepath)
        date = self.get_date(exif)
        if date and not date == '0000:00:00 00:00:00':
            self.meta['date'] = date
        else:
            self.meta['date'] = '1900-01-01 01:01:01'
        # Arrumando geolocalização
        try:
            gps = self.get_gps(exif)
            for k, v in gps.iteritems():
                self.meta[k] = v
        except:
            self.meta['geolocation'] = ''
            self.meta['latitude'] = ''
            self.meta['longitude'] = ''

        # Processar imagem
        web_filepath, thumb_filepath = self.process_image()
        self.meta['web_filepath'] = web_filepath
        self.meta['thumb_filepath'] = thumb_filepath

        print
        print '\tVariável\tMetadado'
        print '\t' + 40 * '-'
        print '\t' + self.meta['web_filepath']
        print '\t' + self.meta['thumb_filepath']
        print '\t' + 40 * '-'
        print '\tTítulo:\t\t%s' % self.meta['title']
        print '\tDescrição:\t%s' % self.meta['caption']
        print '\tEspécie:\t%s' % self.meta['genus_sp']
        print '\tTáxon:\t\t%s' % self.meta['taxon']
        print '\tTags:\t\t%s' % '\n\t\t\t'.join(self.meta['tags'])
        print '\tTamanho:\t%s' % self.meta['size']
        print '\tEspecialista:\t%s' % self.meta['source']
        print '\tAutor:\t\t%s' % self.meta['author']
        print '\tSublocal:\t%s' % self.meta['sublocation']
        print '\tCidade:\t\t%s' % self.meta['city']
        print '\tEstado:\t\t%s' % self.meta['state']
        print '\tPaís:\t\t%s' % self.meta['country']
        print '\tDireitos:\t%s' % self.meta['rights']
        print '\tData:\t\t%s' % self.meta['date']
        print
        print '\tGeolocalização:\t%s' % self.meta['geolocation']
        print '\tDecimal:\t%s, %s' % (self.meta['latitude'],
                self.meta['longitude'])

        return self.meta

    def get_exif(self, filepath):
        '''Extrai o exif da imagem selecionada usando o pyexiv2 0.2.2.'''
        exif_meta = pyexiv2.ImageMetadata(filepath)
        exif_meta.read()
        return exif_meta

    def get_gps(self, exif):
        '''Extrai coordenadas guardadas no EXIF.'''
        gps = {}
        gps_data = {}
        # Latitude
        gps['latref'] = exif['Exif.GPSInfo.GPSLatitudeRef'].value
        gps['latdeg'] = self.resolve(exif['Exif.GPSInfo.GPSLatitude'].value[0])
        gps['latmin'] = self.resolve(exif['Exif.GPSInfo.GPSLatitude'].value[1])
        gps['latsec'] = self.resolve(exif['Exif.GPSInfo.GPSLatitude'].value[2])
        latitude = self.get_decimal(
                gps['latref'], gps['latdeg'], gps['latmin'], gps['latsec'])
        # Longitude
        gps['longref'] = exif['Exif.GPSInfo.GPSLongitudeRef'].value
        gps['longdeg'] = self.resolve(exif['Exif.GPSInfo.GPSLongitude'].value[0])
        gps['longmin'] = self.resolve(exif['Exif.GPSInfo.GPSLongitude'].value[1])
        gps['longsec'] = self.resolve(exif['Exif.GPSInfo.GPSLongitude'].value[2])
        longitude = self.get_decimal(
                gps['longref'], gps['longdeg'], gps['longmin'], gps['longsec'])

        # Gravando valores prontos
        gps_data['geolocation'] = '%s %d°%d\'%d" %s %d°%d\'%d"' % (
                gps['latref'], gps['latdeg'], gps['latmin'], gps['latsec'],
                gps['longref'], gps['longdeg'], gps['longmin'], gps['longsec'])
        gps_data['latitude'] = '%f' % latitude
        gps_data['longitude'] = '%f' % longitude
        return gps_data

    def get_decimal(self, ref, deg, min, sec):
        '''Descobre o valor decimal das coordenadas.'''
        decimal_min = (min * 60.0 + sec) / 60.0
        decimal = (deg * 60.0 + decimal_min) / 60.0
        negs = ['S', 'W']
        if ref in negs:
            decimal = -decimal
        return decimal

    def resolve(self, frac):
        '''Resolve a fração das coordenadas para int.

        Por padrão os valores do exif são guardados como frações. Por isso é
        necessário converter.
        '''
        fraclist = str(frac).split('/')
        result = int(fraclist[0]) / int(fraclist[1])
        return result

    def get_date(self, exif):
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

    def process_image(self):
        '''Redimensiona a imagem e inclui marca d'água.'''
        local_filepath = os.path.join(self.local_dir, self.filename)
        print '\nProcessando a imagem...'
        try:
            # Converte para 72dpi, JPG qualidade 50 e redimensiona as imagens
            # maiores que 640 (em altura ou largura)
            subprocess.call(['convert', self.source_filepath, '-density', '72', '-format', 'jpg',
                '-quality', '50', '-resize', '640x640>', local_filepath])
            # Insere marca d'água no canto direito embaixo
            subprocess.call(['composite', '-dissolve', '20', '-gravity',
                'southeast', watermark, local_filepath, local_filepath])
            # Copia imagem para pasta web
            #XXX Melhorar isso de algum jeito...
            web_filepath = os.path.join(self.site_dir, self.filename)
            copy(local_filepath, web_filepath)
        except IOError:
            print '\nOcorreu algum erro na conversão da imagem. Verifique se o ' \
                    'ImageMagick está instalado.'
        else:
            print 'Imagem convertida com sucesso! Criando thumbnails...'
            thumb_filepath = self.create_thumbs()
            return web_filepath, thumb_filepath

    def create_thumbs(self):
        '''Cria thumbnails para as fotos novas.'''
        # Define nome do thumbnail.
        thumbname = self.filename.split('.')[0] + '.png'
        # Define caminho para pasta local.
        local_filepath = os.path.join(self.local_thumb_dir, thumbname)
        try:
            # Convocando o ImageMagick
            subprocess.call(['convert', '-define', 'jpeg:size=200x150',
                self.source_filepath, '-thumbnail', '120x90^', '-gravity', 'center',
                '-extent', '120x90', 'PNG8:%s' % local_filepath])
        except IOError:
            #TODO Criar entrada no log.
            print 'Não consegui criar o thumbnail...'
        # Copia thumb da pasta local para site_media.
        copy(local_filepath, self.site_thumb_dir)
        # Define caminho para o thumb do site.
        site_filepath = os.path.join(self.site_thumb_dir, thumbname)
        return site_filepath


class Folder:
    '''Classes de objetos para lidar com as pastas e seus arquivos.'''
    def __init__(self, folder, n_max):
        self.folder_path = folder
        self.n_max = n_max
        self.files = []

    def get_files(self):
        '''Busca recursivamente arquivos de uma pasta.
        
        Identifica a extensão do arquivo e salva tipo junto com o caminho.
        Retorna lista de tuplas com caminho e tipo.
        '''
        n = 0
        # Tuplas para o endswith()
        photo_extensions = ('jpg', 'JPG', 'jpeg', 'JPEG')
        video_extensions = ('avi', 'AVI', 'mov', 'MOV', 'mp4', 'MP4', 'ogg', 'OGG', 'ogv', 'OGV', 'dv', 'DV', 'mpg', 'MPG', 'mpeg', 'MPEG', 'flv', 'FLV')
        ignore_extensions = ('~')
        # Buscador de arquivos em ação
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if filename.endswith(photo_extensions) and n < self.n_max:
                    filepath = os.path.join(root, filename)
                    self.files.append((filepath, 'photo'))
                    n += 1
                    continue
                if filename.endswith(video_extensions) and n < self.n_max:
                    filepath = os.path.join(root, filename)
                    self.files.append((filepath, 'video'))
                    n += 1
                    continue
                elif filename.endswith(ignore_extensions):
                    print 'Ignorando %s' % filename
                    continue
            else:
                print 'Nome do último arquivo: %s' % filename
                break
        else:
            print '\n%d arquivos encontrados.' % n

        return self.files


# Funções principais

def prepare_meta(meta):
    '''Processa as strings dos metadados convertendo para bd.
    
    Transforma None em string vazia, transforma autores e táxons em lista,
    espécies em dicionário.
    '''
    # Converte valores None para string em branco
    for k, v in meta.iteritems():
        if v is None:
            meta[k] = u''

    # Preparando autor(es) para o banco de dados
    meta['author'] = [a.strip() for a in meta['author'].split(',')] 
    # Preparando taxon(s) para o banco de dados
    meta['taxon'] = [a.strip() for a in meta['taxon'].split(',')] 

    # Preparando a espécie para o banco de dados
    spp_diclist = []
    genera_spp = [i.strip() for i in meta['genus_sp'].split(',')]
    for genus_sp in genera_spp:
        if genus_sp:
            bilist = genus_sp.split()
            if len(bilist) == 1 and bilist[0] != '':
                spp_diclist.append({'genus': bilist[0], 'sp': ''})
            elif len(bilist) == 2:
                if bilist[1] in ['sp.', 'sp', 'spp']:
                    bilist[1] = ''
                spp_diclist.append({'genus': bilist[0], 'sp': bilist[1]})
    meta['genus_sp'] = spp_diclist

    return meta

def dir_ready(*dirs):
    '''Verifica se o diretório existe, criando caso não exista.'''
    for dir in dirs:
        if os.path.isdir(dir) is False:
            print 'Criando diretório inexistente...'
            os.mkdir(dir)

def usage():
    '''Imprime manual de uso e argumentos disponíveis.'''
    print
    print 'Comando básico:'
    print '  python cifonauta.py [args]'
    print
    print 'Argumentos:'
    print '  -h, --help'
    print '\tMostra este menu de ajuda.'
    print
    print '  -n {n}, --n-max {n} (padrão=20)'
    print '\tEspecifica um número máximo de arquivos que o programa irá ' \
            'verificar.'
    print
    print '  -f, --force-update'
    print '\tAtualiza banco de dados e refaz thumbnails de todas as entradas, '
    print '\tinclusive as que não foram modificadas.'
    print
    print 'Exemplo:'
    print '  python cifonauta.py -f -n 15'
    print '\tFaz a atualização forçada dos primeiros 15 arquivos que o programa'
    print '\tencontrar na pasta padrão (source_media; ver código).'
    print

def main(argv):
    ''' Função principal do programa.
    
    Lê os argumentos se houver e chama as outras funções.
    '''
    n = 0
    n_new = 0
    n_up = 0
    # Valores padrão para argumentos
    force_update = False
    n_max = 20
    web_upload = False
    single_img = False

    # Verifica se argumentos foram passados com a execução do programa
    try:
        opts, args = getopt.getopt(argv, 'hfn:', [
            'help',
            'force-update',
            'n='])
    except getopt.GetoptError:
        print 'Algo de errado nos argumentos...'
        usage()
        sys.exit(2)
    
    # Define o que fazer de acordo com o argumento passado
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-n', '--n-max'):
            n_max = int(arg)
        elif opt in ('-f', '--force-update'):
            force_update = True
    
    # Imprime resumo do que o programa vai fazer
    if force_update is True:
        print '\n%d arquivos serão atualizadas de forma forçada.' % n_max
        print '(argumento "-f" utilizado)'
    else:
        print '\n%d arquivos serão verificadas e registradas no banco de ' \
                'dados.' % n_max

    # Cria o arquivo log
    logname = 'log_%s' % time.strftime('%Y.%m.%d_%I:%M:%S', time.localtime())
    log = open(logname, 'a+b')

    # Cria instância do bd
    cbm = Database()

    # Inicia o cifonauta buscando pasta...
    folder = Folder(source_dir, n_max)
    filepaths = folder.get_files()
    for path in filepaths:
        # Reconhece se é foto ou vídeo
        if path[1] == 'photo':
            media = Photo(path[0])
        elif path[1] == 'video':
            media = Movie(path[0])
        # Busca nome do arquivo no banco de dados
        query = cbm.search_db(media)
        if not query:
            # Se mídia for nova
            print '\nARQUIVO NOVO, CRIANDO ENTRADA NO BANCO DE DADOS...'
            media.create_meta()
            cbm.update_db(media)
            n_new += 1
        else:
            if not force_update and query == 2:
                # Se registro existir e timestamp for igual
                print '\nREGISTRO EXISTE E ESTÁ ATUALIZADO NO SITE! ' \
                        'PRÓXIMO ARQUIVO...'
                pass
            else:
                # Se arquivo do site não estiver atualizada
                if force_update:
                    print '\nREGISTRO EXISTE E ESTÁ ATUALIZADO, MAS '\
                            'RODANDO SOB ARGUMENTO "-f".'
                else:
                    print '\nREGISTRO EXISTE, MAS NÃO ESTÁ ATUALIZADO. ' \
                            'ATUALIZANDO O BANCO DE DADOS...'
                media.create_meta()
                cbm.update_db(media, update=True)
                n_up += 1
    n = len(filepaths)
    
    # Deletando arquivo log se ele estiver vazio
    if log.read(1024) == '':
        log.close()
        # Deletando log vazio
        os.remove(logname)
    else:
        # Fechando arquivo de log
        log.close()
    
    print '\n%d ARQUIVOS ANALISADOS' % n
    print '%d novos' % n_new
    print '%d atualizados' % n_up
    t = int(time.time() - t0)
    if t > 60:
        print '\nTempo de execução:', t / 60, 'min', t % 60, 's'
    else:
        print '\nTempo de execução:', t, 's'
    print

# Início do programa
if __name__ == '__main__':
    # Marca a hora inicial
    t0 = time.time()
    # Inicia função principal, lendo os argumentos (se houver)
    main(sys.argv[1:])
