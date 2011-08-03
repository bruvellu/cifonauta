#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import pickle
from iptcinfo import IPTCInfo
from remove import compile_paths
from meta.models import Image, Video

# Instancia logger do cifonauta.
logger = logging.getLogger('cifonauta.linking')


class LinkManager:
    def __init__(self):
        # Diretório com links para pasta oficial.
        self.source_media = 'source_media/oficial'
        # Diretório oficial com arquivos originais.
        self.storage = '/home/nelas/storage/oficial'

        # Listas para processamento.
        self.links = []
        self.broken_links = {}
        self.tofix = {}
        self.lost = {}

        # Lista de arquivos originais.
        self.sources = self.get_paths(self.storage)

        # Pega lista de arquivos.
        self.filepaths = self.get_paths(self.source_media)
        self.deal_links(self.filepaths)

    def get_paths(self, folder):
        '''Busca arquivos recursivamente na pasta indicada.

        >>> folder = 'source_media/oficial'
        >>> filepaths = get_paths(folder)
        >>> isinstance(filepaths, list)
        True
        '''
        filepaths = []
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if not filename.endswith('~') or not filename.endswith('.txt'):
                    filepath = os.path.join(root, filename)
                    filepaths.append(filepath)
                else:
                    continue
            else:
                continue
        else:
            logger.info('%s arquivos na pasta %s.', len(filepaths), folder)

        # Checa se não houve algum problema.
        if not filepaths:
            logger.exception('Pasta %s vazia?', folder)
        return filepaths

    def deal_links(self, paths):
        '''Verifica links quebrados e adiciona à lista correspondente.'''
        for path in paths:
            linkpath = os.readlink(path)
            if self.check_link(linkpath):
                self.links.append(linkpath)
                logger.debug('Link saudável: %s', linkpath)
            else:
                self.broken_links[path] = linkpath
                logger.debug('Link quebrado: %s', linkpath)

    def handle_broken(self):
        '''Processa links quebrados, tentando arrumar.

        Retorna dicionário com arquivos para arrumar e arquivos perdidos.
        '''
        if self.broken_links:
            logger.info('Existem links quebrados.')
            for k, v in self.broken_links.iteritems():
                logger.debug('%s -> %s', k, v)
                matches = self.get_matches(v)
                # Se não encontrar candidados o arquivo deve ter sido deletado.
                if not matches:
                    logger.debug('Nenhum candidato para %s foi encontrado!', v)
                    # Adiciona para a lista de perdidos.
                    self.lost[k] = v
                else:
                    logger.debug('%s mudou de lugar.', v)
                    # Imprime opções na tela.
                    print 'Indique a imagem correspondente no diretório oficial:\n'
                    print '\t%s\n' % v
                    for idx, val in enumerate(matches):
                        print '\t[%d] ' % idx + val
                    index = raw_input('\nDigite o número da imagem certa ' \
                            '("i" para ignorar; "l" para perdidas): ')
                    # Lida com input do usuário.
                    if index == 'i':
                        logger.debug('Ignorando o link quebrado: %s.', v)
                    elif index == 'l':
                        logger.debug('Imagem perdida: %s', v)
                        self.lost[k] = v
                    elif not index.strip():
                        logger.debug('Valor vazio, tente novamente.')
                        print 'Valor vazio, tente novamente.'
                    elif int(index) > len(matches) - 1:
                        logger.debug('Número inválido, tente novamente.')
                        print 'Número inválido, tente novamente.'
                    else:
                        logger.debug('Link %s será arrumado.', matches[int(index)])
                        self.tofix[matches[int(index)]] = k
        else:
            logger.info('Nenhum link quebrado.')


    def get_matches(self, link):
        '''Compara nome do arquivo original com o link.'''
        matches = []
        # Compara o destino do link com a lista de arquivos originais.
        for source in self.sources:
            if os.path.basename(link) == os.path.basename(source):
                # Se os nomes forem iguais o arquivo perdido pode ter
                # mudado de pasta.
                logger.debug('Encontrado suposto arquivo perdido: %s', source)
                matches.append(source)
        return matches

    def check_link(self, linkpath):
        '''Verifica se o link simbólico está quebrado ou não.'''
        try:
            if os.lstat(linkpath):
                return True
        except:
            logger.debug('Link quebrado: %s', linkpath)
            return False

    def fixlinks(self):
        '''Corrige o link.

        Fazer teste.
        '''
        if self.tofix:
            logger.info('Corrigindo links.')
            for sourcepath, linkpath in self.tofix.iteritems():
                logger.debug('Corrigindo: %s', linkpath)
                logger.debug('Para: %s', sourcepath)

                # Instancia nome do link.
                linkname = os.path.basename(linkpath)

                # Padroniza o caminho relativo do link.
                relative_path = self.standardize_path(sourcepath)

                # Junta link relativo com o nome único do link.
                relative_link = os.path.join(os.path.dirname(relative_path), linkname)
                # Define o caminho final acrescentando o source_media.
                final_link = os.path.join('source_media', relative_link)

                # Renomeia movendo o arquivo e limpando pastas vazias
                os.renames(linkpath, final_link)
                # Remove o arquivo para poder criar o link atualizado
                os.remove(final_link)
                # Cria link simbólico atualizado
                os.symlink(sourcepath, final_link)

            if self.check_link(final_link):
                # Necessário para fazer a comparação no add_new.
                self.links.append(final_link)
            else:
                logger.debug('Link recém criado com problemas: %s',
                        final_link)
        else:
            logger.debug('Nenhum link para arrumar...')


    def standardize_path(self, linkpath):
        '''Padroniza caminho dos links usando a pasta oficial como base.

        >>> path = '/home/nelas/storage/oficial/Vellutini/Clypeaster/DSCN1999.JPG'
        >>> standardize_path(path)
        'oficial/Vellutini/Clypeaster/DSCN1999.JPG'
        '''
        # Separa pastas por separador.
        linklist = linkpath.split(os.sep)
        try:
            # Estabelece o ponto onde o link será cortado.
            ponto = linklist.index('oficial')
            del linklist[:ponto]
            return os.path.join(*linklist)
        except:
            logger.debug('Algo errado com o caminho %.', linkpath)
            return None

    def handle_lost(self):
        '''Lida com arquivos perdidos.'''
        if self.lost:
            logger.info('%s arquivos perdidos', len(self.lost))
            for k, v in self.lost.iteritems():
                logger.debug('Perdidos: %s -> %s', k, v)
                name = os.path.basename(k)
                if name.endswith('txt'):
                    logger.debug('Apagando arquivo txt: %s', name)
                    os.remove(k)
                try:
                    media = Image.objects.get(web_filepath__icontains=name)
                except:
                    try:
                        media = Video.objects.get(webm_filepath__icontains=name)
                    except:
                        logger.debug('Nenhuma imagem com nome %s', name)
                        continue
                if media:
                    try:
                        paths = compile_paths(media)
                        confirm = raw_input('Confirma? (s ou n): ')
                        if confirm == 's':
                            try:
                                media.delete()
                                logger.debug('Entrada de %s foi apagada!', media)
                            except:
                                logger.warning(
                                        'Não rolou apagar %s do banco de dados', 
                                        media)
                            for path in paths:
                                try:
                                    os.remove(path)
                                    logger.debug('%s foi apagado!', path)
                                except:
                                    logger.warning('%s não foi apagado!', path)
                    except:
                        logger.debug('Algo errado na hora de ler a imagem.')
        else:
            logger.info('Nenhum arquivo para ser deletado.')


    def add_new(self):
        '''Cria links para os arquivos novos.'''
        # Seleciona arquivos de mídia que não tem links.
        diff = set(self.sources) - set(self.links)
        if diff:
            logger.info('%s novos links serão criados', len(diff))
            for filepath in diff:
                linkpath = self.standardize_path(filepath)
                linkpath = os.path.join('source_media', linkpath)
                # Cria diretórios necessários.
                try:
                    os.makedirs(os.path.dirname(linkpath))
                except OSError:
                    logger.debug('Diretório %s já existe.', linkpath)
                # Remove possível arquivo duplicado.
                try:
                    os.remove(linkpath)
                except:
                    logger.debug('Arquivo %s é novo mesmo.', linkpath)
                # Cria o link, enfim.
                try:
                    os.symlink(filepath, linkpath)
                except:
                    logger.debug('Link não pode ser criado: %s -> %s',
                            filepath, linkpath)
        else:
            logger.info('Nenhum arquivo novo.')

def main():
    logger.info('Verificando links da pasta oficial...')

    # Instancia o manager.
    manager = LinkManager()

    # Tenta dar um jeito nos links quebrados
    manager.handle_broken()
    manager.fixlinks()
    # Dá um jeito nos arquivos perdidos.
    manager.handle_lost()
    # Adiciona links para os arquivos novos.
    manager.add_new()

# Início do programa
if __name__ == '__main__':
    main()
