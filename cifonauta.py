#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CIFONAUTA
# Copyleft 2010 - Bruno C. Vellutini | organelas.com
#
#TODO Definir licença.
#
# Atualizado: 16 Feb 2011 01:09AM
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
import random

from datetime import datetime
from shutil import copy
from iptcinfo import IPTCInfo
import pyexiv2

from itis import Itis
import linking

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.8.5'
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
        photopath = 'photos/'
        videopath = 'videos/'

        try:
            if media.type == "photo":
                # Busca pelo nome exato do arquivo, para evitar confusão.
                record = Image.objects.get(web_filepath=photopath + media.filename)
            elif media.type == "video":
                try:
                    record = Video.objects.get(webm_filepath=videopath + media.filename.split('.')[0] + '.webm')
                except:
                    try:
                        record = Video.objects.get(mp4_filepath=videopath + media.filename.split('.')[0] + '.mp4')
                    except:
                        try:
                            record = Video.objects.get(ogg_filepath=videopath + media.filename.split('.')[0] + '.ogv')
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
        # Guarda objeto com infos taxonômicas.
        taxa = media_meta['taxon']
        del media_meta['taxon']
        # Prevenção contra extinto campo de espécie.
        try:
            del media_meta['genus_sp']
        except:
            pass
        # Guarda objeto com autores
        authors = media_meta['author']
        # Guarda objeto com especialistas 
        sources = media_meta['source']
        del media_meta['source']
        # Guarda objeto com tags
        tags = media_meta['tags']
        del media_meta['tags']
        # Guarda objeto com referências
        refs = media_meta['references']
        del media_meta['references']

        # Não deixar entrada pública se faltar título ou autor
        if media_meta['title'] == '' or not media_meta['author']:
            print 'Mídia sem título ou autor!'
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Deleta para inserir autores separadamente.
        del media_meta['author']

        # Transforma valores em instâncias dos modelos
        toget = ['size', 'rights', 'sublocation',
                'city', 'state', 'country']
        for k in toget:
            print '\nK'
            print '\nMETA (%s): %s' % (k, media_meta[k])
            # Apenas criar se não estiver em branco.
            if media_meta[k]:
                media_meta[k] = self.get_instance(k, media_meta[k])
                print 'INSTANCES FOUND: %s' % media_meta[k] 
                print 'INSTANCES ADDED.'
            else:
                del media_meta[k]

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

        # Atualiza especialistas
        entry = self.update_sets(entry, 'source', sources)

        # Atualiza táxons
        entry = self.update_sets(entry, 'taxon', taxa)

        # Atualiza marcadores
        entry = self.update_sets(entry, 'tag', tags)

        # Atualiza referências
        entry = self.update_sets(entry, 'reference', refs)

        # Salvando modificações
        entry.save()

        print 'Registro no banco de dados atualizado!'

    def get_instance(self, table, value):
        '''Retorna o id a partir do nome.'''
        metadatum, new = eval('%s.objects.get_or_create(name="%s")' %
                (table.capitalize(), value))
        if table == 'taxon' and new:
            # Consulta ITIS para extrair táxons.
            taxon = self.get_itis(value)
            # Reforça, caso a conexão falhe.
            if not taxon:
                taxon = self.get_itis(value)
                if not taxon:
                    print u'Nova tentativa em 5s...'
                    time.sleep(5)
                    taxon = self.get_itis(value)
            try:
                # Pega a lista de pais e cria táxons, na ordem reversa.
                for parent in taxon.parents:
                    print u'Criando %s...' % parent.taxonName
                    newtaxon, new = Taxon.objects.get_or_create(name=parent.taxonName)
                    if new:
                        newtaxon.rank = parent.rankName
                        newtaxon.tsn = parent.tsn
                        if parent.parentName:
                            newtaxon.parent = Taxon.objects.get(name=parent.parentName)
                        newtaxon.save()
                        print u'Salvo!'
                    else:
                        print u'Já existe!'

                if taxon.parent_name:
                    # Ordem reversa acima garante que ele já existe.
                    metadatum.parent = Taxon.objects.get(name=taxon.parent_name)
                if taxon.tsn:
                    metadatum.tsn = taxon.tsn
                if taxon.rank:
                    metadatum.rank = taxon.rank
            except:
                print u'Não rolou pegar hierarquia...'

            metadatum.save()
        return metadatum

    def update_sets(self, entry, field, meta):
        '''Atualiza campos many to many do banco de dados.

        Verifica se o value não está em branco, para não adicionar entradas em
        branco no banco.
        '''
        print '\nMETA (%s): %s' % (field, meta)
        meta_instances = [self.get_instance(field, value) for value in meta if value.strip()]
        print 'INSTANCES FOUND: %s' % meta_instances
        eval('entry.%s_set.clear()' % field)
        [eval('entry.%s_set.add(value)' % field) for value in meta_instances if meta_instances]
        print 'INSTANCES ADDED.'
        return entry

    def get_itis(self, name):
        '''Consulta banco de dados do ITIS.

        Extrai o táxon pai e o ranking. Valores são guardados em:

        taxon.name
        taxon.rank
        taxon.tsn
        taxon.parent
        taxon.parent_rank
        taxon.parent_tsn
        '''
        try:
            taxon = Itis(name)
        except:
            return None
        return taxon


