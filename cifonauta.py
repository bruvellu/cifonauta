#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CIFONAUTA
# Copyleft 2010 - Bruno C. Vellutini | organelas.ccom
#
#TODO Inserir licença.
#
# Atualizado: 19 Jun 2010 09:08PM
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

# Diretório com as imagens
sourcedir = 'fotos'
# Diretório espelho do site (imagens já carregadas)
webdir = 'site_media/images'
thumbdir = 'site_media/images/thumbs'
localdir = 'localweb'
local_thumbdir = 'localweb/thumbs'
# Arquivo com marca d'água
watermark = 'marca.png'


class Database:
    '''Define objeto que interage com o banco de dados.'''
    def __init__(self):
        pass

    def search_db(self, filename, timestamp):
        '''Busca o registro no banco de dados pelo nome do arquivo.
        
        Se encontrar, compara a data de modificação do arquivo e do registro.
        Se as datas forem iguais pula para a próxima imagem, se forem diferentes
        atualiza o registro.
        '''
        print '\nVerificando se a imagem está no banco de dados...'
        
        try :
            record = Image.objects.get(web_filepath__icontains=filename)
            print 'Bingo! Registro de %s encontrado.' % filename
            print 'Comparando a data de modificação do arquivo com o registro...'
            # Corrige timestamps para poder comparar.
            #timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if record.timestamp != timestamp:
                print 'Arquivo mudou!'
                return 1
            else:
                print 'Arquivo não mudou!'
                return 2
        except Image.DoesNotExist:
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

        # Transforma valores em instâncias dos modelos
        toget = ['author', 'taxon', 'genus', 'species', 'size', 'source',
                'rights', 'sublocation', 'city', 'state', 'country']
        for k in toget:
            if k == 'genus':
                image_meta[k] = self.get_instance(k, image_meta['genus_sp'][0])
            elif k == 'species':
                image_meta[k] = self.get_instance(k, image_meta['genus_sp'][1])
            else:
                image_meta[k] = self.get_instance(k, image_meta[k])
        del image_meta['genus_sp']
        
        # Conectando espécie e gênero.
        image_meta['species'].parent = image_meta['genus']
        image_meta['species'].save()

        if not update:
            image_meta['view_count'] = 0
            entry = Image(**image_meta)
            # Tem que salvar para criar id, usado na hora de salvar as tags
            entry.save()
        else:
            entry = Image.objects.get(web_filepath__icontains=filename)
            for k, v in image_meta.iteritems():
                setattr(entry, k, v)

        # Atualiza marcadores
        tag_instances = [self.get_instance('tag', tag) for tag in tags]
        entry.tag_set.clear()
        [entry.tag_set.add(tag) for tag in tag_instances]

        # Salvando modificações
        entry.save()

        print 'Registro no banco de dados atualizado!'

    def get_instance(self, table, value, genus=''):
        '''Retorna o id a partir do nome.'''
        metadatum, new = eval('%s.objects.get_or_create(name="%s")' %
                (table.capitalize(), value))
        return metadatum


class Photo:
    '''Define objeto para instâncias das fotos.'''
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
        copy(thumb_localfilepath, thumbdir)
        thumb_filepath = os.path.join(thumbdir, thumbname)
        return thumb_filepath


class Folder:
    '''Define objeto para lidar com as pastas a serem lidas.'''
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
        o = []
        # Buscador de imagens em ação
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if filename.endswith(extensions) and n < self.n_max:
                    filepath = os.path.join(root, filename)
                    self.images.append(filepath)
                    o.append(filename)
                    n += 1
                    continue
                elif filename.endswith(to_ignore):
                    print 'Ignorando %s' % filename
                    continue
                else:
                    print 'Nome do último arquivo: %s' % filename
                    break
        else:
            print '\n%d imagens encontradas.' % n
        # Cria lista com nome dos arquivos da pasta
        i = os.listdir(self.folder_path)
        # Verifica as diferenças...
        diff = set(i) - set(o)
        # Grava no arquivo...
        #FIXME Tentar descobrir por que acontece isso!
        loucura = open('loucura.txt', 'w')
        for nome in diff:
            loucura.write(nome + '\n')

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
    cbm = Database()

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
