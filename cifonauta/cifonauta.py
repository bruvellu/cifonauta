#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CIFONAUTA
# Copyleft 2010 - Bruno C. Vellutini | organelas.ccom
#
#TODO Inserir licença.
#
# Atualizado: 07 May 2010 12:31AM
'''Gerenciador do Banco de imagens do CEBIMar-USP.

Este programa gerencia as imagens do banco de imagens do CEBIMar lendo seus
metadados, reconhecendo marquivos modificados e atualizando o website.

Centro de Biologia Marinha da Universidade de São Paulo.
'''

import os
import sys
import subprocess
import time
import getopt

import pg

from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from shutil import copy
from iptcinfo import IPTCInfo

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.6'
__maintainer__ = 'Bruno Vellutini'
__email__ = 'organelas at gmail dot com'
__status__ = 'Development'

# Diretório com as imagens
sourcedir = 'fotos'
# Diretório espelho do site (imagens já carregadas)
webdir = 'site_media/images'
thumbdir = 'site_media/images/thumbs'
localdir = 'web'
local_thumbdir = 'web/thumbs'
# Arquivo com marca d'água
watermark = 'marca.png'


class Database:
    def __init__(self, name, user):
        try:
            self.db = pg.DB(dbname=name, user=user)
        except:
            print 'O CIFONAUTA não conseguiu se conectar ao banco:'
            print '\n\tNome: %s' % name
            print '\n\tUsuário: %s' % user

    def search_db(self, filename, timestamp):
        '''Busca o registro no banco de dados pelo nome do arquivo.
        
        Se encontrar, compara a data de modificação do arquivo e do registro.
        Se as datas forem iguais pula para a próxima imagem, se forem diferentes
        atualiza o registro.
        '''
        print '\nVerificando se a imagem está no banco de dados...'

        record = self.db.query(
            '''
            SELECT web_filepath, timestamp
            FROM meta_image
            WHERE web_filepath ILIKE '%%%s';
            ''' % filename).dictresult()

        # Se o registro existir
        if record:
            print 'Bingo! Registro de %s encontrado.' % filename
            print 'Comparando a data de modificação do arquivo com o registro...'
            # Corrige timestamps para poder comparar.
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            db_timestamp = record[0]['timestamp'].split('.')
            db_timestamp = db_timestamp[0]

            if db_timestamp != timestamp:
                print '%s != %s' % (db_timestamp, timestamp)
                print 'Arquivo mudou!'
                return 1
            else:
                print '%s = %s' % (db_timestamp, timestamp)
                print 'Arquivo não mudou!'
                return 2
        else:
            print 'Registro não encontrado.'
            return False

    def update_db(self, image_meta, update=False):
        '''Cria ou atualiza registro no banco de dados.'''
        print '\nAtualizando o banco de dados...'
        # Atualizando imagens
        filename = os.path.basename(image_meta['web_filepath'])
        # Guarda objeto com tags
        tags = image_meta['tags']
        del image_meta['tags']

        # Não deixar imagem pública se faltar título ou autor
        if image_meta['title'] == '' or image_meta['author'] == '':
            print 'Imagem sem título ou autor!'
            image_meta['is_public'] = False
        else:
            image_meta['is_public'] = True

        # Transforma valores em IDs
        toget = ['author', 'taxon', 'genus', 'species', 'size', 'source',
                'rights', 'sublocation', 'city', 'state', 'country']
        for k in toget:
            new_k = '%s_id' % k
            if k == 'genus':
                image_meta[new_k] = self.getrow_id(k, image_meta['genus_sp'][0])
            elif k == 'species':
                image_meta[new_k] = self.getrow_id(k, image_meta['genus_sp'][1])
            else:
                image_meta[new_k] = self.getrow_id(k, image_meta[k])
                del image_meta[k]
        del image_meta['genus_sp']

        if not update:
            image_meta['view_count'] = 0
            entry = self.db.insert('meta_image', image_meta)
            entry = self.db.get(
                    'meta_image', image_meta['source_filepath'],
                    'source_filepath')
        else:
            image_id = self.db.query(
                    '''
                    SELECT id FROM meta_image
                    WHERE web_filepath ILIKE '%%%s';
                    ''' % filename
                    ).dictresult()
            image_meta['id'] = image_id[0]['id']
            entry = self.db.update('meta_image', image_meta)

        # Atualiza marcadores
        if tags:
            tag_ids = [self.getrow_id('tag', tag) for tag in tags]
            old_tag_ids = self.db.query(
                        '''
                        SELECT tag_id
                        FROM meta_tag_images
                        WHERE image_id = %d;
                        ''' % entry['id']).dictresult()
            old_tag_ids = [tag['tag_id'] for tag in old_tag_ids]
            tags_to_unlink = set(old_tag_ids) - set(tag_ids)
            for tag_id in tags_to_unlink:
                tag_image_id = self.db.query(
                        '''
                        SELECT id
                        FROM meta_tag_images
                        WHERE image_id = %d
                        AND tag_id = %d;''' % (entry['id'], tag_id)).dictresult()
                self.db.delete('meta_tag_images', {'id': tag_image_id[0]['id']})
            for tag_id in tag_ids:
                tag_image_id = self.db.query(
                        '''
                        SELECT id
                        FROM meta_tag_images
                        WHERE image_id = %d
                        AND tag_id = %d;''' % (entry['id'], tag_id)).dictresult()
                if not tag_image_id:
                    self.db.insert('meta_tag_images', {
                        'tag_id': tag_id, 'image_id': entry['id']})
                else:
                    pass

        print 'Registro no banco de dados atualizado!'

    def getrow_id(self, table, value):
        '''Retorna o id a partir do nome.'''
        try:
            row = self.db.get('meta_%s' % table, value, 'name')
        except:
            newrow = self.db.insert('meta_%s' % table, {'name': u'%s' % value,
                'slug': ''})
            row = self.db.get('meta_%s' % table, value, 'name')
        id = row['id']
        return id


