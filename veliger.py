#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# VELIGER
# Copyleft 2010 - Bruno C. Vellutini | organelas.com
# 
# TODO Inserir licença.
#
# Atualizado: 09 Mar 2010 08:12PM
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

from PIL import Image as pil_image
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
    def __init__(self):
        QMainWindow.__init__(self)

        # Definições
        global mainWidget
        mainWidget = MainTable(datalist, header)
        self.model = mainWidget.model
        # Dock com thumbnail
        self.dockThumb = DockThumb()
        self.dockWidgetRight = QDockWidget('Thumbnail', self)
        self.dockWidgetRight.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
                )
        self.dockWidgetRight.setWidget(self.dockThumb)
        # Dock com lista de updates
        self.dockList = DockChanged()
        self.dockWidgetRight2 = QDockWidget('Entradas modificadas', self)
        self.dockWidgetRight2.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
                )
        self.dockWidgetRight2.setWidget(self.dockList)
        # Dock com editor de metadados
        self.dockEditor = DockEditor()
        self.dockWidgetBottom = QDockWidget('Editor', self)
        self.dockWidgetBottom.setAllowedAreas(
                Qt.TopDockWidgetArea |
                Qt.BottomDockWidgetArea
                )
        self.dockWidgetBottom.setWidget(self.dockEditor)

        # Atribuições da MainWindow
        self.setCentralWidget(mainWidget)
        self.setWindowTitle(u'VÉLIGER - Editor de Metadados')
        self.setWindowIcon(QIcon('./icons/python.svg'))
        self.setToolTip('Tabela com todas as entradas')
        self.statusBar().showMessage('Ready to Rock!', 2000)
        self.menubar = self.menuBar()

        # Menu
        self.exit = QAction(QIcon('./icons/system-shutdown.png'), 'Sair', self)
        self.exit.setShortcut('Ctrl+Q')
        self.exit.setStatusTip('Fechar o programa')
        self.connect(self.exit, SIGNAL('triggered()'), SLOT('close()'))

        self.openFile = QAction(QIcon('./icons/document-open.png'), 'Abrir arquivo(s)', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.setStatusTip('Abrir imagens')
        self.connect(self.openFile, SIGNAL('triggered()'), self.openDialog)

        self.openDir = QAction(QIcon('./icons/folder-new.png'), 'Abrir pasta(s)', self)
        self.openDir.setShortcut('Ctrl+D')
        self.openDir.setStatusTip('Abrir pasta')
        self.connect(self.openDir, SIGNAL('triggered()'), self.openDirDialog)

        self.delRow = QAction(QIcon('./icons/edit-delete.png'), 'Deletar entrada(s)', self)
        self.delRow.setShortcut('Ctrl+W')
        self.delRow.setStatusTip('Deletar entrada')
        self.connect(self.delRow, SIGNAL('triggered()'), self.delcurrent)

        self.saveFile = QAction(QIcon('./icons/document-save.png'), 'Salvar metadados', self)
        self.saveFile.setShortcut('Ctrl+S')
        self.saveFile.setStatusTip('Salvar metadados')
        self.connect(self.saveFile, SIGNAL('triggered()'),
                self.dockEditor.saveData)
        salvo = lambda: self.changeStatus(u'Alterações salvas!')
        self.saveFile.triggered.connect(salvo)

        self.delAll = QAction(QIcon('./icons/edit-delete.png'), 'Limpar tabela', self)
        self.delAll.setStatusTip('Deletar todas as entradas')
        self.connect(self.delAll, SIGNAL('triggered()'), self.cleartable)

        self.toggleThumb = self.dockWidgetRight.toggleViewAction()
        self.toggleThumb.setShortcut('Shift+T')
        self.toggleThumb.setStatusTip('Esconde ou mostra o dock com thumbnails')

        self.toggleEditor = self.dockWidgetBottom.toggleViewAction()
        self.toggleEditor.setShortcut('Shift+E')
        self.toggleEditor.setStatusTip('Esconde ou mostra o dock com thumbnails')

        self.arquivo = self.menubar.addMenu('&Arquivo')
        self.arquivo.addAction(self.openFile)
        self.arquivo.addAction(self.openDir)
        self.arquivo.addAction(self.saveFile)
        self.arquivo.addSeparator()
        self.arquivo.addAction(self.exit)

        self.editar = self.menubar.addMenu('&Editar')
        self.editar.addAction(self.delAll)
        self.editar.addSeparator()
        self.editar.addAction(self.toggleThumb)
        self.editar.addAction(self.toggleEditor)

        # Toolbar
        self.toolbar = self.addToolBar('Ações')
        self.toolbar.addAction(self.openFile)
        self.toolbar.addAction(self.openDir)
        self.toolbar.addAction(self.saveFile)
        self.toolbar.addAction(self.delRow)
        self.toolbar = self.addToolBar('Sair')
        self.toolbar.addAction(self.exit)

        # Docks
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetRight)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetRight2)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidgetBottom)
        self.tabifyDockWidget(self.dockWidgetRight, self.dockWidgetRight2)
        #self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # Fill Editor
        #self.onClicked = lambda: self.changeStatus('lala')
        #self.connect(
        #    self.mainWidget.selectionModel,
        #    SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
        #    self,
        #    self.onClicked())

        self.resize(1000, 780)

    def changeStatus(self, status, duration=2000):
        self.statusBar().showMessage(status, duration)

    def openDialog(self):
        filepaths = QFileDialog.getOpenFileNames(self, 'Selecione imagem(ns)',
                './', 'Images (*.jpg)')
        if filepaths:
            n_all = len(filepaths)
            n_new = 0
            n_dup = 0
            t0 = time.time()
            self.changeStatus(u'Importando %d imagens...' % n_all)
            for filepath in filepaths:
                filename = os.path.basename(str(filepath))
                isduplicate = self.matchfinder(filename)
                if isduplicate is False:
                    entrymeta = self.createMeta(filepath)
                    self.model.insertRows(0, 1, QModelIndex(), entrymeta)
                    n_new += 1
                else:
                    n_dup += 1
                    pass
            t1 = time.time()
            t = t1 - t0
            self.changeStatus(u'%d imagens analisadas em %.2f s,' % (n_all, t) +
                    u' %d novas e %d duplicadas' % (n_new, n_dup), 10000)

    def openDirDialog(self):
        folder = QFileDialog.getExistingDirectory(
                self,
                'Selecione uma pasta',
                './',
                QFileDialog.ShowDirsOnly
                )
        if folder:
            self.imgGrab(str(folder))

    def imgGrab(self, folder):
        '''
        Busca recursivamente arquivos com extensão jpg|JPG na pasta determinada.
        '''
        # Zera contadores
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
                    # Checa por duplicatas na tabela
                    isduplicate = self.matchfinder(filename)
                    if isduplicate is False:
                        filepath = os.path.join(root, filename)
                        timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p',
                                time.localtime(os.path.getmtime(filepath)))                    
                        entrymeta = self.createMeta(filepath)
                        self.model.insertRows(0, 1, QModelIndex(), entrymeta)
                        n_new += 1
                    else:
                        n_dup += 1
                        pass

                    # Contador
                    n_all += 1
            
            else:	# Se o número máximo de imagens for atingido, finalizar
                t1 = time.time()
                t = t1 - t0
                self.changeStatus(u'%d imagens analisadas em %.2f s,' % (n_all, t) +
                        u' %d novas e %d duplicadas' % (n_new, n_dup), 10000)
                break
            
    def createMeta(self, filepath):
        '''Define as variáveis extraídas dos metadados (IPTC) da imagem.

        Usa a biblioteca do arquivo iptcinfo.py.
        '''

        filename = os.path.basename(str(filepath))

        print 'Lendo os metadados de %s e criando variáveis.' % filename
        
        # Criar objeto com metadados
        info = IPTCInfo(filepath)
        
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

        entrymeta = []

        # Cria a lista para tabela da interface
        entrymeta = [
                unicode(str(filepath)),
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

        return entrymeta

    def matchfinder(self, candidate):
        index = self.model.index(0, 0, QModelIndex())
        if isinstance(candidate, str):
            matches = self.model.match(index, 0, candidate, -1, Qt.MatchContains)
        elif isinstance(candidate, list):
            value = os.path.basename(str(entry[0]))
            matches = self.model.match(index, 0, value, -1, Qt.MatchContains)
        if len(matches) > 0:
            return True
        else:
            return False

    def delcurrent(self):
        indexes = mainWidget.selectionModel.selectedRows()
        if indexes:
            n_del = 0
            # Cria lista com linhas a serem deletadas
            indexes = [index.row() for index in indexes]
            # Ordem decrescente previne contra o erro 'out of range'
            # na hora de deletar diversas entradas
            indexes.sort()
            indexes.reverse()
            for index in indexes:
                self.model.removeRows(index, 1, QModelIndex())
                n_del += 1
            self.changeStatus(u'%d entradas deletadas' % n_del)
        else:
            self.changeStatus(u'Nenhuma entrada selecionada')

    def cleartable(self):
        rows = self.model.rowCount(self.model)
        if rows > 0:
            self.model.removeRows(0, rows, QModelIndex())
            self.changeStatus(u'%d entradas deletadas' % rows)
        else:
            self.changeStatus(u'Nenhuma entrada selecionada')

    def closeEvent(self, event):
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

    def cachetable(self):
        '''Salva a lista de imagens da tabela.'''
        tablecache = open(picdb, 'wb')
        entries = mainWidget.model.mydata
        print 'Salvando cache...',
        pickle.dump(entries, tablecache)
        tablecache.close()
        print 'pronto!'


class MainTable(QTableView):
    def __init__(self, datalist, header, *args):
        QTableView.__init__(self, *args)

        self.header = header
        self.mydata = datalist

        self.model = TableModel(self, self.mydata, self.header)
        self.setModel(self.model)
        
        self.nrows = self.model.rowCount(self.model)
        self.ncols = self.model.columnCount(self.model)

        self.selectionModel = self.selectionModel()
        self.selectionModel.clearSelection()

        vh = self.verticalHeader()
        vh.setVisible(False)

        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)

        # TODO Estudar o melhor jeito de chamar.
        # Também pode ser no singular com index.
        #self.resizeColumnsToContents()

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(self.SelectRows)
        self.setSortingEnabled(True)
        self.hideColumn(0)
        self.hideColumn(14)
        self.selecteditems = []

        #self.delegate = QItemDelegate(self)

        #self.setItemDelegate(self.delegate)

        self.connect(
                self.selectionModel,
                SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                self.updateSelection
                )

        self.connect(
                self.selectionModel,
                SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                self.changeCurrent
                )

        self.connect(
                self.model,
                SIGNAL('dataChanged(index)'),
                self.datawatcher
                )

        # Não funcionou ainda, fazer a edição da tabela refletir nos campos
        #self.connect(
        #        self.selectionModel,
        #        SIGNAL('dataChanged(index, index)'),
        #        self.changeCurrent
        #        )

    def updateSelection(self, selected, deselected):
        # TODO Descobrir o melhor jeito de lidar com seleção múltipla.
        # Aqui estou gerenciando uma lista de índices (self.selecteditems) de
        # cada ítem selecionado, mas ele não está adicionando ranges quando uso
        # o SHIFT, apenas os ítens clicados FIXME.
        deselectedindexes = deselected.indexes()
        if not deselectedindexes:
            selectedindexes = selected.indexes()
            self.selecteditems.append(selectedindexes)
            #value = self.model.data(items[1], Qt.DisplayRole)
            #print value.toString()
        else:
            del self.selecteditems[:]
            selectedindexes = selected.indexes()
            self.selecteditems.append(selectedindexes)

        # Criando valores efetivamente da entrada selecionada.
        values = []
        for index in selectedindexes:
            value = self.model.data(index, Qt.DisplayRole)
            values.append((index, value.toString()))
        self.emit(SIGNAL('thisIsCurrent(values)'), values)

        #for index in items:
        #    text = '%s, %s' % (index.row(), index.column())
        #    #print text

        #items = deselected.indexes()

        #for index in items:
        #    text = '%s, %s' % (index.row(), index.column())
        #    #print text

    def changeCurrent(self, current, previous):
        # XXX Serve pra rastrear índices individuais, estava usando para criar
        # a seleção. O que fazer agora com esse resto de código?
        values = []
        for col in xrange(self.ncols):
            index = self.model.index(current.row(), col, QModelIndex())
            value = self.model.data(index, Qt.DisplayRole)
            values.append((index, value.toString()))
        #self.emit(SIGNAL('thisIsCurrent(values)'), values)

    def datawatcher(self, index):
        print 'ALO'
        print index.row(), index.column()
        columns = self.selectionModel.selectedColumns(index.row())
        for column in columns:
            value = self.model.data(column, Qt.DisplayRole)
            print value.toString()

    #def paintEvent(self, event):
    #    print 'Algo foi pintado!'
    #    event.accept()


