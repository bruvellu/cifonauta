#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CIFONAUTA
# Copyleft 2010-2011 - Bruno C. Vellutini | organelas.com
#
#TODO Definir licença.
#
'''Gerenciador do banco de imagens do CEBIMar-USP.

Este programa gerencia os arquivos do banco de imagens do CEBIMar lendo seus
metadados, reconhecendo marquivos modificados e atualizando o website.

Centro de Biologia Marinha da Universidade de São Paulo.
'''

import getopt
import logging
import os
import pickle
import sys
import subprocess
import time

from datetime import datetime
from iptcinfo import IPTCInfo
from shutil import copy

import linking
from itis import Itis
from media_utils import *

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import *

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010-2011, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.9.0'
__maintainer__ = 'Bruno Vellutini'
__email__ = 'organelas@gmail.com'
__status__ = 'Development'


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
        print
        logger.info('Procurando %s (%s) no banco de dados...',
                media.filename, media.source_filepath)
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
                            logger.debug('%s não está no banco de dados.',
                                    media.filename)
                            return False
            logger.debug('Bingo! Registro de %s encontrado.', media.filename)
            logger.info('Comparando timestamp do arquivo com o registro...')
            if record.timestamp != media.timestamp:
                logger.debug('Arquivo mudou! Retorna 1')
                return 1
            else:
                logger.debug('Arquivo não mudou! Retorna 2')
                return 2
        except Image.DoesNotExist:
            logger.debug('Registro não encontrado (Image.DoesNotExist).')
            return False

    def update_db(self, media, update=False):
        '''Cria ou atualiza registro no banco de dados.'''
        logger.info('Atualizando o banco de dados...')
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
            logger.debug('Mídia %s sem título ou autor!', 
                    media_meta['source_filepath'])
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Deleta para inserir autores separadamente.
        del media_meta['author']

        # Transforma valores em instâncias dos modelos
        toget = ['size', 'rights', 'sublocation',
                'city', 'state', 'country']
        for k in toget:
            logger.debug('META (%s): %s', k, media_meta[k])
            # Apenas criar se não estiver em branco.
            if media_meta[k]:
                media_meta[k] = self.get_instance(k, media_meta[k])
                logger.debug('INSTANCES FOUND: %s', media_meta[k])
            else:
                del media_meta[k]

        if not update:
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

        logger.info('Registro no banco de dados atualizado!')

    def get_instance(self, table, value):
        '''Retorna o id a partir do nome.'''
        model, new = eval('%s.objects.get_or_create(name="%s")' % (table.capitalize(), value))
        if table == 'taxon' and new:
            # Consulta ITIS para extrair táxons.
            taxon = self.get_itis(value)
            # Reforça, caso a conexão falhe.
            if not taxon:
                taxon = self.get_itis(value)
                if not taxon:
                    logger.debug('Nova tentativa em 5s...')
                    time.sleep(5)
                    taxon = self.get_itis(value)
            try:
                # Por fim, atualizar o modelo.
                model = taxon.update_model(model)
            except:
                logger.warning('Não rolou pegar hierarquia...')
        return model

    def update_sets(self, entry, field, meta):
        '''Atualiza campos many to many do banco de dados.

        Verifica se o value não está em branco, para não adicionar entradas em
        branco no banco.
        '''
        logger.debug('META (%s): %s', field, meta)
        meta_instances = [self.get_instance(field, value) for value in meta if value.strip()]
        logger.debug('INSTANCES FOUND: %s', meta_instances)
        eval('entry.%s_set.clear()' % field)
        [eval('entry.%s_set.add(value)' % field) for value in meta_instances if meta_instances]
        return entry

    def get_itis(self, name):
        '''Consulta banco de dados do ITIS.

        Extrai o táxon pai e o ranking. Valores são guardados em:

        taxon.name
        taxon.rank
        taxon.tsn
        taxon.parents
        taxon.parent['name']
        taxon.parent['tsn']
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
        logger.info('Lendo os metadados de %s e criando objetos.' % 
                self.filename)
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
                'size': u'',
                'source': u'',
                'date': '1900-01-01 01:01:01',
                'geolocation': u'',
                'latitude': u'',
                'longitude': u'',
                'references': u'',
                'notes': u'',
                'duration': u'',
                'dimensions': u'',
                'codec': u'',
                }

        # Verifica se arquivo acessório com meta dos vídeos existe.
        try:
            linked_to = os.readlink(self.source_filepath)
            txt_path = linked_to.split('.')[0] + '.txt'
            meta_text = open(txt_path, 'rb')
            logger.debug('Arquivo acessório %s existe!', txt_path)
        except:
            logger.debug('Arquivo acessório de %s não existe!', 
                    self.source_filepath)
            meta_text = ''

        if meta_text:
            try:
                meta_dic = pickle.load(meta_text)
                # Atualiza meta com valores do arquivo acessório.
                self.meta.update(meta_dic)
                meta_text.close()
            except:
                logger.warning('Pickle está corrompido: %s', meta_text)

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

        # Inclui duração, dimensões e codec do vídeo.
        infos = get_info(self.meta['source_filepath'])
        self.meta.update(infos)

        # Processa o vídeo.
        web_paths, thumb_filepath, large_thumb = self.process_video()
        # Caso arquivo esteja corrompido.
        if not web_paths:
            return None

        # Prepara alguns campos para banco de dados.
        self.meta = prepare_meta(self.meta)

        # Insere paths sem o folder site_media
        for k, v in web_paths.iteritems():
            self.meta[k] = v.strip('site_media/')
        self.meta['thumb_filepath'] = thumb_filepath.strip('site_media/')
        self.meta['large_thumb'] = large_thumb.strip('site_media/')

        return self.meta

    def build_call(self, filepath):
        '''Constrói o subprocesso para converter o vídeo com o FFmpeg.
        #webm HD
        ffmpeg -y -i hd.m2ts -i marca.png -metadata title="A WEBM HD" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libvorbis -b:a 128k -ac 2 -ar 44100 -vcodec libvpx
        -filter_complex "scale=512x288,overlay=0:main_h-overlay_h-0" hd.webm

        #webm DV
        ffmpeg -y -i dv.avi -i marca.png -metadata title="A WEBM DV" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libvorbis -b:a 128k -ac 2 -ar 44100 -vcodec libvpx
        -filter_complex "scale=512x384,overlay=0:main_h-overlay_h-0" dv.webm

        #ogg HD
        ffmpeg -y -i hd.m2ts -i marca.png -metadata title="AN OGG HD" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libvorbis -b:a 128k -ac 2 -ar 44100 -vcodec libtheora
        -filter_complex "scale=512x288,overlay=0:main_h-overlay_h-0" hd.ogv

        #ogg DV
        ffmpeg -y -i dv.avi -i marca.png -metadata title="AN OGG DV" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libvorbis -b:a 128k -ac 2 -ar 44100 -vcodec libtheora
        -filter_complex "scale=512x384,overlay=0:main_h-overlay_h-0" dv.ogv

        #mp4 HD
        ffmpeg -y -i hd.m2ts -i marca.png -metadata title="A MP4 HD" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libfaac -b:a 128k -ac 2 -ar 44100 -vcodec libx264
        -filter_complex "scale=512x288,overlay=0:main_h-overlay_h-0" hd.mp4

        #mp4 DV
        ffmpeg -y -i dv.avi -i marca.png -metadata title="A MP4 DV" -metadata author="AN AUTHOR"
        -b:v 600k -threads 0 -acodec libfaac -b:a 128k -ac 2 -ar 44100 -vcodec libx264
        -filter_complex "scale=512x384,overlay=0:main_h-overlay_h-0" dv.mp4
        '''
        # Base
        call = [
                'ffmpeg', '-y', '-i', self.source_filepath, '-i', 'marca.png',
                '-metadata', 'title="%s"' % self.meta['title'],
                '-metadata', 'author="%s"' % self.meta['author'],
                '-b:v', '600k', '-threads', '0',
                ]
        #TODO Achar um jeito mais confiável de saber se é HD...
        # Comando cria objeto da marca d'água e redimensiona para 100px de 
        # largura, redimensiona o vídeo para o tamanho certo de acordo com seu 
        # tipo e insere a marca no canto esquerdo embaixo.
        if self.source_filepath.endswith('m2ts'):
            call.extend([
                '-filter_complex', 'scale=512x288,overlay=0:main_h-overlay_h-0',
                '-aspect', '16:9',
                ])
        else:
            call.extend([
                '-filter_complex', 'scale=512x384,overlay=0:main_h-overlay_h-0',
                '-aspect', '4:3',
                ])
        # Audio codecs
        # Exemplo para habilitar som no vídeo: filepath_comsom_.avi
        if 'comsom' in self.source_filepath.split('_'):
            if filepath.endswith('mp4'):
                call.extend(['-acodec', 'libfaac', '-b:a', '128k',
                    '-ac', '2', '-ar', '44100'])
            else:
                call.extend(['-acodec', 'libvorbis', '-b:a', '128k',
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

        # Finaliza com nome do arquivo
        call.append(filepath)
        return call

    def process_video(self):
        '''Redimensiona o vídeo, inclui marca d'água e comprime.'''
        #FIXME O que fazer quando vídeos forem menores que isso?
        logger.info('Processando o vídeo %s', self.source_filepath)
        web_paths = {}
        try:
            #TODO Repensar essa função no módulo media_utils.
            # WebM
            webm_name = self.filename.split('.')[0] + '.webm'
            webm_filepath = os.path.join(self.local_dir, webm_name)
            webm_call = self.build_call(webm_filepath)
            # MP4
            mp4_name = self.filename.split('.')[0] + '.mp4'
            mp4_filepath = os.path.join(self.local_dir, mp4_name)
            mp4_call = self.build_call(mp4_filepath)
            # OGG
            ogg_name = self.filename.split('.')[0] + '.ogv'
            ogg_filepath = os.path.join(self.local_dir, ogg_name)
            ogg_call = self.build_call(ogg_filepath)
            try:
                # WebM
                subprocess.call(webm_call)
                try:
                    # Copia vídeo para pasta web
                    webm_site_filepath = os.path.join(self.site_dir, webm_name)
                    copy(webm_filepath, webm_site_filepath)
                except:
                    logger.warning('Erro ao copiar %s para o site.', 
                            webm_filepath)
                web_paths['webm_filepath'] = webm_site_filepath
            except:
                logger.warning('Processamento do WebM (%s) não funcionou!', 
                        webm_filepath)
            try:
                # MP4
                subprocess.call(mp4_call)
                try:
                    # Copia vídeo para pasta web
                    mp4_site_filepath = os.path.join(self.site_dir, mp4_name)
                    copy(mp4_filepath, mp4_site_filepath)
                    try:
                        subprocess.call(['qt-faststart', mp4_site_filepath,
                            mp4_site_filepath])
                    except:
                        logger.debug('qt-faststart não funcionou para %s', 
                                mp4_filepath)
                except:
                    logger.warning('Erro ao copiar %s para o site.', 
                            mp4_filepath)
                web_paths['mp4_filepath'] = mp4_site_filepath
            except:
                logger.warning('Processamento do x264 (%s) não funcionou!', 
                        mp4_filepath)
            try:
                # OGG
                subprocess.call(ogg_call)
                try:
                    # Copia vídeo para pasta web
                    ogg_site_filepath = os.path.join(self.site_dir, ogg_name)
                    copy(ogg_filepath, ogg_site_filepath)
                except:
                    logger.warning('Erro ao copiar %s para o site.', 
                            ogg_filepath)
                web_paths['ogg_filepath'] = ogg_site_filepath
            except:
                logger.warning('Processamento do OGG (%s) não funcionou!', 
                        ogg_filepath)
        except IOError:
            logger.warning('Erro na conversão de %s.')
            return None, None, None
        else:
            logger.info('%s convertido com sucesso!', self.source_filepath)
            thumb_localpath, still_localpath = create_still(
                    self.source_filepath, self.local_thumb_dir)

            # Copia thumb e still da pasta local para site_media.
            try:
                copy(thumb_localpath, self.site_thumb_dir)
                logger.debug('Thumb copiado para %s', self.site_thumb_dir)
                copy(still_localpath, self.site_thumb_dir)
                logger.debug('Still copiado para %s', self.site_thumb_dir)
            except IOError:
                logger.warning('Não conseguiu copiar thumb ou still em %s', 
                        self.site_thumb_dir)

            # Define caminho para o thumb e still do site.
            thumb_sitepath = os.path.join(
                    self.site_thumb_dir,
                    os.path.basename(thumb_localpath)
                    )
            still_sitepath = os.path.join(
                    self.site_thumb_dir,
                    os.path.basename(still_localpath)
                    )

            return web_paths, thumb_sitepath, still_sitepath


