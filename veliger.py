#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
VELIGER_v0.4
Atualizado: 02 Feb 2010 09:36PM

Editor de Metadados do Banco de imagens do CEBIMar-USP
Centro de Biologia Marinha da Universidade de São Paulo

Bruno C. Vellutini | organelas.com
'''

import os
import sys
import string
import subprocess
import time
import fileinput
import getopt

from PIL import Image as pil_image
from shutil import copy
from bsddb3 import db

from iptcinfo import IPTCInfo
from eagle import *

# ImageMagick e exiftool devem estar instalados no sistema
# Além de poder executar bash script
# TODO Diminuir e integrar dependências, possível?

#=== GUI_BACKEND ===#

def idle_status_rm(self):
    app.remove_status_message(status)

def data_changed(app, widget, value):
    '''
    Monitora as mudanças nos valores da tabela principal.

    Não faz nada, por enquanto.
    '''
    pass

def selection_changed(app, widget, selected):
    '''
    Função que define o tamanho do thumbnail a ser colocado na aba de edição
    dos mestadados (baseado nas dimensões da janela), passa os metadados da
    tabela para esta aba e focaliza na mesma.
    '''
    # Evita que o programa tente redimensionar um thumbnail inexistente (quando
    # a entrada é None - ocorre durante a limpeza da tabela)
    if selected is not None:

        # Ativa aba de edição que está desativada por padrão
        app['tabs'].get_page(1).set_active()
        
        # Cria variável com a dimensão da janela
        wsize = app.get_window_size()
        
        # Define o tamanho do thumbnail
        if wsize[0] >= 1335:
            app['thumb'].image = 'imagens/thumbs/500/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1335 and wsize[0] >= 1235:
            app['thumb'].image = 'imagens/thumbs/450/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1235 and wsize[0] >= 1135:
            app['thumb'].image = 'imagens/thumbs/400/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1135 and wsize[0] >= 955:
            app['thumb'].image = 'imagens/thumbs/300/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 955:
            app['thumb'].image = 'imagens/thumbs/250/%s' % \
            app['table'].selected()[0][1][0]
        
        # Passa os valores dos widgets da tabela para os campos de edição
        # app['nome'] = app['table'].selected()[0][1][0]
        app['titulo'] = app['table'].selected()[0][1][3]
        app['legenda'] = app['table'].selected()[0][1][4]
        app['keywords'] = app['table'].selected()[0][1][5]
        app['autor'] = app['table'].selected()[0][1][2]
        app['sublocal'] = app['table'].selected()[0][1][6]
        app['cidade'] = app['table'].selected()[0][1][7]
        app['estado'] = app['table'].selected()[0][1][8]
        app['pais'] = app['table'].selected()[0][1][9]
        app['taxon'] = app['table'].selected()[0][1][10]
        app['spp'] = app['table'].selected()[0][1][11]
        app['tamanho'] = app['table'].selected()[0][1][12]
        app['especialista'] = app['table'].selected()[0][1][13]
        app['direitos'] = app['table'].selected()[0][1][14]
        # app['path'] = app['table'].selected()[0][1][15]
    
        # Ativa o botão de salvar
        app['save_button'].active = True
        
        # Muda o foco para a aba de edição
        app['tabs'].focus_page(edit_data)
    
        # app['edit_button'].active = True


def save_meta(app, button):
    '''
    Salva os metadados na imagem usando o exiftool e repassa os valores de
    volta para a tabela, além de incluir a imagem na lista de fotos
    atualizadas.
    '''
    if app['nome'] != '':
        # Salvar metadados novos usando o ExifTools
        print '\nSalvando metadados...'
        try:
            # Salva os metadados na imagem (sobrepondo os correspondentes
            # originais)
            subprocess.call([
                'exiftool',
                '-overwrite_original',
                '-City=%s' % app['cidade'],
                '-By-line=%s' % app['autor'],
                '-Province-State=%s' % app['estado'],
                '-Country-PrimaryLocationName=%s' % app['pais'],
                '-CopyrightNotice=%s' % app['direitos'],
                '-UsageTerms="Creative Commons BY-NC-SA"',
                '-ObjectName=%s' % app['titulo'],
                '-Caption-Abstract=%s' % app['legenda'],
                '-Sub-location=%s' % app['sublocal'],
                '-Headline=%s' % app['taxon'],
                '-OriginalTransmissionReference=%s' % app['spp'],
                '-SpecialInstructions=%s' % app['tamanho'],
                '-Source=%s' % app['especialista'],
                app['table'].selected()[0][1][15]
                ])
            # Loop para incluir os keywords individualmente.
            # Lista com comando e argumentos
            shell_call = ['exiftool', '-overwrite_original']
            # Lista com keywords
            if app['keywords'] != '' or app['keywords'] is not None:
                print 'Atualizando marcadores...'
                keyword_list = app['keywords'].split(', ')
                for keyword in keyword_list:
                    shell_call.append('-Keywords=%s' % keyword.lower())
            else:
                print 'Marcadores em branco, deletando na imagem...'
                shell_call.append('-Keywords=')
            # Adicionando o endereço do arquivo ao comando
            shell_call.append(app['table'].selected()[0][1][15])
            # Executando o exiftool para adicionar as keywords
            subprocess.call(shell_call)
            print 'Keywords adicionadas.'
        except IOError:
            print '\nOcorreu algum erro. Verifique se o ExifTool está \
                    instalado.'
        else:
            print 'Novos metadados salvos na imagem com sucesso!'

        print '\nVerificando se a imagem está no banco de dados...'
        
        # Abrir e/ou criar arquivo do banco de dados
        imgdb = db.DB()
        imgdb.open(dbname)
        
        # Ativando o cursor
        cursor = imgdb.cursor()
        # Buscando o registro com o nome do arquivo
        rec = cursor.set(app['table'].selected()[0][1][0])
        # Fechando o cursor
        cursor.close()
        
        # Se o registro existir
        if rec:
            print 'Bingo! Registro de %s encontrado.\n' % \
            app['table'].selected()[0][1][0]
            # Transformando a entrada do banco em dicionário
            recdata = eval(rec[1])
            
            # Define a data de modificação do arquivo
            timestamp = time.strftime(
                    '%d/%m/%Y %I:%M:%S %p',
                    time.localtime(os.path.getmtime(app['table'].selected()[0][1][15]))
                    )
            
            # Criar entrada com valores atualizados
            newRec = {
                    'nome':recdata['nome'],
                    'timestamp':timestamp,
                    'postid':recdata['postid'],
                    'titulo':app['titulo'],
                    'keywords':app['keywords'].lower(),
                    'autor':app['autor'],
                    'cidade':app['cidade'],
                    'sublocal':app['sublocal'],
                    'estado':app['estado'],
                    'pais':app['pais'],
                    'taxon':app['taxon'],
                    'direitos':app['direitos'],
                    'legenda':app['legenda'],
                    'spp':app['spp'],
                    'tamanho':app['tamanho'],
                    'especialista':app['especialista'],
                    'www':recdata['www'],
                    'mod':True
                    }
            
            # Gravar entrada atualizada no banco de dados (transformada em
            # string)
            imgdb.put(recdata['nome'],str(newRec))

        # Fechando o banco
        imgdb.close()
        
        # Passa metadados novos pra tabela
        print 'Atualizando a tabela...'
        app['table'].selected()[0][1][3] = app['titulo']
        app['table'].selected()[0][1][4] = app['legenda']
        app['table'].selected()[0][1][5] = app['keywords'].lower()
        app['table'].selected()[0][1][2] = app['autor']
        app['table'].selected()[0][1][6] = app['sublocal']
        app['table'].selected()[0][1][7] = app['cidade']
        app['table'].selected()[0][1][8] = app['estado']
        app['table'].selected()[0][1][9] = app['pais']
        app['table'].selected()[0][1][10] = app['taxon']
        app['table'].selected()[0][1][11] = app['spp']
        app['table'].selected()[0][1][12] = app['tamanho']
        app['table'].selected()[0][1][13] = app['especialista']
        app['table'].selected()[0][1][14] = app['direitos']
    else:
        print 'Vazio!'
    
    # Atualiza lista de imagens modificadas
    updated = len(app['uptable'])

    if len(app['uptable']) == 0:
        app['uptable'].append([
            app['table'].selected()[0][1][0],
            app['table'].selected()[0][1][1],
            app['table'].selected()[0][1][3]
            ])
    else:
        # Verifica duplicatas
        for item in app['uptable']:
            if item[0] == app['table'].selected()[0][1][0]:
                item[2] = app['table'].selected()[0][1][3]
                break
        else:
            app['uptable'].append([
                app['table'].selected()[0][1][0],
                app['table'].selected()[0][1][1],
                app['table'].selected()[0][1][3]
                ])

    print 'Pronto.'

    app['tabs'].focus_page(full_list)

def back_cb(app, button):
    '''
    Botão na aba de edição para voltar à tabela
    '''
    app['tabs'].focus_page(full_list)

def clean_cb(app, button):
    '''
    Limpa entrada da tabela do CIFONAUTA, não remove entrada do banco de dados
    '''
    i = app['table'].selected()[0][0]
    del app['table'][i]

    # Limpa aba de edição
    for meta in widgets:
        if meta == 'thumb':
            data = chr(128) * (30 * 30 * 3)
            app[meta].image = Image(width=30, height=30, depth=24, data=data)
        else:
            app[meta] = ''
    
    # Desativa aba de edição
    app['tabs'].get_page(1).set_inactive()

    # Muda o foco para a aba inicial
    app['tabs'].focus_page(full_list)

def delete_cb(app, button):
    '''
    Remove entrada da tabela e do banco de dados
    '''
    # Confirmação da remoção
    do = yesno('Remover a entrada do banco de dados?', yesdefault=False)
    if do:
        # Abrir banco de dados
        imgdb = db.DB()
        imgdb.open(dbname)
        
        # Remove entrada do banco de dados
        imgdb.delete(app['table'].selected()[0][1][0])
        
        # Fechar banco de dados
        imgdb.close()
        
        i = app['table'].selected()[0][0]
        del app['table'][i]
        
        # Limpa aba de edição
        for meta in widgets:
            if meta == 'thumb':
                data = chr(128) * (30 * 30 * 3)
                app[meta].image = Image(
                        width=30,
                        height=30,
                        depth=24,
                        data=data
                        )
            else:
                app[meta] = ''
                
        # Desativa aba de edição
        app['tabs'].get_page(1).set_inactive()
        
        # Muda o foco para a aba inicial		
        app['tabs'].focus_page(full_list)
    else:
        pass

def format(app, table, row, col, value):
    '''
    Função que formata as células da tabela principal para destacar campos a
    serem preenchidos
    '''
    if value == '':
        if col == 2 or col == 3:
            return Table.CellFormat(bgcolor='red')
        else:
            return Table.CellFormat(bgcolor='yellow')

def thumb_gen(app, button):
    '''
    Botão com o thumbnail. Clique nele para redimensionar o thumb de acordo com
    as dimensões da janela.
    '''
    # Redimensiona o thumbnail
    if app['table'].selected() is None:
        pass
    else:
        wsize = app.get_window_size()
    
        if wsize[0] >= 1335:
            app['thumb'].image = 'imagens/thumbs/500/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1335 and wsize[0] >= 1235:
            app['thumb'].image = 'imagens/thumbs/450/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1235 and wsize[0] >= 1135:
            app['thumb'].image = 'imagens/thumbs/400/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 1135 and wsize[0] >= 955:
            app['thumb'].image = 'imagens/thumbs/300/%s' % \
            app['table'].selected()[0][1][0]
        elif wsize[0] < 955:
            app['thumb'].image = 'imagens/thumbs/250/%s' % \
            app['table'].selected()[0][1][0]

def edit_cb(app, button):
    '''
    Abre o editor de metadados da imagem selecionada.

    Atualmente desativado, a função selection já faz esse papel.
    '''
    #TODO Apagar definitivamente?
    app['tabs'].get_page(1).set_active()
    
    wsize = app.get_window_size()
    
    if wsize[0] >= 1335:
        app['thumb'].image = 'imagens/thumbs/500/%s' % \
        app['table'].selected()[0][1][0]
    elif wsize[0] < 1335 and wsize[0] >= 1235:
        app['thumb'].image = 'imagens/thumbs/450/%s' % \
        app['table'].selected()[0][1][0]
    elif wsize[0] < 1235 and wsize[0] >= 1135:
        app['thumb'].image = 'imagens/thumbs/400/%s' % \
        app['table'].selected()[0][1][0]
    elif wsize[0] < 1135 and wsize[0] >= 955:
        app['thumb'].image = 'imagens/thumbs/300/%s' % \
        app['table'].selected()[0][1][0]
    elif wsize[0] < 955:
        app['thumb'].image = 'imagens/thumbs/250/%s' % \
        app['table'].selected()[0][1][0]

    # app['nome'] = app['table'].selected()[0][1][0]
    app['titulo'] = app['table'].selected()[0][1][3]
    app['legenda'] = app['table'].selected()[0][1][4]
    app['keywords'] = app['table'].selected()[0][1][5]
    app['autor'] = app['table'].selected()[0][1][2]
    app['sublocal'] = app['table'].selected()[0][1][6]
    app['cidade'] = app['table'].selected()[0][1][7]
    app['estado'] = app['table'].selected()[0][1][8]
    app['pais'] = app['table'].selected()[0][1][9]
    app['taxon'] = app['table'].selected()[0][1][10]
    app['spp'] = app['table'].selected()[0][1][11]
    app['tamanho'] = app['table'].selected()[0][1][12]
    app['especialista'] = app['table'].selected()[0][1][13]
    app['direitos'] = app['table'].selected()[0][1][14]
    # app['path'] = app['table'].selected()[0][1][15]

    app['save_button'].active = True
    
    app['tabs'].focus_page(edit_data)

def pref_cb(app, menuitem):
    '''Abre a janela com as preferências.'''
    app.show_preferences_dialog()

def selectdir_cb(app, widget, name):
    '''Callback do botão para selecionar o diretório na janela de
    preferências.'''
    #TODO funcionalidade incompleta
    app['srcdir'] = name

def selectdb_cb(app, widget, name):
    '''Callback do botão para selecionar o arquivo de banco de dados.'''
    #TODO funcionalidade incompleta
    app['dbfile'] = name

def quit_cb(app, menuitem):
    '''Sai do programa.'''
    close(app_id='main')

def openfile_cb(app, menuitem):
    '''
    Callback para a janela de seleção de arquivos do menu.

    Pega o caminho do(s) arquivo(s), lê os metadados e joga na tabela.
    '''
    # Inicia contadores (m=nova imagem, n=duplicada)
    m = 0
    n = 0
    
    # Seleção de arquivos
    fpaths = app.file_chooser(0, filter='*.jpg', multiple=True)

    # Se arquivo(s) for(em) selecionado(s) executar
    if fpaths:
        static_list = []
        for table_entry in app['table']:
            static_list.append(table_entry)
        for fpath in fpaths:
            # Checando por duplicatas
            for static_entry in static_list:
                if duplicate_check(
                        static_entry,
                        os.path.split(fpath)[1]
                        ) == True:
                    n += 1
                    break
            else:
                # Define a data de modificação do arquivo
                timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p',
                            time.localtime(os.path.getmtime(fpath)))
                
                # Verifica se imagem está no banco de dados
                entry = searchImgdb(fpath, timestamp)
                
                app['table'].append(entry)

                m += 1

        # FIXME Exibir mensagem na barra de status direito...
        global status
        status = app.status_message(
                ' %d imagens duplicadas, %d novas imagens' % (n, m))

def openfolder_cb(app, menuitem):
    '''
    Callback para a janela de seleção de pastas do menu.

    Pega a pasta e procura dentro dela todos os arquivos terminados em .jpg.
    Para cada arquivo lê os metadados e joga na tabela.
    '''
    # Inicia contadores (m=nova imagem, n=duplicada)
    m = 0
    n = 0
    
    folder = app.file_chooser(2)
    
    # Se alguma pasta for selecionada
    if folder:
        # Cria list estática com entradas da tabela para verificar duplicatas
        static_list = []
        for table_entry in app['table']:
            static_list.append(table_entry)

        # Extrai lista de imagens usando a função imgGrab e seus metadados
        # usando a função createMeta (dentro da primeira)
        entries = imgGrab(folder)

        print 'Populando a tabela... isto pode levar alguns segundos.'
        for entry in entries:
            # Verificando entradas duplicadas
            for static_entry in static_list:
                if duplicate_check(static_entry, entry[0]) == True:
                    n += 1
                    break
            else:
                app['table'].append(entry)
                m += 1
                
        # FIXME Exibir mensagem na barra de status direito...
        global status
        status = app.status_message(' %d imagens duplicadas, %d novas imagens'
                % (n, m))

def opendatabase_cb(app, menuitem):
    '''
    Callback para a janela de seleção de arquivos do menu.

    Pega o caminho do arquivo de banco de dados e chama a função que lê as
    entradas e joga na tabela (db_import).
    '''
    database_name = app.file_chooser(0, filter='database*', multiple=False)
    
    # Se algum arquivo for selecionado executar a função
    if database_name:
        db_import(database_name)

def cleartable_cb(app, menuitem):
    '''
    Limpa tabela com lista de imagens e desativa aba de edição de metadados.
    '''
    # Limpa tabela
    t = app['table']
    t.clear()
    
    # Limpa aba de edição
    for meta in widgets:
        if meta == 'thumb':
            data = chr(128) * (30 * 30 * 3)
            app[meta].image = Image(width=30, height=30, depth=24, data=data)
        else:
            app[meta] = ''
    
    # Desativa aba de edição
    app['tabs'].get_page(1).set_inactive()

    # Muda o foco para a aba inicial
    app['tabs'].focus_page(full_list)

def digittime_cb(app, widget, text):
    '''
    Tentativa de inserir um timer para o buscador... não implementado ainda.
    '''
    # TODO
    if len(text) < 4:
        pass
    else:
        global t0
        global t
        
        t1 = time.time()
        
        t = t1 - t0
        
        while t < 1 or t > 20:
            print t
            break
        else:
            print app, widget, text
            filter_gui(text)
        
        t0 = time.time()

def filter_gui(text):
    '''
    Filtro do buscador. Não implementado ainda.
    '''
    # TODO Buscador
    del app['table'][:]
    for entry in full_table:
        if(
                    text.lower() in str(entry[2]).lower() or
                    text.lower() in str(entry[3]).lower() or
                    text.lower() in str(entry[4]).lower() or
                    text.lower() in str(entry[5]).lower() or
                    text.lower() in str(entry[6]).lower() or
                    text.lower() in str(entry[7]).lower() or
                    text.lower() in str(entry[9]).lower() or
                    text.lower() in str(entry[10]).lower() or
                    text.lower() in str(entry[11]).lower() or
                    text.lower() in str(entry[13]).lower()
                    ):
                app['table'].append(entry)

#=== BACKEND ===#

def db_import(dbname):
    '''
    Importa um banco de dados já existente (normalmente criado na sessão
    anterior).
    '''

    # Contador
    n = 0
    m = 0

    # Abrir e/ou criar arquivo do banco de dados
    imgdb = db.DB()
    imgdb.open(dbname, db.DB_BTREE, db.DB_READ_UNCOMMITTED)
    
    # Cria lista que gerará a tabela da interface gráfica
    entry_meta = []
    
    # Ativando o cursor
    cursor = imgdb.cursor()
    
    # Pega a primeira entrada do BD
    rec = cursor.first()

    print 'Importando banco de dados... Isto pode levar alguns segundos.'
    
    while rec:
        # Transforma string do BD em um dicionário
        # FIXME Avaliar questão da segurança ao usar o 'eval'
        recdata = eval(rec[1])
        
        # Converte valores dos metadados vazios (None) para string em branco
        for k, v in recdata.iteritems():
            if v is None:
                v = u''
                recdata[k] = v
            else:
                pass
    
        # Cria a linha da tabela da interface
        entry_meta = [
                recdata['nome'],
                Image(filename='imagens/thumbs/100/%s' % recdata['nome']),
                recdata['autor'],
                recdata['titulo'],
                recdata['legenda'],
                recdata['keywords'],
                recdata['sublocal'],
                recdata['cidade'],
                recdata['estado'],
                recdata['pais'],
                recdata['taxon'],
                recdata['spp'],
                recdata['tamanho'],
                recdata['especialista'],
                recdata['direitos'],
                os.path.join(srcdir, recdata['nome']),
                ]

        # Se programa estiver iniciando
        if app is None:
            full_table.append(entry_meta)
        # Se não, fazer checagem de duplicatas
        else:
            static_list = []
            for table_entry in app['table']:
                static_list.append(table_entry)
            for static_entry in static_list:
                if duplicate_check(static_entry, entry_meta[0]) == True:
                    n += 1
                    break
            else:
                app['table'].append(entry_meta)
                m += 1

        #Pega próxima entrada do BD
        rec = cursor.next()
            
    # Fechando o cursor do banco de dados
    cursor.close()
    
    # Fechando o banco
    imgdb.close()

    print 'Banco de dados importado.'
    # Mostra mensagem na barra de status do programa
    # FIXME implementar direito...
    if app is not None:
        global status
        status = app.status_message(
                ' %d imagens importadas, %d imagens duplicadas' % (m, n))
        app.idle_add(idle_status_rm)

def duplicate_check(entry, filename):
    '''
    Função que compara o nome do arquivo importado com o nome do arquivo
    presente no banco de dados.
    '''
    entry_name = entry[0]
    if entry_name == filename:
        return True
    else:
        return False

def create_thumbs(fpath):
    '''
    Cria thumbnails de vários tamanhos para as fotos novas.
    '''
    
    print 'Iniciando o criador de thumbnails.'

    # Lista com tamanhos dos tumbnails
    sizes = [100, 250, 300, 400, 450, 500]
    
    # Checagem padrão
    print '\nChecando se pastas existem...'
    hasdir = os.path.isdir(thumbdir)
    if hasdir == True:
        for size in sizes:
            each_thumbdir = os.path.join(thumbdir,str(size))
            haseach_thumbdir = os.path.isdir(each_thumbdir)
            if haseach_thumbdir == True:
                continue
            else:
                os.mkdir(each_thumbdir)
    else:
        os.mkdir(thumbdir)
        for size in sizes:
            each_thumbdir = os.path.join(thumbdir,str(size))
            os.mkdir(each_thumbdir)

    print 'Pronto!'
    
    # Nome do arquivo
    file = os.path.split(fpath)[1]
    
    # Para cada tamanho de thumb
    for size in sizes:
        pasta = os.path.join(thumbdir,str(size))
        lista = os.listdir(pasta)
        newthumb_path = os.path.join(pasta, file)
        # Se o arquivo já existir, pular
        if file in lista:
            print 'Thumbs já existem.'
            continue
        # Se não, criar thumb
        else:
            # Copiar original para pasta
            copy(fpath, pasta)
            print '%s copiado para pasta %s' % (file, size)
            try:
                # Criar thumb
                im = pil_image.open(newthumb_path)
                dim = size, size
                im.thumbnail(dim)
                im.save(os.path.join(pasta, file), 'JPEG')
                print 'Thumbnail criado!'
            except:
                print 'Não consegui criar o thumbnail...'

def searchImgdb(fpath, timestamp):
    '''
    Busca o registro da imagem no banco de dados procurando pelo nome do
    arquivo.
    
    Se encontrar, compara a data de modificação do arquivo e do registro.

    Se as datas forem iguais pula para a próxima imagem, se forem diferentes
    atualiza o registro.
    '''

    print 'Verificando se a imagem está no banco de dados...'
    
    # Obtém nome do arquivo
    fname = os.path.basename(fpath)

    # Abrir e/ou criar arquivo do banco de dados
    imgdb = db.DB()
    imgdb.open(dbname, db.DB_BTREE, db.DB_READ_UNCOMMITTED)
    
    # Ativando o cursor
    cursor = imgdb.cursor()
    # Buscando o registro com o nome do arquivo
    rec = cursor.set(fname)
    # Fechando o cursor
    cursor.close()
    # Fechando o banco
    imgdb.close()

    # Se o registro existir
    if rec:
        print 'Bingo! Registro de %s encontrado.\n' % fname
        # Transformando a entrada do banco em dicionário
        recdata = eval(rec[1])

        print 'Comparando a data de modificação do arquivo com o registro...'
        if recdata['timestamp'] == timestamp:
            # Se os timetamps forem iguais
            print
            print '\tBanco de dados\t\t  Arquivo'
            print '\t' + 2 * len(timestamp) * '-' + 4 * '-'
            print '\t%s\t= %s' % (recdata['timestamp'], timestamp)
            print
            if recdata['www'] == True and recdata['mod'] == False:
                # Arquivo não foi modificado, nem precisa ser atualizado
                print 'Arquivo não mudou!'
            elif recdata['www'] == True and recdata['mod'] == True:
                # Timestamp não foi modificado, mas imagem não foi carregada
                # no site ainda
                print 'Arquivo que está no site não está atualizado!'
            elif recdata['www'] == False:
                print 'Arquivo não está no site!'
                # Imagem nunca foi carregado no site
            
            entry_meta = []
            # Cria a lista para tabela da interface
            entry_meta = [
                        recdata['nome'],
                        Image(filename='imagens/thumbs/100/%s' %
                            recdata['nome']),
                        recdata['autor'],
                        recdata['titulo'],
                        recdata['legenda'],
                        recdata['keywords'],
                        recdata['sublocal'],
                        recdata['cidade'],
                        recdata['estado'],
                        recdata['pais'],
                        recdata['taxon'],
                        recdata['spp'],
                        recdata['tamanho'],
                        recdata['especialista'],
                        recdata['direitos'],
                        fpath
                        ]
            
            return entry_meta
        else:
            print
            print '\tBanco de dados\t\t   Arquivo'
            print '\t' + 2 * len(timestamp) * '-' + 4 * '-'
            print '\t%s\t!= %s' % (recdata['timestamp'], timestamp)
            print
            if recdata['www'] == True:
                # Timestamp modificado, imagem do site não está atualizada
                print 'Arquivo que está no site não está atualizado!'
            elif recdata['www'] == False:
                # Imagem nunca foi carregada no site
                print 'Arquivo não está no site!'
                
            # Lê metadados e cria entrada da tabela
            entry = createMeta(fpath)
            return entry
    else:
        print 'Registro não encontrado!'
        print 'Continuando...'
        
        create_thumbs(fpath)
    
        # Lê metadados e cria entrada da tabela
        entry = createMeta(fpath)

        # Criar entrada com valores atualizados
        newRec = {
                    'nome':fname,
                    'timestamp':timestamp,
                    'postid':0,
                    'titulo':entry[3],
                    'keywords':entry[5],
                    'autor':entry[2],
                    'cidade':entry[7],
                    'sublocal':entry[6],
                    'estado':entry[8],
                    'pais':entry[9],
                    'taxon':entry[10],
                    'direitos':entry[14],
                    'legenda':entry[4],
                    'spp':entry[11],
                    'tamanho':entry[12],
                    'especialista':entry[13],
                    'www':False,
                    'mod':False
                    }
        
        # Atualizar a data de modificação no registro do banco de dados
        print '\nAtualizando o banco de dados...'
        
        # Abrir banco de dados
        imgdb = db.DB()
        imgdb.open(dbname)
        
        # Gravar entrada atualizada no banco de dados (transformada em string)
        imgdb.put(fname,str(newRec))
        
        # Fechar banco de dados
        imgdb.close()
        
        print 'Registro no banco de dados atualizado!'
        
        return entry

def createMeta(pathtofile):
    '''
    Define as variáveis extraídas dos metadados (IPTC) da imagem.

    Usa a biblioteca do arquivo iptcinfo.py.
    '''

    fname = os.path.basename(pathtofile)

    print 'Lendo os metadados de %s e criando variáveis.' % fname
    
    # Criar objeto com metadados
    info = IPTCInfo(pathtofile)
    
    # Checando se o arquivo tem dados IPTC
    if len(info.data) < 4:
        print 'Imagem não tem dados IPTC!'

    # Dicionário com metadados da imagem
    meta = {}
    
    # Definindo as variáveis
    title = info.data['object name']			# 5
    keywords = info.data['keywords']			# 25
    author = info.data['by-line']				# 80
    city = info.data['city']				# 90
    sublocation = info.data['sub-location']			# 92
    state = info.data['province/state']			# 95
    country = info.data['country/primary location name']	# 101
    category = info.data['headline']			# 105
    copyright = info.data['copyright notice']		# 116
    caption = info.data['caption/abstract']			# 120
    spp = info.data['original transmission reference']	# 103
    scale = info.data['special instructions']		# 40
    source = info.data['source']				# 115

    meta = {
            'nome' : fname,
            'titulo' : title,
            'keywords' : ', '.join(keywords),
            'autor' : author,
            'legenda' : caption,
            'sublocal' : sublocation,
            'cidade' : city,
            'estado' : state,
            'pais' : country,
            'taxon' : category,
            'spp' : spp,
            'tamanho' : scale,
            'especialista' : source,
            'direitos' : copyright,
            'path' : pathtofile
            }

    # Converte valores dos metadados vazios (None) para string em branco
    for k, v in meta.iteritems():
        if v is None:
            v = u''
            meta[k] = v
        else:
            pass
    
    entry_meta = []

    # Cria a lista para tabela da interface
    entry_meta = [
            meta['nome'],
            Image(filename='imagens/thumbs/100/%s' % meta['nome']),
            meta['autor'],
            meta['titulo'],
            meta['legenda'],
            meta['keywords'],
            meta['sublocal'],
            meta['cidade'],
            meta['estado'],
            meta['pais'],
            meta['taxon'],
            meta['spp'],
            meta['tamanho'],
            meta['especialista'],
            meta['direitos'],
            meta['path']
            ]

    return entry_meta
            
def imgGrab(folder):
    '''
    Busca recursivamente arquivos com extensão jpg|JPG na pasta determinada.
    '''
    # Zera contador
    n = 0

    # Cria listas
    folder_imgs = []
    ext_list = ['jpg', 'JPG']
    
    # Buscador de imagens em ação
    print '\nIniciando o cifonauta!!!'
    for root, dirs, files in os.walk(folder):
        for fname in files:
            extension = fname.split('.')[-1]
            if extension in ext_list:
                # Define o endereço do arquivo
                fpath = os.path.join(root,fname)
                
                # Define a data de modificação do arquivo
                timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p',
                        time.localtime(os.path.getmtime(fpath)))
                
                # Verifica se imagem está no banco de dados
                entry = searchImgdb(fpath, timestamp)
                
                # Adiciona à lista
                folder_imgs.append(entry)
                
                # Contador
                n += 1
        
        else:	# Se o número máximo de imagens for atingido, finalizar
            global status
            status = app.status_message(' %d fotos analisadas' % n)
            app.idle_add(idle_status_rm)
            break
        
    # Retorna a lista de imagens com seus metadados
    return folder_imgs


#=== MAIN ===#

# Diretório com as imagens
srcdir = 'imagens/source'
# Diretório com thumbnails
thumbdir = 'imagens/thumbs'

# Nome do arquivo com banco de dados
dbname = 'database'

# Lista com nomes dos widgets
widgets = [
        'thumb',
        'autor',
        'titulo',
        'legenda',
        'keywords',
        'sublocal',
        'cidade',
        'estado',
        'pais',
        'taxon',
        'spp',
        'tamanho',
        'especialista',
        'direitos'
        ]

# Inicia contador (FIXME Era pra ser integrado no buscador, mas ainda não
# implementado)
t0 = time.time()

# Criar a instância do bd
imgdb = db.DB()

# Abrir e/ou criar arquivo do banco de dados
imgdb.open(dbname, db.DB_BTREE, db.DB_CREATE)
imgdb.close()

# Cria lista para tabela completa
full_table = []

# Define app para evitar conflito (func: db_import) na importação inicial do bd
app = None

# Importa banco de dados existente
db_import(dbname)

# Lista para tabela com imagens atualizadas
updated_meta = ''

# Imagem padrão
data = chr(128) * (30 * 30 * 3)

#=== GUI_FRONTEND ===#

print 'Iniciando a interface do usuário...'

full_list = Tabs.Page(
        label=u'Imagens selecionadas',
        children=(
            # Entry(id='search_box', label='Busca:', callback=digittime_cb),
            Table(id='table', label='Tabela de Metadados', items=full_table,
                headers=['Arquivo', 'Thumb', 'Autor', 'Título', 'Legenda',
                    'Keywords', 'Sublocal', 'Cidade', 'Estado', 'País',
                    'Táxon', 'Espécie', 'Tamanho', 'Especialista', 'Direitos',
                    'Path'],
                types=[str,Image,str,str,str,str,str,str,str,str,str,str,str,str,str,str],
                selection_callback=selection_changed,
                cell_format_func=format,
                hidden_columns_indexes=[0,15],
                ),
            # Button(id='edit_button', label='Editar', active=False,
            # callback=edit_cb),
            ),
        )

edit_data = Tabs.Page(
        label=u'Metadados',
        active=False,
        children=(
            Group(id='soft_data',
                border=False,
                children=(
                    Group(id='soft_meta',
                        horizontal=True,
                        border=False,
                        children=(
                            Group(id='thumb_edit',
                                border=False,
                                children=(
                                    Button(id='thumb', image=Image(width=30,
                                        height=30, depth=24, data=data),
                                        callback=thumb_gen)
                                    )
                                ),
                            Group(id='main_meta',
                                border=False,
                                children=(
                                    # Entry(id='nome', label='Arquivo:',
                                    # editable=False),
                                    # Entry(id='path', label='Local:',
                                    # editable=False),
                                    Entry(id='titulo', label='Título:'),
                                    Entry(id='legenda', label='Legenda:',
                                        multiline=True),
                                    Entry(id='keywords', label='Marcadores:'),
                                    Entry(id='autor', label='Autor:'),
                                    Entry(id='sublocal', label='Local:'),
                                    Entry(id='cidade', label='Cidade:'),
                                    Entry(id='estado', label='Estado:'),
                                    Entry(id='pais', label='País:'),
                                    Entry(id='taxon', label='Táxon:'),
                                    Entry(id='spp', label='Espécie:'),
                                    Selection(id='tamanho',
                                        label='Tamanho',
                                        options=[
                                            '<0,1 mm',
                                            '0,1 - 1,0 mm',
                                            '1,0 - 10 mm',
                                            '10 - 100 mm',
                                            '>100 mm'
                                            ]
                                        ),
                                    Entry(id='especialista',
                                        label='Especialista:'),
                                    Entry(id='direitos', label='Direitos:'),
                                    )
                                )
                            ),
                        ),
                    ),
                ),
            Group(id='menu',
                horizontal=True,
                border=False,
                children=(
                    Button(id='back_button', label='Voltar', active=True,
                        callback=back_cb,
                        expand_policy=ExpandPolicy.Horizontal()),
                    Button(id='clean_button', label='Limpar', active=True,
                        callback=clean_cb,
                        expand_policy=ExpandPolicy.Horizontal()),
                    Button(id='delete_button', label='Deletar', active=True,
                        callback=delete_cb,
                        expand_policy=ExpandPolicy.Horizontal()),
                    Button(id='save_button', label='Salvar', active=False,
                        callback=save_meta,
                        expand_policy=ExpandPolicy.Horizontal())
                    )
                ),
            ),
        )

update_list = Tabs.Page(
        label=u'Modificadas',
        children=(
            Table(id='uptable', label='Imagens atualizadas nesta sessão',
                items=updated_meta,
                headers=['Arquivo','Thumb', 'Título'],
                types=[str,Image,str],
                hidden_columns_indexes=[0],
                ),
            ),
        )

app = App(
        id='main',
        title='CIFONAUTA - Gerenciador de metadados',
        window_size=(1000, 950),
        statusbar=True,
        preferences=(# Não implementado ainda
            Group(id='dirdb',
                label='Diretório e banco de dados',
                children=(
                    Group(id='dir',
                        border=False,
                        horizontal=True,
                        children=(
                            Entry(id='srcdir', label='Diretório fonte:'),
                            SelectFolderButton(callback=selectdir_cb),
                            )
                        ),
                    Group(id='db',
                        border=False,
                        horizontal=True,
                        children=(
                            Entry(id='dbfile',
                                label='Arquivo de banco de dados:'),
                            OpenFileButton(callback=selectdb_cb),
                            )
                        )
                    ),
                ),
            Group(id='wpopt',
                label='WordPress',
                children=(
                    Entry(id='wp', label='Servidor XML-RPC:'),
                    Entry(id='login', label='Usuário:'),
                    Password(id='senha', label='Senha:')
                    ),
                ),
            ),
        menu=(
            Menu.Submenu(label='Arquivo',
                subitems=(
                    Menu.Item(label="Abrir arquivo", callback=openfile_cb),
                    Menu.Item(label="Abrir pasta", callback=openfolder_cb),
                    Menu.Item(label="Importar banco de dados",
                        callback=opendatabase_cb),
                    Menu.Separator(),
                    Menu.Item(label="Opções", active=False, callback=pref_cb),
                    Menu.Separator(),
                    Menu.Item(label="Sair", callback=quit_cb),
                    ),
                ),
            Menu.Submenu(label='Editar',
                subitems=(
                    Menu.Item(label="Limpar tabela", callback=cleartable_cb),
                    ),
                ),
            ),
        center=(
                Tabs(
                    id='tabs',
                    children=(full_list, edit_data, update_list)
                    ),
                ),
        data_changed_callback=data_changed,
        )
run()
