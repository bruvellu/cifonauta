#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from iptcinfo import IPTCInfo

storage = '/home/nelas/storage/oficial'
source_media = 'source_media/oficial'

sources = []
links = []
broken_links = {}

def stand_path(link_path):
    '''Padroniza caminho dos links.'''
    link_list = link_path.split(os.sep)
    try:
        ponto = link_list.index('oficial')
        del link_list[:ponto]
        return os.path.join(*link_list)
    except:
        print 'Algo está errado com o nome das pastas.'

def deal_links(filepath):
    '''Lida com caminhos a partir do nome da pasta oficial'''
    link_path = os.readlink(filepath)
    try:
        if os.lstat(link_path):
            links.append(link_path)
    except:
        print '%s é um link quebrado!' % link_path 
        broken_links[filepath] = link_path

def fixlink(pre_path, linkpath):
    '''Corrige o link.'''
    print '\nCorrigindo:'
    print '\t%s' % linkpath
    print 'Para:'
    print '\t%s' % pre_path
    # Instancia nome do link
    linkname = os.path.basename(linkpath)
    # Processa o link final
    rel_link = stand_path(pre_path)
    new_link = os.path.join(os.path.dirname(rel_link), linkname)
    final_link = os.path.join('source_media', new_link)
    # Renomeia movendo o arquivo e limpando pastas vazias
    os.renames(linkpath, final_link)
    # Remove o arquivo para poder criar o link atualizado
    os.remove(final_link)
    # Cria link simbólico atualizado
    os.symlink(pre_path, final_link)
    # Chama função que adicionará à lista de links
    deal_links(final_link)

def get_links():
    '''Recursivamente verifica os links.
    
    Salva links numa lista e links quebrados em outra.
    '''
    print '\nLINKS'
    total = 0
    for root, dirs, files in os.walk(source_media):
        for filename in files:
            filepath = os.path.join(root, filename)
            deal_links(filepath)
            total += 1
        else:
            continue
    else:
        print '%d arquivos' % total

def temp_spp(filepath):
    '''Copia campo de espécies para táxons (IPTC).
    
    Função criada para converter espécies para táxons. Necessária após a unificação taxonômica. Não será mais usada.
    '''
    info = IPTCInfo(filepath, True, 'utf-8') 
    if info.data['original transmission reference']:
        print 'ESPÉCIES PERDIDAS!'
        print info.data['original transmission reference']
        print 'TÁXONS!'
        print info.data['headline']

        info.data['headline'] = info.data['original transmission reference']
        info.data['original transmission reference'] = ''
        print
        print info.data['headline']
        print info.data['original transmission reference']
        info.save()
        #import pdb; pdb.set_trace()

def get_media():
    '''Recursivamente identifica os arquivos de mídia.'''
    print '\nOFICIAIS'
    total = 0
    for root, dirs, files in os.walk(storage):
        for filename in files:
            # Exclui arquivos acessórios dos vídeos.
            #FIXME Não estou conseguindo excluir os .txt...
            if not filename.endswith('~') or not filename.endswith('.txt'):
                filepath = os.path.join(root, filename)
                #temp_spp(filepath)
                sources.append(filepath)
                total += 1
            else:
                continue
        else:
            continue
    else:
        print '%d arquivos' % total

def fix_broken():
    '''Processa links quebrados, tentando arrumar.'''
    if broken_links:
        print '\nBROKEN LINKS'
        lost = {}
        for k, v in broken_links.iteritems():
            print
            print k + ' -> ' + v
            potencial = []
            for i in sources:
                if os.path.basename(v) == os.path.basename(i):
                    print '\nENCONTRADO SUPOSTO ARQUIVO PERDIDO:'
                    print i
                    potencial.append(i)
            if not potencial:
                print 'Nenhum candidato a este link foi encontrado!'
                #TODO Documentar tudo isso pra não esquecer como funciona.
                lost[k] = v
            elif len(potencial) == 1:
                print 'Apenas um candidato, corrigindo o link...'
                fixlink(potencial[0], k)
            elif len(potencial) > 1:
                print
                print 'A imagem abaixo mudou de lugar e quebrou o link.'
                print
                print '\t' + v
                print
                print 'Como mais de um arquivo com o mesmo nome foi encontrado' \
                        ', indique a imagem correspondente no diretório oficial.'
                print
                for idx, val in enumerate(potencial):
                    print '\t[%d] ' % idx + val
                index = raw_input('\nDigite o número da imagem certa ' \
                        '("i" para ignorar; "l" para perdidas): ')
                if index == 'i':
                    print 'Ignorando... o erro será anunciado novamente.'
                elif index == 'l':
                    print 'Imagem perdida, e agora?'
                    print k, v
                    lost[k] = v
                elif not index.strip():
                    print 'Valor vazio, tente novamente.'
                elif int(index) > len(potencial) - 1:
                    print 'Número inválido, tente novamente.'
                else:
                    print 'Eureka, vamos arrumar o link %s' % potencial[int(index)]
                    fixlink(potencial[int(index)], k)
        print lost
        if lost:
            print 'LOST'
            file = open('to_del', 'wb')
            for k, v in lost.iteritems():
                print k + ' -> ' + v
            pickle.dump(lost, file)
            file.close()
    else:
        print '\nNenhum link quebrado.'

def add_new():
    '''Cria links para os arquivos novos.'''
    # Seleciona arquivos de mídia que não tem links.
    diff = set(sources) - set(links)
    if diff:
        print '\nNOVAS'
        for filepath in diff:
            print filepath
            linkpath = stand_path(filepath)
            linkpath = os.path.join('source_media', linkpath)
            try:
                os.makedirs(os.path.dirname(linkpath))
            except OSError:
                print 'Diretório já existe.'
            try:
                os.remove(linkpath)
            except:
                print 'Arquivo ainda não existe.'
            os.symlink(filepath, linkpath)
    else:
        print 'Nenhum arquivo novo.'

def main():
    # Cria lista de links
    get_links()
    # Cria lista de arquivos de mídia
    get_media()
    # Tenta dar um jeito nos links quebrados
    fix_broken()
    # Adiciona links para os arquivos novos
    add_new()

# Início do programa
if __name__ == '__main__':
    # Inicia função principal, lendo os argumentos (se houver)
    main()