class Photo:
    '''Define objeto para instâncias das fotos.'''
    def __init__(self, filepath):
        self.source_filepath = filepath
        self.filename = os.path.basename(filepath)
        # Checar se arquivo existe antes.
        if check_file(self.source_filepath):
            self.timestamp = datetime.fromtimestamp(
                    os.path.getmtime(self.source_filepath))
            self.type = 'photo'
        else:
            logger.critical('Arquivo não existe: %s', self.source_filepath)
            logger.debug('Removendo link quebrado: %s', self.source_filepath)
            os.remove(self.source_filepath)
            self.type = 'broken'

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
        logger.info('Lendo metadados de %s e criando objetos.',
                self.filename)

        # Criar objeto com metadados.
        info = IPTCInfo(self.source_filepath, True, charset)
        # Checando se o arquivo tem dados IPTC.
        if len(info.data) < 4:
            logger.warning('%s não tem dados IPTC!', self.filename)

        # Limpa metadados pra não misturar com o anterior.
        self.meta = {}
        self.meta = {
                'source_filepath': os.path.abspath(self.source_filepath),
                'title': info.data['object name'],                      #5
                'tags': info.data['keywords'],                          #25
                'author': info.data['by-line'],                         #80
                'city': info.data['city'],                              #90
                'sublocation': info.data['sub-location'],               #92
                'state': info.data['province/state'],                   #95
                'country': info.data['country/primary location name'],  #101
                'taxon': info.data['headline'],                         #105
                'rights': info.data['copyright notice'],                #116
                'caption': info.data['caption/abstract'],               #120
                'size': info.data['special instructions'],              #40
                'source': info.data['source'],                          #115
                'references': info.data['credit'],                      #110
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

        # Prepara alguns campos para banco de dados.
        self.meta = prepare_meta(self.meta)

        # Extraindo metadados do EXIF.
        exif = get_exif(self.source_filepath)
        # Extraindo data.
        self.meta['date'] = get_date(exif)
        # Extraindo a geolocalização.
        gps = get_gps(exif)
        self.meta.update(gps)

        # Processar imagem.
        web_filepath, thumb_filepath = self.process_photo()
        # Caso arquivo esteja corrompido, interromper.
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
        print u'\tTáxon:\t\t%s' % ', '.join(self.meta['taxon'])
        print u'\tTags:\t\t%s' % '\n\t\t\t'.join(self.meta['tags'])
        print u'\tTamanho:\t%s' % self.meta['size']
        print u'\tEspecialista:\t%s' % ', '.join(self.meta['source'])
        print u'\tAutor:\t\t%s' % ', '.join(self.meta['author'])
        print u'\tSublocal:\t%s' % self.meta['sublocation']
        print u'\tCidade:\t\t%s' % self.meta['city']
        print u'\tEstado:\t\t%s' % self.meta['state']
        print u'\tPaís:\t\t%s' % self.meta['country']
        print u'\tDireitos:\t%s' % self.meta['rights']
        print u'\tData:\t\t%s' % self.meta['date']
        print
        print u'\tGeolocalização:\t%s' % self.meta['geolocation'].decode("utf8")
        print u'\tDecimal:\t%s, %s' % (self.meta['latitude'],
                self.meta['longitude'])
        print

        return self.meta

    def process_photo(self):
        '''Redimensiona a imagem e inclui marca d'água.'''
        logger.info('Processando %s...', self.source_filepath)
        photo_localpath = os.path.join(self.local_dir, self.filename)
        try:
            # Converte o arquivo para a web.
            converted = convert_to_web(self.source_filepath, photo_localpath)
            # Insere marca d'água.
            watermark = watermarker(photo_localpath)
            # Define caminho para arquivo web.
            photo_sitepath = os.path.join(self.site_dir, self.filename)
            # Copia foto para pasta site_media se .
            copy(photo_localpath, photo_sitepath)
        except IOError:
            logger.warning('Erro na conversão de %s, verifique o ImageMagick.', 
                    self.source_filepath)
            # Evita que o loop seja interrompido.
            return None, None
        else:
            logger.info('%s convertida com sucesso!', self.source_filepath)
            thumb_localpath = create_thumb(self.source_filepath, 
                    self.local_thumb_dir)

            # Copia thumb da pasta local para site_media.
            try:
                copy(thumb_localpath, self.site_thumb_dir)
                logger.debug('Thumb copiado para %s', self.site_thumb_dir)
            except:
                logger.warning('Erro ao copiar thumb para %s', self.site_thumb_dir)

            # Define caminho para o thumb do site.
            thumb_sitepath = os.path.join(
                    self.site_thumb_dir,
                    os.path.basename(thumb_localpath)
                    )

            return photo_sitepath, thumb_sitepath


class Folder:
    '''Classes de objetos para lidar com as pastas e seus arquivos.

    >>> dir = 'source_media'
    >>> folder = Folder(dir, 100)
    >>> os.path.isdir(folder.folder_path)
    True
    >>> filepaths = folder.get_files()
    >>> isinstance(filepaths, list)
    True
    '''
    def __init__(self, folder, n_max):
        self.folder_path = folder
        self.n_max = n_max
        self.files = []
        logger.debug('Pasta a ser analisada: %s', self.folder_path)

    def get_files(self, type=None):
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
                filepath = fix_filename(root, filename)
                if filepath.endswith(photo_extensions) and n < self.n_max:
                    if type is None or type == 'photo':
                        self.files.append((filepath, 'photo'))
                        n += 1
                    continue
                if filepath.endswith(video_extensions) and n < self.n_max:
                    if type is None or type == 'video':
                        self.files.append((filepath, 'video'))
                        n += 1
                    continue
                elif filepath.endswith(ignore_extensions):
                    logger.debug('Ignorando %s', filepath)
                    continue
            else:
                continue
        else:
            logger.info('%d arquivos encontrados.', n)

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

def build_autocomplete():
    '''Cria arquivo para popular o autocomplete do Véliger.'''
    autocomplete = open('autocomplete.pkl', 'wb')
    tags = Tag.objects.values_list('name', flat=True)
    taxa = Taxon.objects.values_list('name', flat=True)
    sources = Source.objects.values_list('name', flat=True)
    authors = Author.objects.values_list('name', flat=True)
    rights = Rights.objects.values_list('name', flat=True)
    places = Sublocation.objects.values_list('name', flat=True)
    cities = City.objects.values_list('name', flat=True)
    states = State.objects.values_list('name', flat=True)
    countries = Country.objects.values_list('name', flat=True)
    autolists = {
            'tags': list(tags),
            'taxa': list(taxa),
            'sources': list(sources),
            'authors': list(authors),
            'rights': list(rights),
            'places': list(places),
            'cities': list(cities),
            'states': list(states),
            'countries': list(countries),
            }
    pickle.dump(autolists, autocomplete)
    autocomplete.close()

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
    print 'Exemplo:'
    print '  python cifonauta.py -fp -n 15'
    print '\tFaz a atualização forçada dos primeiros 15 fotos que o programa'
    print '\tencontrar na pasta padrão e atualiza TSV de todas as imagens.'
    print

def main(argv):
    ''' Função principal do programa.

    Lê os argumentos se houver e chama as outras funções.
    '''
    # Diretório com os arquivos
    source_dir = u'source_media'
    n = 0
    n_new = 0
    n_up = 0
    # Valores padrão para argumentos
    force_update = False
    n_max = 20000
    web_upload = False
    single_img = False
    only_videos = False
    only_photos = False

    # Verifica se argumentos foram passados com a execução do programa
    try:
        opts, args = getopt.getopt(argv, 'hfvpn:', [
            'help',
            'force-update',
            'only-videos',
            'only-photos',
            'n='])
    except getopt.GetoptError:
        usage()
        logger.critical('Algo errado nos argumentos "%s". Abortando...',
                ' '.join(argv))
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
        elif opt in ('-v', '--only-videos'):
            only_videos = True
        elif opt in ('-p', '--only-photos'):
            only_photos = True

    # Imprime resumo do que o programa vai fazer
    logger.debug('Argumentos: n=%d, force_update=%s, only_photos=%s, only_videos=%s.',
            n_max, force_update, only_photos, only_videos)

    # Verifica e atualiza links entre pasta "oficial" e "source_media".
    linking.main()

    # Cria instância do bd
    cbm = Database()

    # Inicia o cifonauta buscando pasta...
    folder = Folder(source_dir, n_max)
    if only_photos:
        filepaths = folder.get_files(type='photo')
    elif only_videos:
        filepaths = folder.get_files(type='video')
    else:
        filepaths = folder.get_files()
    for path in filepaths:
        # Reconhece se é foto ou vídeo
        if path[1] == 'photo':
            media = Photo(path[0])
        elif path[1] == 'video':
            media = Movie(path[0])
        # Skip path if it is a broken link.
        if media.type == 'broken':
            continue
        # Busca nome do arquivo no banco de dados
        query = cbm.search_db(media)
        if not query:
            # Se mídia for nova
            logger.info('ARQUIVO NOVO: %s. CRIANDO ENTRADA NO BANCO DE DADOS...', media.filename)
            # Caso o arquivo esteja corrompido, pular
            if not media.create_meta(new=True):
                logger.warning('Erro grave, pulando %s', media.source_filepath)
                continue
            cbm.update_db(media)
            n_new += 1
        else:
            if not force_update and query == 2:
                # Se registro existir e timestamp for igual
                logger.info('REGISTRO ATUALIZADO NO SITE! PRÓXIMO...')
                pass
            else:
                # Se arquivo do site não estiver atualizada
                if force_update:
                    logger.info('REGISTRO ATUALIZADO, MAS SOB FORCE_UPDATE.')
                else:
                    logger.info('REGISTRO NÃO ESTÁ ATUALIZADO. ATUALIZANDO...')
                media.create_meta()
                cbm.update_db(media, update=True)
                n_up += 1
    n = len(filepaths)

    # Create file for Veliger autocomplete.
    build_autocomplete()

    # Estatísticas.
    print '\n%d ARQUIVOS ANALISADOS' % n
    print '%d novos' % n_new
    print '%d atualizados' % n_up
    t = int(time.time() - t0)
    if t > 60:
        print '\nTempo de execução:', t / 60, 'min', t % 60, 's'
    else:
        print '\nTempo de execução:', t, 's'
    print
    logger.info('%ds: %d analisados, %d novos, %d atualizados',
            t, n, n_new, n_up)

# Início do programa
if __name__ == '__main__':
    # Criando o logger.
    logger = logging.getLogger('cifonauta')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # Define formato das mensagens.
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s @ %(module)s %(funcName)s (l%(lineno)d): %(message)s')

    # Cria o manipulador do console.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # Define a formatação para o console.
    console_handler.setFormatter(formatter)
    # Adiciona o console para o logger.
    logger.addHandler(console_handler)

    # Cria o manipulador do arquivo.log.
    file_handler = logging.FileHandler('logs/cifonauta.log')
    file_handler.setLevel(logging.DEBUG)
    # Define a formatação para o arquivo.log.
    file_handler.setFormatter(formatter)
    # Adiciona o arquivo.log para o logger.
    logger.addHandler(file_handler)

    # Marca a hora inicial
    t0 = time.time()
    logger.info('Cifonauta iniciando...')
    # Inicia função principal, lendo os argumentos (se houver)
    main(sys.argv[1:])
