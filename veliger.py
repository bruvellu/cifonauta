#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# VÉLIGER
# Copyleft 2010 - Bruno C. Vellutini | organelas.com
# 
# TODO Inserir licença.
#
# Atualizado: 15 Mar 2010 08:43AM
'''Editor de Metadados do Banco de imagens do CEBIMar-USP.

Escrever uma explicação.
Centro de Biologia Marinha da Universidade de São Paulo.
'''

import os
import sys
import operator
import subprocess
import time
import pickle

from PIL import Image
from shutil import copy
from iptcinfo import IPTCInfo

from PyQt4.QtCore import *
from PyQt4.QtGui import *

__author__ = 'Bruno Vellutini'
__copyright__ = 'Copyright 2010, CEBIMar-USP'
__credits__ = 'Bruno C. Vellutini'
__license__ = 'DEFINIR'
__version__ = '0.5'
__maintainer__ = 'Bruno Vellutini'
__email__ = 'organelas at gmail dot com'
__status__ = 'Development'


class MainWindow(QMainWindow):
    '''Janela principal do programa.

    Inicia as instâncias dos outros componentes e aguarda interação do usuário.
    '''
    def __init__(self):
        QMainWindow.__init__(self)
        # Definições
        global mainWidget
        mainWidget = MainTable(datalist, header)
        self.model = mainWidget.model
        # Dock com thumbnail
        self.dockThumb = DockThumb()
        self.thumbDockWidget = QDockWidget(u'Thumbnail', self)
        self.thumbDockWidget.setWidget(self.dockThumb)
        # Dock com lista de updates
        self.dockUnsaved = DockUnsaved()
        self.unsavedDockWidget = QDockWidget(u'Entradas modificadas', self)
        self.unsavedDockWidget.setWidget(self.dockUnsaved)
        # Dock com editor de metadados
        self.dockEditor = DockEditor()
        self.editorDockWidget = QDockWidget(u'Editor', self)
        self.editorDockWidget.setAllowedAreas(
                Qt.TopDockWidgetArea |
                Qt.BottomDockWidgetArea
                )
        self.editorDockWidget.setWidget(self.dockEditor)

        # Atribuições da MainWindow
        self.setCentralWidget(mainWidget)
        self.setWindowTitle(u'VÉLIGER - Editor de Metadados')
        self.setWindowIcon(QIcon(u'./icons/python.svg'))
        self.statusBar().showMessage(u'Pronto para editar!', 2000)
        self.menubar = self.menuBar()

        # Ações do menu
        self.exit = QAction(QIcon(u'./icons/system-shutdown.png'),
                u'Sair', self)
        self.exit.setShortcut('Ctrl+Q')
        self.exit.setStatusTip(u'Fechar o programa')
        self.connect(self.exit, SIGNAL('triggered()'), SLOT('close()'))

        self.openFile = QAction(QIcon(u'./icons/document-open.png'),
                u'Abrir arquivo(s)', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip(u'Abrir imagens')
        self.connect(self.openFile, SIGNAL('triggered()'), self.openfile_dialog)

        self.openDir = QAction(QIcon(u'./icons/folder-new.png'),
                u'Abrir pasta(s)', self)
        self.openDir.setShortcut('Ctrl+D')
        self.openDir.setStatusTip(u'Abrir pasta')
        self.connect(self.openDir, SIGNAL('triggered()'), self.opendir_dialog)

        self.delRow = QAction(QIcon(u'./icons/edit-delete.png'),
                u'Deletar entrada(s)', self)
        self.delRow.setShortcut('Ctrl+W')
        self.delRow.setStatusTip(u'Deletar entrada')
        self.connect(self.delRow, SIGNAL('triggered()'), self.delcurrent)

        self.saveFile = QAction(QIcon(u'./icons/document-save.png'),
                u'Salvar metadados', self)
        self.saveFile.setShortcut('Ctrl+S')
        self.saveFile.setStatusTip(u'Salvar metadados')
        self.connect(self.saveFile, SIGNAL('triggered()'),
                self.dockEditor.savedata)
        salvo = lambda: self.changeStatus(u'Alterações salvas!')
        self.saveFile.triggered.connect(salvo)

        self.delAll = QAction(QIcon(u'./icons/edit-delete.png'),
                u'Limpar tabela', self)
        self.delAll.setStatusTip(u'Deletar todas as entradas')
        self.connect(self.delAll, SIGNAL('triggered()'), self.cleartable)

        # Toggle dock widgets
        self.toggleThumb = self.thumbDockWidget.toggleViewAction()
        self.toggleThumb.setShortcut('Shift+T')
        self.toggleThumb.setStatusTip(u'Esconde ou mostra o dock com thumbnails')

        self.toggleEditor = self.editorDockWidget.toggleViewAction()
        self.toggleEditor.setShortcut('Shift+E')
        self.toggleEditor.setStatusTip(u'Esconde ou mostra o dock com o editor')

        self.toggleUnsaved = self.unsavedDockWidget.toggleViewAction()
        self.toggleUnsaved.setShortcut('Shift+U')
        self.toggleUnsaved.setStatusTip(u'Esconde ou mostra o dock com modificadas')

        # Menu
        self.arquivo = self.menubar.addMenu('&Arquivo')
        self.arquivo.addAction(self.openFile)
        self.arquivo.addAction(self.openDir)
        self.arquivo.addAction(self.saveFile)
        self.arquivo.addAction(self.delRow)
        self.arquivo.addSeparator()
        self.arquivo.addAction(self.exit)

        self.editar = self.menubar.addMenu('&Editar')
        self.editar.addAction(self.delAll)
        self.editar.addSeparator()
        self.editar.addAction(self.toggleThumb)
        self.editar.addAction(self.toggleEditor)
        self.editar.addAction(self.toggleUnsaved)

        # Toolbar
        self.toolbar = self.addToolBar('Ações')
        self.toolbar.addAction(self.openFile)
        self.toolbar.addAction(self.openDir)
        self.toolbar.addAction(self.saveFile)
        self.toolbar.addAction(self.delRow)
        self.toolbar = self.addToolBar('Sair')
        self.toolbar.addAction(self.exit)

        # Docks
        self.addDockWidget(Qt.RightDockWidgetArea, self.thumbDockWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.unsavedDockWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.editorDockWidget)
        self.tabifyDockWidget(self.thumbDockWidget, self.unsavedDockWidget)
        self.setTabPosition(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea,
                QTabWidget.North)
        #self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.connect(
                self.dockUnsaved,
                SIGNAL('commitMeta(entries)'),
                self.commitmeta
                )

        self.connect(
                self.dockUnsaved,
                SIGNAL('syncSelection(filename)'),
                self.setselection
                )

        self.resize(1000, 780)

    def setselection(self, filename):
        '''Sincroniza seleção entre lista e tabela principal.

        Pega a seleção da lista de imagens modificadas e procura a linha
        correspondente na tabela principal. Se o item não for encontrado o item
        na lista é apagado.
        '''
        index = self.model.index(0, 0, QModelIndex())
        matches = self.model.match(index, 0, filename, -1,
                Qt.MatchContains)
        if len(matches) == 1:
            match = matches[0]
            mainWidget.selectRow(match.row())
        elif len(matches) == 0:
            mainWidget.selectionModel.clearSelection()
            mainWidget.emitlost(filename)
            self.changeStatus(u'%s não foi encontrada, importe-a novamente' %
                    filename, 10000)

    def commitmeta(self, entries):
        '''Grava os metadados modificados na imagem.
        
        Pega lista de imagens modificadas, procura entrada na tabela principal
        e retorna os metadados. Chama função que gravará estes metadados na
        imagem. Chama função que emitirá o sinal avisando a gravação foi
        completada com sucesso.        
        '''
        for entry in entries:
            index = self.model.index(0, 0, QModelIndex())
            matches = self.model.match(index, 0, entry, -1,
                    Qt.MatchContains)
            if len(matches) == 1:
                values = []
                match = matches[0]
                for col in xrange(mainWidget.ncols):
                    index = self.model.index(match.row(), col, QModelIndex())
                    value = self.model.data(index, Qt.DisplayRole)
                    values.append(unicode(value.toString()))
                filename = os.path.basename(values[0])
                self.changeStatus(u'Gravando metadados em %s...' % filename)
                write = self.writemeta(values)
                if write == 0:
                    self.changeStatus(u'%s atualizado!' % filename)
                    continue
                else:
                    break
        if write == 0:
            mainWidget.emitsaved()
        else:
            self.changeStatus(u'%s deu erro!' % filename, 5000)
            critical = QMessageBox()
            critical.setWindowTitle(u'Erro de gravação!')
            critical.setText(u'Metadados não foram gravados.')
            critical.setInformativeText(
                    u'%s pode ter mudado de local, nome ou ' % filename +
                    'estar protegido contra gravação. Tente importá-lo ' +
                    'novamente. O arquivo será retirado da lista de ' +
                    'imagens modificadas. Deseja deletar a entrada da ' +
                    'tabela principal também?')
            critical.setIcon(QMessageBox.Critical)
            critical.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            critical.exec_()
            self.setselection(filename)
            mainWidget.emitlost(filename)
            if critical == QMessageBox.Yes:
                self.delcurrent()
            #TODO deletar entrada da tabela principal tb?

    def writemeta(self, values):
        '''Grava os metadados no arquivo.'''
        print 'Começando a gravar metadados pelo IPTCinfo...'
        # Criar objeto com metadados
        info = IPTCInfo(values[0])
        try:
            info.data['object name'] = values[1]                    # title
            info.data['caption/abstract'] = values[2]               # caption
            info.data['headline'] = values[4]                       # category
            info.data['original transmission reference'] = values[5]# spp
            info.data['source'] = values[6]                         # source
            info.data['by-line'] = values[7]                        # author
            info.data['copyright notice'] = values[8]               # copyright
            info.data['special instructions'] = values[9]           # scale
            info.data['sub-location'] = values[10]                  # sublocation
            info.data['city'] = values[11]                          # city
            info.data['province/state'] = values[12]                # state
            info.data['country/primary location name'] = values[13] # country

            # Lista com keywords
            if values[3] == '' or values[3] is None:
                info.keywords = []                                  # keywords
            else:
                keywords = values[3].split(', ')
                keywords = [keyword.lower() for keyword in keywords]
                info.data['keywords'] = keywords                    # keywords
            info.save()
        except IOError:
            print '\nOcorreu algum erro. '
            self.changeStatus(u'ERRO!', 10000)
            critical = QMessageBox()
            critical.setWindowTitle(u'Erro!')
            critical.setText(u'Verifique se o IPTCinfo está bem.')
            critical.setIcon(QMessageBox.Critical)
            critical.exec_()
        else:
            print 'Gravado, sem erros.'
            return 0

    def exiftool(self, values):
        '''Grava os metadados no arquivo.

        Usa subprocesso para chamar o exiftool, que gravará os metadados
        modificados na imagem.
        '''
        #TODO Como funcionará no Windows? Será que o PIL pode substituir?
        try:
            shellcall = [
                    'exiftool',
                    '-overwrite_original',
                    '-ObjectName=%s' % values[1],
                    '-Caption-Abstract=%s' % values[2],
                    '-Headline=%s' % values[4],
                    '-OriginalTransmissionReference=%s' % values[5],
                    '-Source=%s' % values[6],
                    '-By-line=%s' % values[7],
                    '-CopyrightNotice=%s' % values[8],
                    '-SpecialInstructions=%s' % values[9],
                    '-Sub-location=%s' % values[10],
                    '-City=%s' % values[11],
                    '-Province-State=%s' % values[12],
                    '-Country-PrimaryLocationName=%s' % values[13],
                    '-UsageTerms="Creative Commons BY-NC-SA"',
                    ]
            # Lista com keywords
            if values[3] == '' or values[3] is None:
                shellcall.append('-Keywords=')
            else:
                keywords = values[3].split(', ')
                for keyword in keywords:
                    shellcall.append('-Keywords=%s' % keyword.lower())
            shellcall.append(values[0])
            # Executando o comando completo
            stdout = subprocess.call(shellcall)
        except IOError:
            print '\nOcorreu algum erro. ',
            print 'Verifique se o ExifTool está instalado.'
            self.changeStatus(u'ERRO: Verifique se o exiftool está instalado',
                    10000)
            critical = QMessageBox()
            critical.setWindowTitle(u'Erro!')
            critical.setText(u'Verifique se o exiftool está instalado.')
            critical.setIcon(QMessageBox.Critical)
            critical.exec_()
        else:
            return stdout

    def changeStatus(self, status, duration=2000):
        '''Muda a mensagem de status da janela principal.'''
        self.statusBar().showMessage(status, duration)

    def openfile_dialog(self):
        '''Abre janela para escolher arquivos.

        Para selecionar arquivo(s) terminados em .jpg.
        '''
        filepaths = QFileDialog.getOpenFileNames(self, 'Selecionar imagem(ns)',
                './', 'Images (*.jpg)')
        if filepaths:
            n_all = len(filepaths)
            n_new = 0
            n_dup = 0
            t0 = time.time()
            self.changeStatus(u'Importando %d imagens...' % n_all)
            for filepath in filepaths:
                filename = os.path.basename(unicode(filepath))
                print filename
                matches = self.matchfinder(filename)
                if len(matches) == 0:
                    entrymeta = self.createmeta(filepath)
                    self.model.insert_rows(0, 1, QModelIndex(), entrymeta)
                    n_new += 1
                else:
                    n_dup += 1
                    pass
            t1 = time.time()
            t = t1 - t0
            self.changeStatus(u'%d imagens analisadas em %.2f s,' % (n_all, t) +
                    u' %d novas e %d duplicadas' % (n_new, n_dup), 10000)

    def opendir_dialog(self):
        '''Abre janela para selecionar uma pasta.
        
        Chama a função para varrer a pasta selecionada.
        '''
        folder = QFileDialog.getExistingDirectory(
                self,
                'Selecione uma pasta',
                './',
                QFileDialog.ShowDirsOnly
                )
        if folder:
            self.imgfinder(str(folder))

    def imgfinder(self, folder):
        '''Busca recursivamente imagens na pasta selecionada.
        
        É possível definir as extensões a serem procuradas. Quando um arquivo é
        encontrado ele verifica se já está na tabela. Se não estiver, ele chama
        a função para extrair os metadados e insere uma nova entrada.
        '''
        n_all = 0
        n_new = 0
        n_dup = 0

        # Tupla para o endswith()
        extensions = ('jpg', 'JPG', 'jpeg', 'JPEG')

        t0 = time.time()
        
        # Buscador de imagens em ação
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.endswith(extensions):
                    matches = self.matchfinder(filename)
                    if len(matches) == 0:
                        filepath = os.path.join(root, filename)
                        timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p',
                                time.localtime(os.path.getmtime(filepath)))                    
                        entrymeta = self.createmeta(filepath)
                        self.model.insert_rows(0, 1, QModelIndex(), entrymeta)
                        n_new += 1
                    else:
                        n_dup += 1
                        pass
                    n_all += 1
            else:	# Se o número máximo de imagens for atingido, finalizar
                t1 = time.time()
                t = t1 - t0
                self.changeStatus(u'%d imagens analisadas em %.2f s,' % (n_all, t) +
                        u' %d novas e %d duplicadas' % (n_new, n_dup), 10000)
                break
            
    def createmeta(self, filepath, charset='utf-8'):
        '''Define as variáveis extraídas dos metadados (IPTC) da imagem.

        Usa a biblioteca do arquivo iptcinfo.py e retorna lista com valores.
        '''
        filename = os.path.basename(unicode(filepath))
        self.changeStatus(u'Lendo os metadados de %s e criando variáveis...' %
                filename)
        # Criar objeto com metadados
        info = IPTCInfo(filepath, True)
        # Checando se o arquivo tem dados IPTC
        if len(info.data) < 4:
            print 'Imagem não tem dados IPTC!'

        # Definindo as variáveis                            # IPTC
        title = info.data['object name']                    # 5
        keywords = info.data['keywords']                    # 25
        author = info.data['by-line']                       # 80
        city = info.data['city']                            # 90
        sublocation = info.data['sub-location']             # 92
        state = info.data['province/state']                 # 95
        country = info.data['country/primary location name']# 101
        category = info.data['headline']                    # 105
        copyright = info.data['copyright notice']           # 116
        caption = info.data['caption/abstract']             # 120
        spp = info.data['original transmission reference']  # 103
        scale = info.data['special instructions']           # 40
        source = info.data['source']                        # 115

        # Criando timestamp
        timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p',
                time.localtime(os.path.getmtime(filepath)))
        # Cria a lista para tabela da interface
        entrymeta = [
                filepath,
                title,
                caption,
                ', '.join(keywords),
                category,
                spp,
                source,
                author,
                copyright,
                scale,
                sublocation,
                city,
                state,
                country,
                timestamp,
                ]
        # Converte valores dos metadados vazios (None) para string em branco
        # FIXME Checar se isso está funcionando direito...
        for index in [index for index, field in enumerate(entrymeta) if \
                field is None]:
            field = u''
            entrymeta[index] = field
        else:
            pass

        self.createthumbs(filepath)

        return entrymeta

    def createthumbs(self, filepath):
        '''Cria thumbnails para as fotos novas.'''

        size = 400, 400
        hasdir = os.path.isdir(thumbdir)
        if hasdir is True:
            pass
        else:
            os.mkdir(thumbdir)
        filename = os.path.basename(str(filepath))
        thumbs = os.listdir(thumbdir)
        thumbpath = os.path.join(thumbdir, filename)
        if filename in thumbs:
            pass
        else:
            copy(unicode(filepath), thumbdir)
            self.changeStatus('%s copiado para %s' % (filename, thumbdir))
            try:
                im = Image.open(thumbpath)
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(thumbpath, 'JPEG')
            except IOError:
                print 'Não consegui criar o thumbnail...'

    def matchfinder(self, candidate):
        '''Verifica se entrada já está na tabela.

        O candidato pode ser o nome do arquivo (string) ou a entrada
        selecionada da tabela (lista). Retorna uma lista com duplicatas ou
        lista vazia caso nenhuma seja encontrada.
        '''
        index = self.model.index(0, 0, QModelIndex())
        if isinstance(candidate, list):
            value = os.path.basename(unicode(entry[0]))
            matches = self.model.match(index, 0, value, -1, Qt.MatchContains)
        else:
            matches = self.model.match(index, 0, candidate, -1, Qt.MatchContains)
        return matches

    def delcurrent(self):
        '''Deleta a(s) entrada(s) selecionada(s) da tabela.
        
        Verifica se a entrada a ser deletada está na lista de imagens
        modificadas. Se estiver, chama janela para o usuário decidir se quer
        apagar a entrada mesmo sem as modificações terem sido gravadas na
        imagem. Caso a resposta seja positiva a entrada será apagada e retirada
        da lista de imagens modificadas.
        '''
        indexes = mainWidget.selectionModel.selectedRows()
        if indexes:
            n_del = 0
            # Cria lista com linhas a serem deletadas
            indexes = [index.row() for index in indexes]
            unsaved = []
            for row in indexes:
                index = mainWidget.model.index(row, 0, QModelIndex())
                filepath = mainWidget.model.data(index, Qt.DisplayRole)
                filename = os.path.basename(unicode(filepath.toString()))
                if filename in self.dockUnsaved.mylist:
                    unsaved.append(filename)
                else:
                    continue
            #TODO Tem algum jeito de melhorar esse função?
            if len(unsaved) > 0:
                warning = QMessageBox.warning(
                        self,
                        u'Atenção!',
                        u'As alterações não foram gravadas nas imagens.' +
                        '\nDeseja apagá-las mesmo assim?',
                        QMessageBox.Yes,
                        QMessageBox.No)
                if warning == QMessageBox.Yes:
                    for filename in unsaved:
                        mainWidget.emitlost(filename)
                    # Ordem decrescente previne contra o erro 'out of range'
                    # na hora de deletar diversas entradas
                    indexes.sort()
                    indexes.reverse()
                    for index in indexes:
                        self.model.remove_rows(index, 1, QModelIndex())
                        n_del += 1
                    self.changeStatus(u'%d entradas deletadas' % n_del)
                else:
                    self.changeStatus(
                            u'Nenhuma entrada apagada, grave as alterações',
                            10000
                            )
            else:
                # Ordem decrescente previne contra o erro 'out of range'
                # na hora de deletar diversas entradas
                indexes.sort()
                indexes.reverse()
                for index in indexes:
                    self.model.remove_rows(index, 1, QModelIndex())
                    n_del += 1
                self.changeStatus(u'%d entradas deletadas' % n_del)
        else:
            self.changeStatus(u'Nenhuma entrada selecionada')

    def cleartable(self):
        '''Remove todas as entradas da tabela.

        Antes de deletar checa se existem imagens não-salvas na lista.
        '''
        # Ver se não dá pra melhorar...
        if len(self.dockUnsaved.mylist) == 0:
            rows = self.model.rowCount(self.model)
            if rows > 0:
                self.model.remove_rows(0, rows, QModelIndex())
                self.changeStatus(u'%d entradas deletadas' % rows)
            else:
                self.changeStatus(u'Nenhuma entrada selecionada')
        else:
            warning = QMessageBox.warning(
                    self,
                    u'Atenção!',
                    u'As alterações não foram gravadas nas imagens.' +
                    '\nDeseja apagá-las mesmo assim?',
                    QMessageBox.Yes,
                    QMessageBox.No)
            if warning == QMessageBox.Yes:
                rows = self.model.rowCount(self.model)
                if rows > 0:
                    self.model.remove_rows(0, rows, QModelIndex())
                    mainWidget.emitsaved()
                    self.changeStatus(u'%d entradas deletadas' % rows)
                else:
                    self.changeStatus(u'Nenhuma entrada selecionada')

    def cachetable(self):
        '''Salva estado atual dos dados em arquivos externos.
        
        Cria backup dos conteúdos da tabela e da lista de imagens modificadas.
        '''
        print 'Salvando cache...',
        self.changeStatus(u'Salvando cache...')
        # Tabela
        tablecache = open(tablepickle, 'wb')
        entries = mainWidget.model.mydata
        pickle.dump(entries, tablecache)
        tablecache.close()
        # Lista
        listcache = open(listpickle, 'wb')
        entries = self.dockUnsaved.mylist
        pickle.dump(entries, listcache)
        listcache.close()
        print 'pronto!'
        self.changeStatus(u'Salvando cache... pronto!')

    def closeEvent(self, event):
        '''O que fazer quando o programa for fechado.'''
        reply = QMessageBox.question(
                self,
                u'Atenção!',
                u'O programa será finalizado.\nVocê está certo disso?',
                QMessageBox.Yes,
                QMessageBox.No
                )
        if reply == QMessageBox.Yes:
            event.accept()
            self.cachetable()
        else:
            event.ignore()