class Movie:
    '''Define objetos para instâncias dos vídeos.'''
    def __init__(self, filepath):
        self.source_filepath = filepath
        self.filename = os.path.basename(filepath)
        self.type = 'video'

        # Checa para ver qual timestamp é mais atual, o arquivo de vídeo ou o
        # arquivo acessório com os metadados.
        try:
            file_timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
            meta_timestamp = datetime.fromtimestamp(
                    os.path.getmtime(filepath.split('.')[0] + '.txt'))
            if file_timestamp > meta_timestamp:
                self.timestamp = file_timestamp
            else:
                self.timestamp = meta_timestamp
        except:
            self.timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))

        # Diretórios
        self.site_dir = u'site_media/videos'
        self.site_thumb_dir = u'site_media/videos/thumbs'
        self.local_dir = u'local_media/videos'
        self.local_thumb_dir = u'local_media/videos/thumbs'

        # Verifica existência dos diretórios.
        dir_ready(self.site_dir, self.site_thumb_dir,
                self.local_dir, self.local_thumb_dir)

    def create_meta(self, new=False):
        '''Define as variáveis dos metadados do vídeo.'''
        print 'Lendo os metadados de %s e criando variáveis.' % self.filename
        # Limpa metadados pra não misturar com o anterior.
        self.meta = {}
        self.meta = {
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
                #'genus_sp': u'',
                'size': u'',
                'source': u'',
                'date': '1900-01-01 01:01:01',
                'geolocation': u'',
                'latitude': u'',
                'longitude': u'',
                'references': u'',
                'notes': u'',
                }

        # Verifica se arquivo acessório com meta dos vídeos existe.
        try:
            linked_to = os.readlink(self.source_filepath)
            txt_path = linked_to.split('.')[0] + '.txt'
            meta_text = open(txt_path, 'rb')
            print 'Arquivo de info existe!'
        except:
            print 'Arquivo de info não existe!'
            meta_text = ''

        #import pdb; pdb.set_trace()

        if meta_text:
            meta_dic = pickle.load(meta_text)
            meta_text.close()
            # Atualiza meta com valores do arquivo acessório.
            self.meta.update(meta_dic)

        # Inicia processo de renomear arquivo. 
        if new:
            # Adiciona o antigo caminho aos metadados.
            self.meta['old_filepath'] = os.path.abspath(self.source_filepath)
            new_filename = rename_file(self.filename, self.meta['author'])
            # Atualiza media object.
            self.source_filepath = os.path.join(
                    os.path.dirname(self.source_filepath), new_filename)
            self.filename = new_filename
            # Atualiza os metadados.
            self.meta['source_filepath'] = os.path.abspath(self.source_filepath)
            # Renomeia o arquivo.
            os.rename(self.meta['old_filepath'], self.meta['source_filepath'])
            if meta_text:
                # Renomeia o arquivo acessório.
                text_name = os.path.basename(self.meta['old_filepath'])
                new_name = text_name.split('.')[0] + '.txt'
                text_path = os.path.join(os.path.dirname(self.meta['old_filepath']), new_name)
                new_path = self.source_filepath.split('.')[0] + '.txt'
                os.rename(text_path, new_path)
        else:
            self.meta['source_filepath'] = os.path.abspath(self.source_filepath)

        # Processa o vídeo.
        web_paths, thumb_filepath, large_thumb = self.process_video()
        if not web_paths:
            return None

        # Prepara alguns campos para banco de dados.
        self.meta = prepare_meta(self.meta)

        for k, v in web_paths.iteritems():
            self.meta[k] = v.strip('site_media/')
        self.meta['thumb_filepath'] = thumb_filepath.strip('site_media/')
        self.meta['large_thumb'] = large_thumb.strip('site_media/')

        return self.meta

    def build_call(self, filepath, ipass):
        '''Constrói o subprocesso para converter o vídeo com o FFmpeg.'''
        #FIXME Descobrir jeito de forçar width e height serem par!

        # Básico
        call = [
                'ffmpeg', '-y', '-i', self.source_filepath,
                '-metadata', 'title="%s"' % self.meta['title'],
                '-metadata', 'author="%s"' % self.meta['author'],
                '-b', '600k', '-g', '15', '-bf', '2',
                '-threads', '0', '-pass', str(ipass),
                ]
        # HD
        #TODO Achar um jeito mais confiável de saber se é HD...
        if self.source_filepath.endswith('m2ts'):
            # Ideal seria ser reconhecida direito no desktop...
            call.extend(['-vf', 'scale=512:288', '-aspect', '4:3'])
        else:
            call.extend(['-vf', 'scale=512:384', '-aspect', '4:3'])
        # Audio codecs
        # Exemplo para habilitar som no vídeo: filepath_comsom_.avi
        if 'comsom' in self.source_filepath.split('_') and ipass == 2:
            if filepath.endswith('mp4'):
                call.extend(['-acodec', 'libfaac', '-ab', '128k',
                    '-ac', '2', '-ar', '44100'])
            else:
                call.extend(['-acodec', 'libvorbis', '-ab', '128k',
                    '-ac', '2', '-ar', '44100'])
        else:
            call.append('-an')

        # Video codec
        if filepath.endswith('webm'):
            call.extend(['-vcodec', 'libvpx'])
        elif filepath.endswith('mp4'):
            call.extend(['-vcodec', 'libx264'])
        if filepath.endswith('ogv'):
            call.extend(['-vcodec', 'libtheora'])
        # Presets
        # Precisa ser colocado depois do vcodec.
        if ipass == 1:
            call.extend(['-vpre', 'veryslow_firstpass'])
        elif ipass == 2:
            call.extend(['-vpre', 'veryslow'])
        # Finaliza com nome do arquivo
        call.append(filepath)
        return call

    def process_video(self):
        '''Redimensiona o vídeo, inclui marca d'água e comprime.'''
        # Exemplo:
        #       /usr/local/bin/ffmpeg -y -i pelagosfera004.m2ts -vf "scale=510:-1" -aspect 16:9 -pass 1 -vcodec libvpx -b 300k -g 15 -bf 2 -vpre veryslow_firstpass -acodec libvorbis -ab 128k -ac 2 -ar 44100 -threads 2 teste2.webm
        #       /usr/local/bin/ffmpeg -y -i pelagosfera004.m2ts -vf "scale=510:-1" -aspect 16:9 -pass 2 -vcodec libvpx -b 300k -g 15 -bf 2 -vpre veryslow -acodec libvorbis -ab 128k -ac 2 -ar 44100 -threads 2 teste2.webm
        #FIXME O que fazer quando vídeos forem menores que isso?
        print '\nProcessando o vídeo...'
        web_paths = {}
        try:
            # WebM
            webm_name = self.filename.split('.')[0] + '.webm'
            webm_filepath = os.path.join(self.local_dir, webm_name)
            webm_firstcall = self.build_call(webm_filepath, 1)
            webm_secondcall = self.build_call(webm_filepath, 2)
            # MP4
            mp4_name = self.filename.split('.')[0] + '.mp4' 
            mp4_filepath = os.path.join(self.local_dir, mp4_name)
            mp4_firstcall = self.build_call(mp4_filepath, 1)
            mp4_secondcall = self.build_call(mp4_filepath, 2)
            # OGG
            ogg_name = self.filename.split('.')[0] + '.ogv' 
            ogg_filepath = os.path.join(self.local_dir, ogg_name)
            ogg_firstcall = self.build_call(ogg_filepath, 1)
            ogg_secondcall = self.build_call(ogg_filepath, 2)
            try:
                # WebM
                subprocess.call(webm_firstcall)
                subprocess.call(webm_secondcall)
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
                subprocess.call(mp4_firstcall)
                subprocess.call(mp4_secondcall)
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
                subprocess.call(ogg_firstcall)
                subprocess.call(ogg_secondcall)
                try:
                    # Copia imagem para pasta web
                    ogg_site_filepath = os.path.join(self.site_dir, ogg_name)
                    copy(ogg_filepath, ogg_site_filepath)
                except:
                    print 'Não conseguiu copiar para o site.'
                web_paths['ogg_filepath'] = ogg_site_filepath
            except:
                print 'Processamento do OGG não funcionou!'
        except IOError:
            print '\nOcorreu algum erro na conversão da imagem.'
            return None, None, None
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
            #XXX Lembrar de deixar do mesmo tamanho do vídeo...
            if self.source_filepath.endswith('m2ts'):
            	subprocess.call(['ffmpeg', '-i', self.source_filepath, '-vframes', '1', '-vf', 'scale=512:288', '-aspect', '16:9', '-ss', '1', '-f', 'image2', local_filepath_large])
            else:
                subprocess.call(['ffmpeg', '-i', self.source_filepath, '-vframes', '1', '-vf', 'scale=512:384', '-ss', '1', '-f', 'image2', local_filepath_large])
            # Cria thumb normal (pequeno)
            subprocess.call(['convert', '-define', 'jpeg:size=200x150', local_filepath_large, '-thumbnail', '120x90^', '-gravity', 'center', '-extent', '120x90', 'PNG8:%s' % local_filepath])
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

    def create_meta(self, charset='utf-8', new=False):
        '''Define as variáveis extraídas dos metadados da imagem.

        Usa a biblioteca do arquivo iptcinfo.py para padrão IPTC e pyexiv2 para EXIF.
        '''
        print u'Lendo os metadados de %s e criando variáveis.' % self.filename
        # Criar objeto com metadados
        info = IPTCInfo(self.source_filepath, True, charset)
        # Checando se o arquivo tem dados IPTC
        if len(info.data) < 4:
            print '%s não tem dados IPTC!' % self.filename

        # Limpa metadados pra não misturar com o anterior.
        self.meta = {}
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
                #'genus_sp': info.data['original transmission reference'], # 103
                'size': info.data['special instructions'], # 40
                'source': info.data['source'], # 115
                'references': info.data['credit'], #110
                'timestamp': self.timestamp,
                'notes': u'',
                }

        if new:
            # Adiciona o antigo caminho aos metadados.
            self.meta['old_filepath'] = os.path.abspath(self.source_filepath)
            new_filename = rename_file(self.filename, self.meta['author'])
            # Atualiza media object.
            self.source_filepath = os.path.join(
                    os.path.dirname(self.source_filepath), new_filename)
            self.filename = new_filename
            # Atualiza os metadados.
            self.meta['source_filepath'] = os.path.abspath(self.source_filepath)
            os.rename(self.meta['old_filepath'], self.meta['source_filepath'])
        else:
            self.meta['source_filepath'] = os.path.abspath(self.source_filepath)

        # Prepara alguns campos para banco de dados
        self.meta = prepare_meta(self.meta)

        # Extraindo metadados do EXIF
        exif = self.get_exif(self.source_filepath)
        date = self.get_date(exif)
        try:
            date_string = date.strftime('%Y-%m-%d %I:%M:%S')
        except:
            date_string = ''
        if date_string and date_string != '0000:00:00 00:00:00':
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
        if not web_filepath:
            return None
        self.meta['web_filepath'] = web_filepath.strip('site_media/')
        self.meta['thumb_filepath'] = thumb_filepath.strip('site_media/')

        print
        print u'\tVariável\tMetadado'
        print u'\t' + 40 * '-'
        print u'\t' + self.meta['web_filepath']
        print u'\t' + self.meta['thumb_filepath']
        print u'\t' + 40 * '-'
        print u'\tTítulo:\t\t%s' % self.meta['title']
        print u'\tDescrição:\t%s' % self.meta['caption']
        #printu '\tEspécie:\t%s' % self.meta['genus_sp']
        print u'\tTáxon:\t\t%s' % ', '.join(self.meta['taxon'])
        print u'\tTags:\t\t%s' % '\n\t\t\t'.join(self.meta['tags'])
        print u'\tTamanho:\t%s' % self.meta['size']
        print u'\tEspecialista:\t%s' % self.meta['source']
        print u'\tAutor:\t\t%s' % ', '.join(self.meta['author'])
        print u'\tSublocal:\t%s' % self.meta['sublocation']
        print u'\tCidade:\t\t%s' % self.meta['city']
        print u'\tEstado:\t\t%s' % self.meta['state']
        print u'\tPaís:\t\t%s' % self.meta['country']
        print u'\tDireitos:\t%s' % self.meta['rights']
        print u'\tData:\t\t%s' % self.meta['date']
        print
        print u'\tGeolocalização:\t%s' % self.meta['geolocation']
        print u'\tDecimal:\t%s, %s' % (self.meta['latitude'],
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
        gps['latdeg'] = exif['Exif.GPSInfo.GPSLatitude'].value[0]
        gps['latmin'] = exif['Exif.GPSInfo.GPSLatitude'].value[1]
        gps['latsec'] = exif['Exif.GPSInfo.GPSLatitude'].value[2]
        latitude = self.get_decimal(
                gps['latref'], gps['latdeg'], gps['latmin'], gps['latsec'])
        # Longitude
        gps['longref'] = exif['Exif.GPSInfo.GPSLongitudeRef'].value
        gps['longdeg'] = exif['Exif.GPSInfo.GPSLongitude'].value[0]
        gps['longmin'] = exif['Exif.GPSInfo.GPSLongitude'].value[1]
        gps['longsec'] = exif['Exif.GPSInfo.GPSLongitude'].value[2]
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
                '-quality', '70', '-resize', '800x800>', local_filepath])
            # Insere marca d'água no canto direito embaixo
            subprocess.call(['composite', '-gravity', 'southwest', watermark, local_filepath, local_filepath])
            # Copia imagem para pasta web
            web_filepath = os.path.join(self.site_dir, self.filename)
            copy(local_filepath, web_filepath)
        except IOError:
            print '\nOcorreu algum erro na conversão da imagem. Verifique se o ' \
                    'ImageMagick está instalado.'
            #TODO Criar entrada no log
            copy(self.source_filepath,
                    '/home/nelas/bugs/' + os.path.basename(os.readlink(self.source_filepath)))
            # Evita que o loop seja interrompido.
            return None, None
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
        video_extensions = ('avi', 'AVI', 'mov', 'MOV', 'mp4', 'MP4', 'ogg', 'OGG', 'ogv', 'OGV', 'dv', 'DV', 'mpg', 'MPG', 'mpeg', 'MPEG', 'flv', 'FLV', 'm2ts', 'M2TS', 'wmv', 'WMV')
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
                continue
        else:
            print '\n%d arquivos encontrados.' % n

        return self.files