class Photo:
    def __init__(self, filepath):
        self.source_filepath = filepath
        self.filename = os.path.basename(filepath)
        self.timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))

    def create_meta(self, charset='utf-8'):
        '''Define as variáveis extraídas dos metadados (IPTC) da imagem.

        Usa a biblioteca do arquivo iptcinfo.py.
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
                
        # Converte valores None para string em branco
        # FIXME Checar se isso está funcionando direito...
        for k, v in self.meta.iteritems():
            if v is None:
                self.meta[k] = u''

        # Preparando a espécie para o banco de dados
        genus_sp = self.meta['genus_sp'].split()
        if not genus_sp:
            genus_sp.extend(['', ''])
        elif len(genus_sp) == 1:
            if genus_sp[0] == '':
                genus_sp.append('')
            else:
                genus_sp.append('sp.')
        self.meta['genus_sp'] = genus_sp

        # Extraindo metadados do EXIF
        exif = self.get_exif(self.source_filepath)
        date = self.get_date(exif)
        if date:
            self.meta['date'] = date
        else:
            self.meta['date'] = ''
        # Arrumando geolocalização
        try:
            gps = self.get_gps(exif['GPSInfo'])
            for k, v in gps.iteritems():
                self.meta[k] = v
        except:
            self.meta['geolocation'] = ''
            self.meta['latitude'] = ''
            self.meta['longitude'] = ''

        # Processar imagem
        #FIXME ARRUMAR TODOS OS OBJETOS PRA FUNCIONAR!
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
        print '\tEspécie:\t%s' % ' '.join(self.meta['genus_sp'])
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

    def get_exif(self, filename):
        tagnames = ['GPSInfo', 'DateTimeOriginal', 'DateTimeDigitized',
                'DateTime']
        exif = {}
        img = Image.open(filename)
        info = img._getexif()
        for tag, value in info.iteritems():
            tagname = TAGS.get(tag, tag)
            if tagname in tagnames:
                exif[tagname] = value
        return exif

    def get_gps(self, data):
        gps = {}
        divide = lambda x: x[0] / x[1]
        # Latitude
        lat_ref = data[1]
        lat_deg = divide(data[2][0])
        lat_min = divide(data[2][1])
        lat_sec = divide(data[2][2])
        lat_sec_float = data[2][2][0] / float(data[2][2][1])
        latitude = self.get_decimal(
                lat_deg, lat_min, lat_sec_float)
        # Longitude
        long_ref = data[3]
        long_deg = divide(data[4][0])
        long_min = divide(data[4][1])
        long_sec = divide(data[4][2])
        long_sec_float = data[4][2][0] / float(data[4][2][1])
        longitude = self.get_decimal(
                long_deg, long_min, long_sec_float)

        gps['geolocation'] = '%s %d°%d"%d\' %s %d°%d"%d\'' % (
                lat_ref, lat_deg, lat_min, lat_sec, long_ref, long_deg,
                long_min, long_sec)
        gps['latitude'] = '%s%f' % (lat_ref, latitude)
        gps['longitude'] = '%s%f' % (long_ref, longitude)
        return gps

    def get_decimal(self, deg, min, sec):
	decimal_min = (min * 60.0 + sec) / 60.0
	decimal = (deg * 60.0 + decimal_min) / 60.0
        return decimal

    def get_date(self, exif):
        try:
            date = exif['DateTimeOriginal']
        except:
            try:
                date = exif['DateTimeDigitized']
            except:
                try:
                    date = exif['DateTime']
                except:
                    return False

        date = datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        return date

    def process_image(self):
        '''Redimensiona a imagem e inclui marca d'água.'''
        local_filepath = os.path.join(localdir, self.filename)
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
            web_filepath = os.path.join(webdir, self.filename)
            copypath = os.path.join('weblarvae', web_filepath)
            copy(local_filepath, copypath)
        except IOError:
            print '\nOcorreu algum erro na conversão da imagem. Verifique se o ' \
                    'ImageMagick está instalado.'
        else:
            print 'Imagem convertida com sucesso! Criando thumbnails...'
            thumb_filepath = self.create_thumbs()
            return web_filepath, thumb_filepath

    def create_thumbs(self):
        '''Cria thumbnails para as fotos novas.'''
        filename_noext = self.filename.split('.')[0]
        thumbname = filename_noext + '.png'
        thumb_localfilepath = os.path.join(local_thumbdir, thumbname)
        try:
            #TODO arrumar
            subprocess.call(['convert', '-define', 'jpeg:size=200x150',
                self.source_filepath, '-thumbnail', '120x90^', '-gravity', 'center',
                '-extent', '120x90', 'PNG8:%s' % thumb_localfilepath])
        except IOError:
            print 'Não consegui criar o thumbnail...'
        #XXX Dar um jeito de melhorar isso...
        copypath = os.path.join('weblarvae', thumbdir)
        copy(thumb_localfilepath, copypath)
        thumb_filepath = os.path.join(thumbdir, thumbname)
        return thumb_filepath