class MainTable(QTableView):
    '''Tabela principal com entradas.'''
    def __init__(self, datalist, header, *args):
        QTableView.__init__(self, *args)

        self.header = header
        self.mydata = datalist

        self.model = TableModel(self, self.mydata, self.header)
        self.setModel(self.model)
        self.selectionModel = self.selectionModel()
        self.selectionModel.clearSelection()

        self.nrows = self.model.rowCount(self.model)
        self.ncols = self.model.columnCount(self.model)

        vh = self.verticalHeader()
        vh.setVisible(False)
        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)

        # TODO Estudar o melhor jeito de chamar.
        # Também pode ser no singular com index.
        self.cols_resized = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        for col in self.cols_resized:
            self.resizeColumnToContents(col)
        self.setColumnWidth(1, 250)
        self.setColumnWidth(2, 200)
        self.setColumnWidth(3, 250)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(self.SelectRows)
        self.setSortingEnabled(True)
        self.hideColumn(0)
        self.hideColumn(14)
        self.selecteditems = []

        # Para limpar entrada dumb na inicialização
        if self.nrows == 1 and self.mydata[0][0] == '':
            self.model.remove_rows(0, 1, QModelIndex())

        #self.connect(
        #        self.selectionModel,
        #        SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
        #        self.update_selection)

        self.connect(
                self.selectionModel,
                SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                self.changecurrent)

        self.connect(
                self.verticalScrollBar(),
                SIGNAL('valueChanged(int)'),
                self.outputrows
                )

        self.connect(
                self.model,
                SIGNAL('dataChanged(index, value, oldvalue)'),
                self.editmultiple
                )

        self.connect(
                self.model,
                SIGNAL('dataChanged(index, value, oldvalue)'),
                self.resizecols
                )

    def editmultiple(self, index, value, oldvalue):
        '''Edita outras linhas selecionadas.'''
        rows = self.selectionModel.selectedRows()
        if len(rows) > 1:
            for row in rows:
                self.selectionModel.clearSelection()
                index = self.model.index(row.row(), index.column(), QModelIndex())
                self.model.setData(index, value, Qt.EditRole)

    def resizecols(self, index):
        '''Ajusta largura das colunas da tabela.'''
        if index.column() in self.cols_resized:
            self.resizeColumnToContents(index.column())

    def outputrows(self, toprow):
        '''Identifica linhas dentro do campo de visão da tabela.'''
        pass
        #TODO Está funcionando, só precisa ver se vale a pena usar...
        #bottomrow = self.verticalHeader().visualIndexAt(self.height())
        #rows = xrange(toprow, bottomrow)
        #for row in rows:
        #    index = self.model.index(row, 0, QModelIndex())
        #    filepath = self.model.data(index, Qt.DisplayRole)
        #    filepath = unicode(filepath.toString())
        #    self.emit(SIGNAL('visibleRow(filepath)'), filepath)

    def emitsaved(self):
        '''Emite aviso que os metadados foram gravados nos arquivos.'''
        self.emit(SIGNAL('savedToFile()'))

    def emitlost(self, filename):
        '''Emite aviso para remover entrada da lista de modificados.'''
        self.emit(SIGNAL('delEntry(filename)'), filename)

    def update_selection(self, selected, deselected):
        '''Pega a entrada selecionada, extrai os valores envia para editor.

        Os valores são enviados através de um sinal.
        '''
        #TODO Função obsoleta, ver se tem algo para aproveitar.
        deselectedindexes = deselected.indexes()
        if not deselectedindexes:
            selectedindexes = selected.indexes()
            self.selecteditems.append(selectedindexes)
        else:
            del self.selecteditems[:]
            selectedindexes = selected.indexes()
            self.selecteditems.append(selectedindexes)
        # Criando valores efetivamente da entrada selecionada.
        values = []
        for index in selectedindexes:
            value = self.model.data(index, Qt.DisplayRole)
            values.append((index, value.toString()))
        #self.emit(SIGNAL('thisIsCurrent(values)'), values)

    def changecurrent(self, current, previous):
        '''Identifica a célula selecionada, extrai valores e envia para editor.

        Os valores são enviados através de um sinal.
        '''
        values = []
        for col in xrange(self.ncols):
            index = self.model.index(current.row(), col, QModelIndex())
            value = self.model.data(index, Qt.DisplayRole)
            values.append((index, value.toString()))
        self.emit(SIGNAL('thisIsCurrent(values)'), values)