# Funções principais

def rename_file(filename, authors):
    '''Renomeia arquivo com iniciais e identificador.'''
    print u'%s, hora de renomeá-lo!' % filename
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

def prepare_meta(meta):
    '''Processa as strings dos metadados convertendo para bd.
    
    Transforma None em string vazia, transforma autores e táxons em lista,
    espécies em dicionário.
    '''
    # Converte valores None para string em branco
    for k, v in meta.iteritems():
        if v is None:
            meta[k] = u''

    #FIXME Checar se tags estão no formato de lista...
    #if not isinstance(meta['tags'], list):

    # Preparando autor(es) para o banco de dados
    meta['author'] = [a.strip() for a in meta['author'].split(',')] 
    # Preparando especialista(s) para o banco de dados
    meta['source'] = [a.strip() for a in meta['source'].split(',')] 
    # Preparando referências para o banco de dados
    meta['references'] = [a.strip() for a in meta['references'].split(',')] 
    # Preparando taxon(s) para o banco de dados
    #XXX Lidar com fortuitos sp.?
    #XXX Lidar com fortuitos aff. e espécies com 3 nomes?
    #meta['taxon'] = [a.strip() for a in meta['taxon'].split(',')] 
    temp_taxa = [a.strip() for a in meta['taxon'].split(',')] 
    clean_taxa = []
    for taxon in temp_taxa:
        tsplit = taxon.split()
        if len(tsplit) == 2 and tsplit[-1] in ['sp', 'sp.', 'spp']:
            tsplit.pop()
            clean_taxa.append(tsplit[0])
        else:
            clean_taxa.append(taxon)
    meta['taxon'] = clean_taxa

    return meta