class Folder:
    def __init__(self, folder, n_max):
        self.folder_path = folder
        self.n_max = n_max
        self.images = []

    def get_images(self):
        '''Busca recursivamente arquivos com extensão .jpg.'''
        n = 0
        # Tupla para o endswith()
        extensions = ('jpg', 'JPG', 'jpeg', 'JPEG')
        to_ignore = ('~')
        # Buscador de imagens em ação
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if filename.endswith(extensions) and n < self.n_max:
                    filepath = os.path.join(root, filename)
                    self.images.append(filepath)
                    n += 1
                    continue
                elif filename.endswith(to_ignore):
                    print 'Ignorando %s' % filename
                    continue
            else:
                print '\n%d imagens encontradas.' % n
                break
        return self.images


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
    print '\tEspecifica um número máximo de imagens que o programa irá ' \
            'verificar.'
    print
    print '  -f, --force-update'
    print '\tAtualiza banco de dados e refaz thumbnails de todas as imagens, '
    print '\tinclusive as que não foram modificadas.'
    print
    print 'Exemplo:'
    print '  python cifonauta.py -f -n 15'
    print '\tFaz a atualização forçada das primeiras 15 imagens que o programa'
    print '\tencontrar na pasta padrão (sourcedir; ver código).'
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
        print '\n%d imagens serão atualizadas de forma forçada.' % n_max
        print '(argumento "-f" utilizado)'
    else:
        print '\n%d imagens serão verificadas e registradas no banco de ' \
                'dados.' % n_max

    # Cria o arquivo log
    logname = 'log_%s' % time.strftime('%Y.%m.%d_%I:%M:%S', time.localtime())
    log = open(logname, 'a+b')

    # Checar se diretório web existe antes de começar
    if os.path.isdir(localdir) is False:
        os.mkdir(localdir)
    if os.path.isdir(local_thumbdir) is False:
        os.mkdir(local_thumbdir)

    # Cria instância do bd
    cbm = Database(name='cebimar', user='nelas')

    # Inicia o cifonauta buscando pasta...
    folder = Folder(sourcedir, n_max)
    image_paths = folder.get_images()
    for path in image_paths:
        image = Photo(path)
        query = cbm.search_db(image.filename, image.timestamp)
        if not query:
            # Se imagem for nova
            print '\nIMAGEM NOVA, CRIANDO ENTRADA NO BANCO DE DADOS...'
            image.create_meta()
            cbm.update_db(image.meta)
            n_new += 1
        else:
            if not force_update and query == 2:
                # Se registro existir e timestamp for igual
                print '\nREGISTRO EXISTE E ESTÁ ATUALIZADO NO SITE! ' \
                        'PRÓXIMA IMAGEM...'
                pass
            else:
                # Se imagem do site não estiver atualizada
                if force_update:
                    print '\nREGISTRO EXISTE E ESTÁ ATUALIZADO, MAS '\
                            'RODANDO SOB ARGUMENTO "-f".'
                else:
                    print '\nREGISTRO EXISTE, MAS NÃO ESTÁ ATUALIZADO. ' \
                            'ATUALIZANDO O BANCO DE DADOS...'
                image.create_meta()
                cbm.update_db(image.meta, update=True)
                n_up += 1
    n = len(image_paths)
    
    # Deletando arquivo log se ele estiver vazio
    if log.read(1024) == '':
        #Fechando a imagem
        log.close()
        # Deletando log vazio
        os.remove(logname)
    else:
        # Fechando arquivo de log
        log.close()
    
    print '\n%d IMAGENS ANALISADAS' % n
    print '%d novas imagens' % n_new
    print '%d imagens atualizadas' % n_up
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
