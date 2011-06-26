#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import pickle
from iptcinfo import IPTCInfo

# Instancia logger do cifonauta.
logger = logging.getLogger('cifonauta.linking')

sources = []

def get_paths(folder):
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
    return filepaths

def standardize_path(linkpath):
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

def check_link(linkpath):
    '''Verifica se o link simbólico está quebrado ou não.'''
    try:
        if os.lstat(linkpath):
            return True
    except:
        logger.debug('Link quebrado: %s', linkpath)
        return False

def fixlink(tofix):
    '''Corrige o link.

    Fazer teste.
    '''
    for sourcepath, linkpath in tofix.iteritems():
        logger.debug('Corrigindo: %s', linkpath)
        logger.debug('Para: %s', sourcepath)

        # Instancia nome do link.
        linkname = os.path.basename(linkpath)

        # Padroniza o caminho relativo do link.
        relative_path = standardize_path(sourcepath)

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

        return final_link

def get_matches(link):
    '''Compara nome do arquivo original com o link.'''
    matches = []
    # Compara o destino do link com a lista de arquivos originais.
    for source in sources:
        if os.path.basename(link) == os.path.basename(source):
            # Se os nomes forem iguais o arquivo perdido pode ter
            # mudado de pasta.
            logger.debug('Encontrado suposto arquivo perdido: %s', source)
            matches.append(source)
    return matches

def handle_broken(broken_links):
    '''Processa links quebrados, tentando arrumar.

    Retorna dicionário com arquivos para arrumar e arquivos perdidos.
    '''
    logger.info('Existem links quebrados.')
    lost = {}
    tofix = {}
    for k, v in broken_links.iteritems():
        logger.debug('%s -> %s', k, v)
        matches = get_matches(v)
        # Se não encontrar candidados o arquivo deve ter sido deletado.
        if not matches:
            logger.debug('Nenhum candidato para %s foi encontrado!', v)
            # Adiciona para a lista de perdidos.
            lost[k] = v
        else:
            logger.debug('%s mudou de lugar.', v)
            # Imprime opções na tela.
            print 'Indique a imagem correspondente no diretório oficial:\n'
            for idx, val in enumerate(matches):
                print '\t[%d] ' % idx + val
            index = raw_input('\nDigite o número da imagem certa ' \
                    '("i" para ignorar; "l" para perdidas): ')
            # Lida com input do usuário.
            if index == 'i':
                logger.debug('Ignorando o link quebrado: %s.', v)
            elif index == 'l':
                logger.debug('Imagem perdida: %s', v)
                lost[k] = v
            elif not index.strip():
                logger.debug('Valor vazio, tente novamente.')
                print 'Valor vazio, tente novamente.'
            elif int(index) > len(matches) - 1:
                logger.debug('Número inválido, tente novamente.')
                print 'Número inválido, tente novamente.'
            else:
                logger.debug('Link %s será arrumado.', matches[int(index)])
                tofix[matches[int(index)]] = k
    return tofix, lost

def add_new(links):
    '''Cria links para os arquivos novos.'''
    # Seleciona arquivos de mídia que não tem links.
    diff = set(sources) - set(links)
    if diff:
        logger.info('%s novos links serão criados', len(diff))
        for filepath in diff:
            linkpath = standardize_path(filepath)
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

    # Diretório de trabalho do cifonauta com links para pasta oficial.
    source_media = 'source_media/oficial'
    # Diretório oficial com arquivos originais.
    storage = '/home/nelas/storage/oficial'

    links = []
    broken_links = {}

    # Pega lista de arquivos.
    filepaths = get_paths(source_media)

    # Checa se não houve algum problema.
    if not filepaths:
        logger.exception('Nenhum arquivo encontrado na pasta source_media.')

    # Verifica links quebrados e adiciona à lista correspondente.
    for filepath in filepaths:
        linkpath = os.readlink(filepath)
        if check_link(linkpath):
            links.append(linkpath)
        else:
            broken_links[filepath] = linkpath

    # Cria lista de arquivos de mídia
    sourcepaths = get_paths(storage)

    # Checa se não houve algum problema.
    if not sourcepaths:
        logger.exception('Nenhum arquivo encontrado na pasta oficial.')

    # Adiciona à lista de arquivos fonte.
    for filepath in sourcepaths:
        sources.append(filepath)

    # Tenta dar um jeito nos links quebrados
    if broken_links:
        tofix, lost = handle_broken(broken_links)
        if tofix:
            logger.info('Corrigindo links.')
            final_link = fixlinks(tofix)
            if check_link(final_link):
                # Necessário para fazer a comparação no add_new.
                links.append(final_link)
            else:
                logger.debug('Link recém criado com problemas: %s',
                        final_link)
        if lost:
            logger.debug('%s arquivos perdidos', len(lost))
            for k, v in lost.iteritems():
                logger.debug('Perdidos: %s -> %s', k, v)
            #TODO Deletar entradas no banco de dados a partir daqui?
    else:
        logger.info('Nenhum link quebrado.')

    # Adiciona links para os arquivos novos
    add_new(links)

# Início do programa
if __name__ == '__main__':
    main()