def dir_ready(*dirs):
    '''Verifica se o diretório existe, criando caso não exista.'''
    for dir in dirs:
        if os.path.isdir(dir) is False:
            print 'Criando diretório inexistente...'
            os.mkdir(dir)

def remove_broken():
    '''Deleta entradas de imagens oficiais apagadas.
    
    Script linking.py salva um pickle do dicionário com os arquivos que devem
    ser apagados.
    '''
    try:
        file = open('to_del', 'rb')
        lost = pickle.load(file)
    except:
        print 'Nenhum arquivo pra deletar.'
        return
    for k, v in lost.iteritems():
        name = os.path.basename(k)
        if name.endswith('txt'):
            os.remove(k)
        try:
            media = Image.objects.get(web_filepath__icontains=name)
        except:
            try:
                media = Video.objects.get(webm_filepath__icontains=name)
            except:
                print 'Nenhum imagem com nome %s' % name
                continue
        if media:
            #TODO Deletar os thumbs e site media também?
            media.is_public = False
            media.review = True
            os.remove(media.source_filepath)
            media.save()
            print 'Link problemático apagado e imagem não está mais pública.'
    print 'Apagando arquivo pickle...'
    file.close()
    os.remove('to_del')

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
    print '  -n {n}, --n-max {n} (padrão=10000)'
    print '\tEspecifica um número máximo de arquivos que o programa irá ' \
            'verificar.'
    print
    print '  -f, --force-update'
    print '\tAtualiza banco de dados e refaz thumbnails de todas as entradas, '
    print '\tinclusive as que não foram modificadas.'
    print
    print '  -v, --only-videos'
    print '\tAtualiza apenas arquivos de vídeo.'
    print
    print '  -p, --only-photos'
    print '\tAtualiza apenas arquivos de fotos.'
    print
    print '  -t, --no-tsv'
    print '\tNão força atualização do TSV.'
    print
    print '  -r, --no-rename'
    print '\tNão executa a função de renomear arquivos.'
    print
    print 'Exemplo:'
    print '  python cifonauta.py -fp -n 15'
    print '\tFaz a atualização forçada dos primeiros 15 fotos que o programa'
    print '\tencontrar na pasta padrão e atualiza TSV de todas as imagens.'
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
    no_rename = False
    n_max = 10000
    web_upload = False
    single_img = False
    only_videos = False
    only_photos = False
    update_tsv = True

    # Verifica se argumentos foram passados com a execução do programa
    try:
        opts, args = getopt.getopt(argv, 'hfrvptn:', [
            'help',
            'force-update',
            'no-rename',
            'only-videos',
            'only-photos',
            'no-tsv',
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
        elif opt in ('-r', '--no-rename'):
            no_rename = True
        elif opt in ('-v', '--only-videos'):
            only_videos = True
        elif opt in ('-p', '--only-photos'):
            only_photos = True
        elif opt in ('-t', '--no-tsv'):
            update_tsv = False

    # Imprime resumo do que o programa vai fazer
    if force_update is True:
        print u'\n%d arquivos serão atualizadas de forma forçada.' % n_max
        print u'(argumento "-f" utilizado)'
    else:
        print u'\n%d arquivos serão verificadas e registradas no banco de ' \
                'dados.' % n_max
    if only_videos is True:
        print u'\nApenas vídeos serão atualizadas.'
    elif only_photos is True:
        print u'\nApenas fotos serão atualizadas.'

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
            if not only_videos:
                media = Photo(path[0])
            else:
                # Caso seja apenas vídeos, pular para próximo ítem.
                continue
        elif path[1] == 'video':
            if not only_photos:
                media = Movie(path[0])
            else:
                # Caso seja apenas fotos, pular para próximo ítem.
                continue
        # Busca nome do arquivo no banco de dados
        query = cbm.search_db(media)
        if not query:
            # Se mídia for nova
            print '\nARQUIVO NOVO, CRIANDO ENTRADA NO BANCO DE DADOS...'
            if no_rename:
                # Caso o arquivo esteja corrompido, pular
                if not media.create_meta():
                    continue
            else:
                # Caso o arquivo esteja corrompido, pular
                if not media.create_meta(new=True):
                    continue
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

    # Força salvar todas as imagens para atualizar o TSV com traduções novas.
    if update_tsv:
        print u'\nATUALIZANDO TSV (pode demorar)'
        images = Image.objects.all()
        videos = Video.objects.all()
        print u'das imagens...'
        for image in images:
            image.save()
        print u'dos vídeos...'
        for video in videos:
            video.save()
        print u'Feito! TSV atualizado.'

    # Deletando arquivo log se ele estiver vazio
    if log.read(1024) == '':
        log.close()
        # Deletando log vazio
        os.remove(logname)
    else:
        # Fechando arquivo de log
        log.close()
    
    #TODO Melhorar as estatísticas daqui...
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
    print 'Verificando e atualizando os links da pasta oficial...'
    linking.main()
    remove_broken()
    # Inicia função principal, lendo os argumentos (se houver)
    main(sys.argv[1:])