class TableModel(QAbstractTableModel):
    '''Modelo dos dados.'''
    def __init__(self, parent, mydata, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mydata = mydata
        self.header = header

    def rowCount(self, parent):
        '''Conta as linhas.'''
        return len(self.mydata)

    def columnCount(self, parent):
        '''Conta as colunas.'''
        return len(self.mydata[0])

    def data(self, index, role):
        '''Transforma dados brutos em elementos da tabela.'''
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole and \
                role != Qt.BackgroundRole:
            return QVariant()
        return QVariant(self.mydata[index.row()][index.column()])
        
    def headerData(self, col, orientation, role):
        '''Constrói cabeçalho da tabela.'''
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])
        return QVariant()

    def flags(self, index):
        '''Indicadores do estado de cada ítem.'''
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def setData(self, index, value, role):
        '''Salva alterações nos dados a partir da edição da tabela.'''
        if index.isValid() and role == Qt.EditRole:
            oldvalue = self.mydata[index.row()][index.column()]
            if index.column() == 3:
                self.mydata[index.row()][index.column()] = unicode(
                        value.toString()).lower()
            else:
                self.mydata[index.row()][index.column()] = value.toString()
            self.emit(SIGNAL('dataChanged(index, value, oldvalue)'),
                    index, value, oldvalue)
            return True
        return False
    
    def sort(self, col, order):
        '''Ordena entradas a partir de valores de determinada coluna'''
        self.emit(SIGNAL('layoutAboutToBeChanged()'))
        self.mydata = sorted(self.mydata, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mydata.reverse()
        self.emit(SIGNAL('layoutChanged()'))

    def setcolor(self, index, role):
        '''Pinta células da tabela.'''
        #FIXME Não funciona.
        print index, role
        if index.isValid() and role == Qt.BackgroundRole:
            return QVariant(QColor(Qt.yellow))

    def insert_rows(self, position, rows, parent, entry):
        '''Insere entrada na tabela.'''
        self.beginInsertRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mydata.append(entry)
        self.endInsertRows()
        return True

    def remove_rows(self, position, rows, parent):
        '''Remove entrada da tabela.'''
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mydata.pop(position)
        self.endRemoveRows()
        return True


class DockEditor(QWidget):
    '''Dock com campos para edição dos metadados.'''
    def __init__(self):
        QWidget.__init__(self)

        varnames = [
                ['title', 'caption', 'tags'],
                ['taxon', 'spp', 'source', 'author', 'rights'],
                ['size', 'location', 'city', 'state', 'country']
                ]
        labels = [
                [u'Título', u'Legenda', u'Marcadores'],
                [u'Táxon', u'Espécie', u'Especialista', u'Autor', u'Direitos'],
                [u'Tamanho', u'Local', u'Cidade', u'Estado', u'País']
                ]
        self.sizes = [
                '',
                '<0,1 mm',
                '0,1 - 1,0 mm',
                '1,0 - 10 mm',
                '10 - 100 mm',
                '>100 mm'
                ]

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        e = 'Edit'

        for box in varnames:
            box_index = varnames.index(box)
            box_layid = 'form' + str(box_index)
            box_id = 'wid' + str(box_index)
            setattr(self, box_layid, QFormLayout())
            setattr(self, box_id, QWidget())
            for var in box:
                var_index = box.index(var)
                setattr(self, var, QLabel('&' + labels[box_index][var_index] + ':'))
                if var == 'caption':
                    setattr(self, var + e, QTextEdit())
                    self.captionEdit.setTabChangesFocus(True)
                elif var == 'size':
                    setattr(self, var + e, QComboBox())
                    eval('self.' + var + e + '.addItems(self.sizes)')
                else:
                    setattr(self, var + e, QLineEdit())
                label = eval('self.' + var)
                edit = eval('self.' + var + e)
                label.setBuddy(edit)
                if box_index == 0:
                    self.form0.addRow(label, edit)
                elif box_index == 1:
                    self.form1.addRow(label, edit)
                elif box_index == 2:
                    self.form2.addRow(label, edit)
            eval('self.' + box_id + '.setLayout(self.' + box_layid + ')')
            self.hbox.addWidget(eval('self.' + box_id))

        self.setMaximumHeight(180)

        self.connect(
                mainWidget,
                SIGNAL('thisIsCurrent(values)'),
                self.setcurrent
                )

        self.connect(
                mainWidget.model,
                SIGNAL('dataChanged(index, value, oldvalue)'),
                self.setsingle
                )

    def setsingle(self, index, value, oldvalue):
        '''Atualiza campo de edição correspondente quando dado é alterado.'''
        print index.row(), index.column(), value.toString(), oldvalue
        if index.column() == 1:
            self.titleEdit.setText(value.toString())
        elif index.column() == 2:
            self.captionEdit.setText(value.toString())
        elif index.column() == 3:
            self.tagsEdit.setText(value.toString())
        elif index.column() == 4:
            self.taxonEdit.setText(value.toString())
        elif index.column() == 5:
            self.sppEdit.setText(value.toString())
        elif index.column() == 6:
            self.sourceEdit.setText(value.toString())
        elif index.column() == 7:
            self.authorEdit.setText(value.toString())
        elif index.column() == 8:
            self.rightsEdit.setText(value.toString())
        elif index.column() == 9:
            for interval in self.sizes:
                if value.toString() == interval:
                    idx = self.sizes.index(interval)
                    self.sizeEdit.setCurrentIndex(idx)
                else:
                    pass
        elif index.column() == 10:
            self.locationEdit.setText(value.toString())
        elif index.column() == 11:
            self.cityEdit.setText(value.toString())
        elif index.column() == 12:
            self.stateEdit.setText(value.toString())
        elif index.column() == 13:
            self.countryEdit.setText(value.toString())

    def setcurrent(self, values):
        '''Atualiza campos de edição quando entrada é selecionada na tabela.'''
        if values:
            self.titleEdit.setText(values[1][1])
            self.captionEdit.setText(values[2][1])
            self.tagsEdit.setText(values[3][1])
            self.taxonEdit.setText(values[4][1])
            self.sppEdit.setText(values[5][1])
            self.sourceEdit.setText(values[6][1])
            self.authorEdit.setText(values[7][1])
            self.rightsEdit.setText(values[8][1])
            for interval in self.sizes:
                if values[9][1] == interval:
                    idx = self.sizes.index(interval)
                    self.sizeEdit.setCurrentIndex(idx)
                else:
                    pass
            self.locationEdit.setText(values[10][1])
            self.cityEdit.setText(values[11][1])
            self.stateEdit.setText(values[12][1])
            self.countryEdit.setText(values[13][1])
            self.values = values

    def savedata(self):
        '''Salva valores dos campos para a tabela.'''
        mainWidget.model.setData(self.values[1][0],
                QVariant(self.titleEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[2][0],
                QVariant(self.captionEdit.toPlainText()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[3][0],
                QVariant(unicode(self.tagsEdit.text()).lower()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[4][0],
                QVariant(self.taxonEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[5][0],
                QVariant(self.sppEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[6][0],
                QVariant(self.sourceEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[7][0],
                QVariant(self.authorEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[8][0],
                QVariant(self.rightsEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[9][0],
                QVariant(self.sizeEdit.currentText()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[10][0],
                QVariant(self.locationEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[11][0],
                QVariant(self.cityEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[12][0],
                QVariant(self.stateEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[13][0],
                QVariant(self.countryEdit.text()),
                Qt.EditRole)
        mainWidget.setFocus(Qt.OtherFocusReason)


class DockThumb(QWidget):
    '''Dock para mostrar o thumbnail da imagem selecionada.'''
    def __init__(self):
        QWidget.__init__(self)

        self.setMaximumWidth(400)
        self.vbox = QVBoxLayout()
        self.pic = QPixmap()
        self.thumb = QLabel()
        self.name = QLabel()
        self.timestamp = QLabel()

        self.thumb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.thumb.setMaximumWidth(400)
        self.thumb.setMinimumSize(100, 100)
        self.thumb.setAlignment(Qt.AlignHCenter)

        self.vbox.addWidget(self.thumb)
        self.vbox.addWidget(self.name)
        self.vbox.addWidget(self.timestamp)
        self.vbox.addStretch(1)

        self.name.setWordWrap(True)
        self.setLayout(self.vbox)

        #XXX omitir enquanto o insert abaixo não funcionar
        #self.pixcache = {}
        QPixmapCache.setCacheLimit(81920)

        self.connect(
                mainWidget,
                SIGNAL('thisIsCurrent(values)'),
                self.setcurrent
                )

        self.connect(
                mainWidget,
                SIGNAL('visibleRow(filepath)'),
                self.pixmapcache
                )

    def pixmapcache(self, filepath):
        '''Cria cache para thumbnail.'''
        filename = os.path.basename(unicode(filepath))
        thumbpath = os.path.join(thumbdir, filename)
        # Tenta abrir o cache
        if not QPixmapCache.find(filename, self.pic):
            self.pic.load(thumbpath)
            print 'Criando cache da imagem %s...' % filename,
            QPixmapCache.insert(filename, self.pic)
            print 'pronto!'
        else:
            pass
        return self.pic
    
    def setcurrent(self, values):
        '''Mostra thumbnail, nome e data de modificação da imagem.

        Captura sinal com valores, tenta achar imagem no cache e exibe
        informações.
        '''
        if values and values[0][1] != '':
            filename = os.path.basename(str(values[0][1]))
            self.name.setText(unicode(filename))
            timestamp = values[14][1]
            self.timestamp.setText(timestamp)

            #XXX omitir enquanto o insert abaixo não funcionar
            #if filename not in self.pixcache.keys():
            #    self.pixcache[filename] = ''

            # Tenta abrir o cache
            self.pic = self.pixmapcache(values[0][1])
        elif values and values[0][1] == '':
            self.pic = QPixmap()
            self.name.clear()
            self.timestamp.clear()
            self.thumb.clear()
        else:
            self.pic = QPixmap()
            self.name.clear()
            self.timestamp.clear()
            self.thumb.clear()
        self.updateThumb()

    def updateThumb(self):
        '''Atualiza thumbnail.'''
        if self.pic.isNull():
            self.thumb.setText(u'Imagem indisponível')
            pass
        else:
            scaledpic = self.pic.scaled(self.width(),
                    self.height()-65,
                    Qt.KeepAspectRatio, Qt.FastTransformation)
            self.thumb.setPixmap(scaledpic)

    def resizeEvent(self, event):
        '''Lida com redimensionamento do thumbnail.'''
        event.accept()
        self.updateThumb()


class DockUnsaved(QWidget):
    '''Exibe lista com imagens modificadas.

    Utiliza dados do modelo em lista. Qualquer imagem modificada será
    adicionada à lista. Seleção na lista seleciona entrada na tabela. Gravar
    salva metadados de cada ítem da lista nas respectivas imagens.
    '''
    def __init__(self):
        QWidget.__init__(self)

        self.mylist = updatelist
        self.model = ListModel(self, self.mylist)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.selectionModel = self.view.selectionModel()
        self.view.setAlternatingRowColors(True)

        self.clearselection = QAction('Limpar seleção', self)
        self.clearselection.setShortcut('Esc')
        self.clear = lambda: self.view.selectionModel.clearSelection()
        self.clearselection.triggered.connect(self.clear)
        self.addAction(self.clearselection)

        self.savebutton = QPushButton('&Gravar', self)
        self.savebutton.setShortcut('Ctrl+Shift+S')
        if not self.model.mylist:
            self.savebutton.setDisabled(True)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.view)
        self.vbox.addWidget(self.savebutton)
        self.setLayout(self.vbox)

        self.connect(
                mainWidget.model,
                SIGNAL('dataChanged(index, value, oldvalue)'),
                self.insertentry
                )

        self.connect(
                self.view.selectionModel,
                SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                self.sync_setselection
                )

        self.connect(
                self.savebutton,
                SIGNAL('clicked()'),
                self.writeselected
                )

        self.connect(
                mainWidget,
                SIGNAL('savedToFile()'),
                self.clearlist
                )

        self.connect(
                mainWidget,
                SIGNAL('delEntry(filename)'),
                self.delentry
                )

    def sync_setselection(self, selected, deselected):
        '''Sincroniza seleção da tabela com a seleção da lista.'''
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            filename = self.model.data(index, Qt.DisplayRole)
            filename = filename.toString()
            self.emit(SIGNAL('syncSelection(filename)'), filename)

    def writeselected(self):
        '''Emite sinal para gravar metadados na imagem.'''
        self.emit(SIGNAL('commitMeta(entries)'), self.mylist)

    def insertentry(self, index, value, oldvalue):
        '''Insere entrada na lista.
        
        Checa se a modificação não foi nula (valor atual == valor anterior) e
        se a entrada é duplicada.
        '''
        if value == oldvalue:
            pass
        else:
            index = mainWidget.model.index(index.row(), 0, QModelIndex())
            filepath = mainWidget.model.data(index, Qt.DisplayRole)
            filename = os.path.basename(unicode(filepath.toString()))
            matches = self.matchfinder(filename)
            if len(matches) == 0:
                self.model.insert_rows(0, 1, QModelIndex(), filename)
                self.savebutton.setEnabled(True)
            else:
                pass

    def delentry(self, filename):
        '''Remove entrada da lista.'''
        matches = self.matchfinder(filename)
        if len(matches) == 1:
            match = matches[0]
            self.model.remove_rows(match.row(), 1, QModelIndex())
            if not self.model.mylist:
                self.savebutton.setDisabled(True)

    def clearlist(self):
        '''Remove todas as entradas da lista.'''
        rows = self.model.rowCount(self.model)
        if rows > 0:
            self.model.remove_rows(0, rows, QModelIndex())
            self.savebutton.setDisabled(True)
        else:
            print 'Nada pra deletar.'

    def matchfinder(self, candidate):
        '''Buscador de duplicatas.'''
        index = self.model.index(0, 0, QModelIndex())
        matches = self.model.match(index, 0, candidate, -1, Qt.MatchExactly)
        return matches

    def resizeEvent(self, event):
        '''Lida com redimensionamentos.'''
        event.accept()


class ListModel(QAbstractListModel):
    '''Modelo com lista de imagens modificadas.'''
    def __init__(self, parent, list, *args):
        QAbstractListModel.__init__(self, parent, *args)
        self.mylist = list

    def rowCount(self, parent):
        '''Conta linhas.'''
        return len(self.mylist)

    def data(self, index, role):
        '''Cria elementos da lista a partir dos dados.'''
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.mylist[index.row()])

    def insert_rows(self, position, rows, parent, entry):
        '''Insere linhas.'''
        self.beginInsertRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mylist.append(entry)
        self.endInsertRows()
        return True

    def remove_rows(self, position, rows, parent):
        '''Remove linhas.'''
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mylist.pop(position)
        self.endRemoveRows()
        return True


class FlushFile(object):
    '''Tira o buffer do print.

    Assim rola juntar prints diferentes na mesma linha. Só pra ficar
    bonitinho... meio inútil.
    '''
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()


#=== MAIN ===#


class InitPs():
    '''Inicia variáveis e parâmetros globais do programa.'''
    def __init__(self):
        global tablepickle
        global listpickle
        global header
        global datalist
        global updatelist
        global thumbdir

        thumbdir = './thumbs'

        # Redefine o stdout para ser flushed após print
        sys.stdout = FlushFile(sys.stdout)
        
        # Cabeçalho horizontal da tabela principal
        header = [
                u'Arquivo', u'Título', u'Legenda', u'Marcadores',
                u'Táxon', u'Espécie', u'Especialista', u'Autor', u'Direitos',
                u'Tamanho', u'Local', u'Cidade', u'Estado', u'País',
                u'Timestamp'
                ]
        
        # Nome do arquivo Pickle para tabela
        tablepickle = 'tablecache'
        try:
            tablecache = open(tablepickle, 'rb')
            datalist = pickle.load(tablecache)
            tablecache.close()
            if not datalist:
                datalist.append([
                    u'', u'', u'', u'', u'',
                    u'', u'', u'', u'', u'',
                    u'', u'', u'', u'', u'',
                    ])
        except:
            f = open(tablepickle, 'wb')
            f.close()
            datalist = [[
                u'', u'', u'', u'', u'',
                u'', u'', u'', u'', u'',
                u'', u'', u'', u'', u'',
                ],]
        # Nome do arquivo Pickle para lista
        listpickle = 'listcache'
        try:
            listcache = open(listpickle, 'rb')
            updatelist = pickle.load(listcache)
            listcache.close()
        except:
            f = open(listpickle, 'wb')
            f.close()
            updatelist = []

if __name__ == '__main__':
    initps = InitPs()
    app = QApplication(sys.argv)
    main = MainWindow()

    main.show()
    sys.exit(app.exec_())