class TableModel(QAbstractTableModel):
    def __init__(self, parent, mydata, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mydata = mydata
        self.header = header

    def rowCount(self, parent):
        return len(self.mydata)

    def columnCount(self, parent):
        return len(self.mydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole and \
                role != Qt.BackgroundRole:
            return QVariant()
        return QVariant(self.mydata[index.row()][index.column()])
        #elif index.column() == 0:
            #return QVariant(os.path.basename(str(
                #self.mydata[index.row()][index.column()])))
            #icon = QPixmap(self.mydata[index.row()][0])
            #scaledIcon = icon.scaled(30, 30, Qt.KeepAspectRatio, Qt.FastTransformation)
            #return QIcon(scaledIcon)
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            oldvalue = self.mydata[index.row()][index.column()]
            self.mydata[index.row()][index.column()] = value.toString()
            self.emit(SIGNAL('dataChanged(index, value, oldvalue)'), index, value, oldvalue)
            return True
        elif index.isValid() and role == Qt.BackgroundRole:
            print 'Será?'
            return QVariant(QColor(Qt.yellow))
        return False
    
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mydata = sorted(self.mydata, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def setColor(self, index, role):
        print index, role
        if index.isValid() and role == Qt.BackgroundRole:
            print 'Será?'
            return QVariant(QColor(Qt.yellow))

    def insertRows(self, position, rows, parent, entry):
        self.beginInsertRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mydata.append(entry)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.mydata.pop(position)
        self.endRemoveRows()
        return True


class DockEditor(QWidget):
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
                self.setCurrent
                )

        self.connect(
                mainWidget.model,
                SIGNAL('dataChanged(index, value, oldvalue)'),
                self.setsingle
                )

        #self.connect(
        #        self.titleEdit,
        #        SIGNAL('textEdited(QString)'),
        #        self.updateData
        #        )

    #def updateData(self, text):
    #    print text
    #    mainWidget.model.setData(self.values[2][0], text, Qt.EditRole)

    def setsingle(self, index, value, oldvalue):
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

        # Colorir
        mainWidget.model.setData(index, value.toString(), Qt.BackgroundRole)
        print 'Coloriu?'

    def setCurrent(self, values):
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

    def saveData(self):
        # Salvar metadados novos usando o ExifTools
        print '\nSalvando metadados...'
        try:
            # Salva os metadados na imagem (sobrepondo os correspondentes
            # originais)
            subprocess.call([
                'exiftool',
                '-overwrite_original',
                '-City=%s' % self.cityEdit.text(),
                '-By-line=%s' % self.authorEdit.text(),
                '-Province-State=%s' % self.stateEdit.text(),
                '-Country-PrimaryLocationName=%s' % self.countryEdit.text(),
                '-CopyrightNotice=%s' % self.rightsEdit.text(),
                '-UsageTerms="Creative Commons BY-NC-SA"',
                '-ObjectName=%s' % self.titleEdit.text(),
                '-Caption-Abstract=%s' % self.captionEdit.toPlainText(),
                '-Sub-location=%s' % self.locationEdit.text(),
                '-Headline=%s' % self.taxonEdit.text(),
                '-OriginalTransmissionReference=%s' % self.sppEdit.text(),
                '-SpecialInstructions=%s' % self.sizeEdit.currentText(),
                '-Source=%s' % self.sourceEdit.text(),
                self.values[0][1]
                ])
            # Loop para incluir os keywords individualmente.
            # Lista com comando e argumentos
            shell_call = ['exiftool', '-overwrite_original']
            # Lista com keywords
            if self.tagsEdit.text() == '' or self.tagsEdit.text() is None:
                print 'Marcadores em branco, deletando na imagem...'
                shell_call.append('-Keywords=')
            else:
                print 'Atualizando marcadores...'
                keywords = self.tagsEdit.text().split(', ')
                for keyword in keywords:
                    keyword = str(keyword)
                    shell_call.append('-Keywords=%s' % keyword.lower())
            # Adicionando o endereço do arquivo ao comando
            shell_call.append(self.values[0][1])
            # Executando o exiftool para adicionar as keywords
            subprocess.call(shell_call)
        except IOError:
            print '\nOcorreu algum erro. Verifique se o ExifTool está \
                    instalado.'
        else:
            print '\nNovos metadados salvos na imagem com sucesso!'

        # Atualizando a tabela
        mainWidget.model.setData(self.values[1][0],
                QVariant(self.titleEdit.text()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[2][0],
                QVariant(self.captionEdit.toPlainText()),
                Qt.EditRole)
        mainWidget.model.setData(self.values[3][0],
                QVariant(self.tagsEdit.text()),
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
        print 'Salvo!'


class DockThumb(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setMaximumWidth(300)
        self.vbox = QVBoxLayout()
        self.pic = QPixmap()
        self.thumb = QLabel()
        self.name = QLabel()
        self.timestamp = QLabel()

        self.thumb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.thumb.setMaximumSize(300, 300)
        self.thumb.setMinimumSize(100, 100)
        self.thumb.setAlignment(Qt.AlignHCenter)

        self.name.setWordWrap(True)

        #self.originalPic = self.pic.scaled(self.thumb.width(), self.thumb.height(),
        #        Qt.KeepAspectRatio, Qt.FastTransformation)

        self.vbox.addWidget(self.thumb)
        self.vbox.addWidget(self.name)
        self.vbox.addWidget(self.timestamp)
        self.vbox.addStretch(1)

        #self.thumb.setPixmap(self.originalPic)

        self.setLayout(self.vbox)

        #XXX omitir enquanto o insert abaixo não funcionar
        #self.pixcache = {}
        QPixmapCache.setCacheLimit(81920)

        self.connect(
                mainWidget,
                SIGNAL('thisIsCurrent(values)'),
                self.setCurrent
                )
    
    def setCurrent(self, values):
        filename = os.path.basename(str(values[0][1]))
        self.name.setText(unicode(filename))
        timestamp = values[14][1]
        self.timestamp.setText(timestamp)

        #XXX omitir enquanto o insert abaixo não funcionar
        #if filename not in self.pixcache.keys():
        #    self.pixcache[filename] = ''

        # Tenta abrir o cache
        if not QPixmapCache.find(filename, self.pic):
            self.pic.load(values[0][1])
            self.pic = self.pic.scaled(self.thumb.maximumSize(),
                    Qt.KeepAspectRatio, Qt.FastTransformation)
            print 'Criando cache da imagem %s...' % filename,
            QPixmapCache.insert(filename, self.pic)
            print 'pronto!'
        else:
            pass
        self.updateThumb()

    def resizeEvent(self, event):
        event.accept()
        self.updateThumb()

    def updateThumb(self):
        if self.pic.isNull():
            pass
        else:
            scaledpic = self.pic.scaled(self.size(),
                    Qt.KeepAspectRatio, Qt.FastTransformation)
            self.thumb.setPixmap(scaledpic)


class DockChanged(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        list = []

        model = ListModel(self, list)

        view = QListView()
        view.setModel(model)
        view.setAlternatingRowColors(True)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(view)
        self.setLayout(self.vbox)

        #self.setMaximumWidth(300)
        #self.vbox.addWidget(self.name)
        #self.vbox.addWidget(self.timestamp)
        #self.vbox.addStretch(1)


    def resizeEvent(self, event):
        event.accept()


class ListModel(QAbstractListModel):
    def __init__(self, parent, list, *args):
        QAbstractListModel.__init__(self, parent, *args)
        self.list = list

    def rowCount(self, parent):
        return len(self.list)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.list[index.row()])

    def insertRows(self, position, rows, parent, entry):
        self.beginInsertRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.list.append(entry)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in xrange(rows):
            self.list.pop(position)
        self.endRemoveRows()
        return True


class FlushFile(object):
    '''
    Simplesmente para tirar o buffer do print, assim rola juntar prints
    diferentes na mesma linha. Só pra ficar bonitinho... meio inútil.
    '''
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()


#=== MAIN ===#


class InitPs():
    '''
    Inicia variáveis e parâmetros globais do programa antes de iniciar a
    interface gráfica.
    '''
    def __init__(self):
        global picdb
        global header
        global datalist

        # Redefine o stdout para ser flushed após print
        sys.stdout = FlushFile(sys.stdout)
        
        # Cabeçalho horizontal da tabela principal
        header = [
                u'Arquivo', u'Título', u'Legenda', u'Marcadores',
                u'Táxon', u'Espécie', u'Especialista', u'Autor', u'Direitos',
                u'Tamanho', u'Local', u'Cidade', u'Estado', u'País',
                u'Timestamp'
                ]
        
        # Nome do arquivo Pickle
        picdb = 'tablecache'
        # Leitura do cache, salvo pelo Pickle
        try:
            tablecache = open(picdb, 'rb')
            datalist = pickle.load(tablecache)
            tablecache.close()
        except:
            f = open(picdb, 'wb')
            f.close()
            datalist = [[
                u'', u'', u'', u'', u'',
                u'', u'', u'', u'', u'',
                u'', u'', u'', u'', u'',
                ],]

if __name__ == '__main__':
    initps = InitPs()
    app = QApplication(sys.argv)
    main = MainWindow()

    main.show()
    sys.exit(app.exec_())
