#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
CIFONAUTA_v0.4
Atualizado: 01 Feb 2010 01:54PM

Gerenciador do Banco de imagens do CEBIMar-USP
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

from bsddb3 import db

from iptcinfo import IPTCInfo
import wordpresslib
from eagle import *


# Diretório com as imagens
srcdir = '/home/nelas/Python/cifonauta_gui/imagens/source'
# Diretório espelho do site (imagens já carregadas)
webdir = '/home/nelas/Python/cifonauta_gui/imagens/web'

# Arquivo com marca d'água
watermark = 'marca.png'

# Nome do arquivo com banco de dados
dbname = 'database'

# Checar se o arquivo existe
# Se não existir, criar

# Criar a instância do bd
imgdb = db.DB()

# Abrir e/ou criar arquivo do banco de dados
imgdb.open(dbname, db.DB_BTREE, db.DB_CREATE)
imgdb.close()

# Dados para o cliente
# TODO Criar um arquivo separado para ler estas informações
wordpress = 'http://musica.organelas.com/xmlrpc.php'
user = 'nelas'
password = 'ce767JSg'

# GUI
def data_changed(app, widget, value):
    print 'changed:', app, widget, value
    idx, values = value
    if values:
        values[4] += ' [MODIFIED]'
        widget[idx] = values

def selection_changed(app, widget, selected):
    print 'seletion:', app, widget, selected
# GUI

def getCatList():
	'''
	Cria um objeto com a lista de categorias do blog.

	Evita que isso seja checado pra cada imagem.
	'''
	# Prepara o objeto do cliente XML-RPC
	wp = wordpresslib.WordPressClient(wordpress, user, password)
	
	# Seleciona o ID do blog
	wp.selectBlog(0)

	print 'Criando lista de categorias...'

	catlist = wp.getCategoryList()

	return catlist


def wpPostImg():
	'''
	Cria o cliente para acessar o website via XML-RPC.

	Pega as variáveis extraídas dos metadados da imagem e insere no post.

	Publica o post e grava metadados no banco de dados.
	'''

	print '\nIniciando a criação do post...\n'
	
	# Prepara o objeto do cliente XML-RPC
	wp = wordpresslib.WordPressClient(wordpress, user, password)
	
	# Seleciona o ID do blog
	wp.selectBlog(0)

	# Executa a função para processar a imagem (redimensionar e inserir marca d'água)
	imgResize()

	# Cria objeto da imagem, usando o endereço da imagem processada web_fpath
	imageSrc = wp.newMediaObject(web_fpath, False)
	
	# Se a imagem existir usar os metadados para criar o post
	if imageSrc:
		# Cria o objeto do post
		post = wordpresslib.WordPressPost()
		post.title = title		# Título
		post.tags = keywords		# Marcadores (tags)
		post.customFields = cfields	# 'Custom fields' do post
		
		# Conteúdo do post
		# FIXME É necessário inserir o 'imgSrc' no conteúdo do post para que a imagem seja anexada ao post, tentar contornar isso
		post.description = "<a id='baixar' title='Creative Commons BY-NC-SA' href='%s'>Download</a>" % imageSrc

		# Lidar com categorias vazias
		if category == None:
			pass
		else:
			# Verificar se a categoria já existe no site e se não existir, criar
			print '\nVerificando se %s já existe...' % category
			if category == None:
				print 'Categoria vazia.'
			elif category in catlist:
#			if wp.checkCatName(category) == True:
				print 'VIVA! A categoria ' + category + ' existe.'
				post.categories = (wp.getCategoryIdFromName(category),)
			else:
				print 'A categoria ' + category + ' não existe! Criando nova categoria...'
				post.categories = (wp.newCategory(category),)
				print category + ' criada com sucesso!'
		
		# Publicar o post no site
		print '\nCriando o post com a imagem...'
		idNewPost = wp.newPost(post, True)
		print '\nPost criado com sucesso! id=%d' % idNewPost

		dbPut(True, False, idNewPost)

		print '\nPronto! O registro foi incluído no arquivo "%s".' % dbname
		print 40 * '-'
		print

def wpUpdatePost():
	'''
	Atualiza post de imagem que foi modificada.
	'''

	print '\nIniciando a atualização do post...'

	# Pega o ID do post pelo n° de registro no banco de dados
	postId = recdata['postid']
	print 'Post ID=%d' % postId

	# Prepara o objeto do cliente XML-RPC
	wp = wordpresslib.WordPressClient(wordpress, user, password)
	
	# Seleciona o ID do blog
	wp.selectBlog(0)

	# getPost para ler os custom fields
	oldPost = wp.getPost(postId)
	oldCustomFields = oldPost.customFields
	newCustomFields = []

	# Comparar cada cfield novo com o do post publicado e definir o que fazer
	print '\nComparando...'
	for k, v in cfieldsDic.iteritems():
		for custom in oldCustomFields:
			if k != custom['key']:	# Se k do post for diferente do custom['key'], passar para o próximo
				pass
			else:			# Se existir a 'key' no post, mas o 'value' da imagem nova for None (vazio),
				if v == None:
					print '"%s" está vazio, deletando o custom field do post!' % k
					# Passar apenas o id do customfield = deletar o custom field do post publicado
					delCF = {
							'id': int(custom['id'])
							}
					# Inclui na lista
					newCustomFields.append(delCF)
					break
				else:		# Caso o 'value' não esteja vazio, atualizar o custom field
					print '"%s" existe e será atualizada para: %s' % (custom['key'], v)
					# Passar com o valor novo
					upCF = {
							'id' : int(custom['id']),
							'key' : custom['key'],
							'value' : v
							}
					# Inclui na lista
					newCustomFields.append(upCF)
					break
		else:	# Se depois de comparar cada cfield com os do post e não encontrar um correspondente,
			if v != None:	# e o value não for vazio
				print '"%s" não existe e será adicionada com o valor: %s' % (k, v)
				# criar um novo custom field no post publicado
				newCF = {
						'key': k,
						'value':v
						}
				# Inclui na lista
				newCustomFields.append(newCF)
		
	print '\nCustom fields atualizados!\n'

	# Executa a função para processar a imagem (redimensionar e inserir marca d'água)
	imgResize()
	
	print '\nCriando objeto para atualizar imagem...'
	# Cria objeto da imagem, usando o endereço da imagem processada web_fpath
	imageSrc = wp.newMediaObject(web_fpath, True)
	print 'Imagem atualizada!'

	if imageSrc:
		# Cria o objeto do post
		post = wordpresslib.WordPressPost()
		post.title = title			# Título
		post.tags = keywords			# Marcadores (tags)
		
		# 'Custom fields' do post
		post.customFields = newCustomFields
		
		print
		print 'Criado objeto com custom fields.'

		# Conteúdo do post
		# FIXME É necessário inserir o 'imgSrc' no conteúdo do post para que a imagem seja anexada ao post, tentar contornar isso
		post.description = "<a id='baixar' title='Creative Commons BY-NC-SA' href='%s'>Download</a>" % imageSrc
		
		# Definir categoria, teoricamente não precisa verificar se existe ou não
		post.categories = (wp.getCategoryIdFromName(category),)
	
		# Publicar o post no site
		print '\nAtualizando o post com a imagem...'
		wp.editPost(postId, post, True)
		print '\nPost atualizado com sucesso!'
		
	dbPut(True, False, postId)

def imgResize():
	'''
	Redimensiona a imagem e inclui marca d'água antes de fazer o upload.
	'''
	# Endereço do arquivo que será carregado ao site
	global web_fpath
	web_fpath = os.path.join(webdir, fname)

	# Checar se diretório web existe antes de começar
	if os.path.isdir(webdir) == False:
		os.mkdir(webdir)
		print 'Diretório web criado!'
	else:
		print 'Diretório web já existe!'
	
	# Começa a processar a imagem usando o ImageMagick
	print '\nProcessando a imagem...'
	try:
		# Converte para 72dpi, JPG qualidade 50 e redimensiona as imagens maiores que 640 (em altura ou largura)
		subprocess.call(['convert', fpath, '-density', '72', '-format', 'jpg', '-quality', '50', '-resize', '640x640>', web_fpath])
		# Insere marca d'água no canto direito embaixo
		subprocess.call(['composite', '-dissolve', '20', '-gravity', 'southeast', watermark, web_fpath, web_fpath])
	except IOError:
		print '\nOcorreu algum erro na conversão da imagem. Verifique se o ImageMagick está instalado.'
	else:
		print 'Imagem convertida com sucesso!'


def dbPut(www, mod, idpost):
	'''
	Cria ou atualiza registro no banco de dados.

	Pega o id do post novo, do post que será atualizado ou um valor neutro (0) para imagens sem post.

	Usar www=True para imagens carregadas no site e False para imagens ainda não carregadas.
	'''

	# Atualizar a data de modificação no registro do banco de dados
	print '\nAtualizando o banco de dados...'
	
	# Abrir banco de dados
	imgdb = db.DB()
	imgdb.open(dbname)

	# Criar entrada com valores atualizados
	newRec = {
			'nome':fname,
			'timestamp':timestamp,
			'postid':idpost,
			'titulo':title,
			'keywords':', '.join(keywords).lower(),
			'autor':author,
			'cidade':city,
			'sublocal':sublocation,
			'estado':state,
			'pais':country,
			'taxon':category,
			'direitos':copyright,
			'legenda':caption,
			'spp':spp,
			'tamanho':scale,
			'especialista':source,
			'www':www,
			'mod':mod
			}

	# Gravar entrada atualizada no banco de dados (transformada em string)
	imgdb.put(fname,str(newRec))

	# Fechar banco de dados
	imgdb.close()

	print 'Registro no banco de dados atualizado!'


def searchImgdb():
	'''
	Busca o registro da imagem no banco de dados procurando pelo nome do arquivo.
	
	Se encontrar, compara a data de modificação do arquivo e do registro.

	Se as datas forem iguais pula para a próxima imagem, se forem diferentes atualiza o registro.
	'''

	print 'Verificando se a imagem está no banco de dados...'
	
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

	# Tornando o dic da entrada em variável global
	global recdata

	# Se o registro existir
	if rec:
		print 'Bingo! Registro de %s encontrado.\n' % fname
		# Transformando a entrada do banco em dicionário
		recdata = eval(rec[1])

		print 'Comparando a data de modificação do arquivo com o registro...'
		if recdata['timestamp'] == timestamp:	# Se os timetamps forem iguais
			print
			print '\tBanco de dados\t\t  Arquivo'
			print '\t' + 2 * len(timestamp) * '-' + 4 * '-'
			print '\t%s\t= %s' % (recdata['timestamp'], timestamp)
			print
			if recdata['www'] == True and recdata['mod'] == False:
				print 'Arquivo não mudou!'
				return 0 		# Arquivo não foi modificado, nem precisa ser atualizado
			elif recdata['www'] == True and recdata['mod'] == True:
				print 'Timestamps iguais, mas arquivo modificado. Versão do site não está atualizada!'
				return 1		# Timestamp não foi modificado, mas imagem foi carregada no site ainda
			elif recdata['www'] == False:
				print 'Arquivo não está no site!'
				return 2		# Imagem nunca foi carregado no site
		else:
			print
			print '\tBanco de dados\t\t   Arquivo'
			print '\t' + 2 * len(timestamp) * '-' + 4 * '-'
			print '\t%s\t!= %s' % (recdata['timestamp'], timestamp)
			print
			if recdata['www'] == True:
				print 'Arquivo que está no site não está atualizado!'
				return 1		# Timestamp modificado, imagem do site não está atualizada
			elif recdata['www'] == False:
				print 'Arquivo não está no site!'
				return 2		# Imagem nunca foi carregada no site
	else:
		print 'Registro não encontrado. Esta imagem não está online!'
		print 'Continuando...'

def createMeta():
	'''
	Define as variáveis extraídas dos metadados (IPTC) da imagem.

	Usa a biblioteca do arquivo iptcinfo.py.
	'''

	print 'Lendo os metadados de %s e criando variáveis.' % fname
	
	# Criar objeto com metadados
	info = IPTCInfo(fpath)
	
	# Checando se o arquivo tem dados IPTC
	if len(info.data) < 4:
		raise Exception(info.error)
	
	# Converte valores dos metadados vazios (None) para string em branco
	# FIXME Descobrir o melhor jeito de limpar as variáveis None
#	for k, v in info.data.iteritems():
#		print k, v
#		if v == None or v == []:
#			v = u''
#			info.data[k] = v
#			print info.data[k], v
#		else:
#			pass

	# Definindo as variáveis como globais
	global title
	global keywords
	global author
	global city
	global sublocation
	global state
	global country
	global category
	global copyright
	global caption
	global spp
	global scale
	global source
	global cfields
	global cfieldsDic

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

	# Impedindo que imagens sem título ou autor sejam carregadas no site
	# Escreve no arquivo log com o nome e problema
	if (title == None or title == ''):
		print 'Imagem sem título! Pulando...'
		log.write('%s,Título vazio\n' % fname)
		return False
	elif (author == None or author == ''):
		print 'Imagem sem autor! Pulando...'
		log.write('%s,Autor vazio\n' % fname)
		return False
	else:
		if caption == None:
			caption = ''
		elif sublocation == None:
			sublocation = ''
		elif spp == None:
			spp = ''
		elif source == None:
			source = ''
		
		# Define lista com key/values dos 'custom fields'
		cfields = [
				{'key':'Espécie', 'value': spp},
				{'key':'Táxon', 'value': category},
				{'key':'Local', 'value': sublocation},
				{'key':'Cidade', 'value': city},
				{'key':'Estado', 'value': state},
				{'key':'País', 'value': country},
				{'key':'Autor', 'value': author},
				{'key':'Tamanho','value': scale},
				{'key':'Especialista','value': source}
				]
	
		# Define lista com os nomes dos custom fields
		cfieldsDic = {
				'Espécie' : spp,
				'Táxon' : category,
				'Local' : sublocation,
				'Cidade' : city,
				'Estado' : state,
				'País' : country,
				'Autor' : author,
				'Tamanho' : scale,
				'Especialista' : source
				}
		
		# Imprimindo as variáveis para acompanhamento
		print
		print '\tVariável\tMetadado'
		print '\t' + 40 * '-'
		print '\tTítulo:\t\t%s' % title
		print '\tDescrição:\t%s' % caption
		print '\tEspécie:\t%s' % spp
		print '\tTáxon:\t\t%s' % category
		print '\tTags:\t\t%s' % '\n\t\t\t'.join(keywords)
		print '\tTamanho:\t%s' % scale
		print '\tEspecialista:\t%s' % source
		print '\tAutor:\t\t%s' % author
		print '\tSublocal:\t%s' % sublocation
		print '\tCidade:\t\t%s' % city
		print '\tEstado:\t\t%s' % state
		print '\tPaís:\t\t%s' % country
		print '\tDireitos:\t%s' % copyright


def imgGrab():
	'''
	Busca recursivamente arquivos com extensão .jpg no srcdir
	'''
	
	# Define como variáveis globais
	global n
	global n_new
	global n_up
	global n_to

	global fname

	# Zera contadores
	n = 0
	n_new = 0
	n_up = 0
	n_to = 0

	# Buscador de imagens em ação
	print '\nIniciando o cifonauta!!!'
	for root, dirs, files in os.walk(srcdir):
		for fname in files:
			s = string.find(fname, '.jpg')
			if s >=1 and n < n_max:		# Se encontrar imagem e não tiver atingido o número máximo começar o trabalho
				global fpath
				global timestamp

				# Define o endereço do arquivo
				fpath = os.path.join(root,fname)
				
				# Define a data de modificação do arquivo
				timestamp = time.strftime('%d/%m/%Y %I:%M:%S %p', time.localtime(os.path.getmtime(fpath)))
				
				# Nome do diretório pai do arquivo
				# dirname = os.path.split(root)[1]
				
				# Acrescenta 1 ao número de imagens verificadas
				n += 1
		
				print '\nBuscando imagens na pasta %s...\n' % srcdir
				print '\nEncontrada: %s\t\tn=%d\n' % (fname, n)

				# Procurar arquivo no banco de dados comparando timestamps
				chkFile = searchImgdb()
				# Criar os metadados e retorna falso se está faltando algum obrigatório
				chkMeta = createMeta()
		
				if chkFile == 0:		# Se registro existir e timestamp for igual, www=True e mod=False
					if force_update == True:
						print 'Arquivo não mudou, mas programa rodando com argumento -f. Atualização forçada.'
						wpUpdatePost()
					else:
						print '\nREGISTRO EXISTE E ESTÁ ATUALIZADO NO SITE! PRÓXIMA IMAGEM...'
						pass
				elif chkFile == 1:		# Se imagem do site não estiver atualizada
					if web_upload == True:	# Atualizar se -w tiver sido passado
						print '\nREGISTRO EXISTE, MAS IMAGEM NÃO ESTÁ ATUALIZADA.'
						print 'ARGUMENTO -w, ATUALIZANDO O POST...'
						wpUpdatePost()
					else:			# Caso contrário, apenas atualizar bd
						print '\nREGISTRO EXISTE, IMAGEM DO SITE NÃO ATUALIZADA, MAS APENAS ATUALIZANDO O BANCO DE DADOS...'
						dbPut(True, True, recdata['postid'])
						n_to += 1
					n_up += 1
				elif chkFile == 2:		# Se imagem não estiver no site
					if web_upload == True:
						if chkMeta == False:	# mas estiverem faltando metadados obrigatórios, registrar no log e pular
							print '\nREGISTRO EXISTE, MAS IMAGEM NÃO TEM METADADOS ESSENCIAIS. NÃO SERÁ CARREGADA.'
							dbPut(False, True, 0)
							n_to += 1
							pass
						else:
							print '\nREGISTRO EXISTE, MAS IMAGEM NÃO ESTÁ NO SITE.'
							print 'ARGUMENTO -w, CRIANDO UM NOVO POST...'
							wpPostImg()
							n_new += 1
					else:			# Caso contrário, apenas atualizar bd
						print '\nREGISTRO EXISTE, MAS IMAGEM NÃO ESTÁ NO SITE. APENAS ATUALIZANDO O BANCO DE DADOS...'
						dbPut(False, True, 0)
						n_to += 1
				else:				# Se registro não existir
					if web_upload == True:
						if chkMeta == False:	# mas estiverem faltando metadados obrigatórios, registrar no log e pular
							dbPut(False, True, 0)
							n_to += 1
							pass
						else:		# Do contrário, criar novo post com imagem!
							wpPostImg()
							n_new += 1
					else:			# Se registro não existir registrar no bd:
						dbPut(False, True, 0)
						n_to += 1

#					if only_update == True:	# Se registro não existir, mas programa no modo only-update, passa para a próxima
#						print 'Argumento "-u" utilizado:'
#						print '\t%s não está online, mas não será carregada ao site.' % fname
#						pass

			else:		# Se o número máximo de imagens for atingido, finalizar programa
				print '\n%d fotos analisadas! Execução do CIFONAUTA foi concluída, finalizando...' % n
				break

def busca_gui(app, wid, text):
	del app['table'][:]
	for meta in tabgui:
		if(
				text.lower() in str(meta[4]).lower() or
				text.lower() in str(meta[5]).lower() or
				text.lower() in str(meta[6]).lower() or
				text.lower() in str(meta[7]).lower() or
				text.lower() in str(meta[8]).lower() or
				text.lower() in str(meta[9]).lower() or
				text.lower() in str(meta[11]).lower() or
				text.lower() in str(meta[12]).lower() or
				text.lower() in str(meta[13]).lower()
				):
			app['table'].append(meta)


def usage():
	'''
	Função que imprime a ajuda com modo de uso e argumentos disponíveis
	'''
	print
	print 'Comando básico:'
	print '  python cifonauta.py [args]'
	print
	print 'Argumentos:'
	print '  -h, --help\n\tMostra este menu de ajuda.'
	print
	print '  -n {n}, --n-max {n} (padrão=20)\n\tEspecifica um número máximo de imagens que o programa irá verificar.'
	print
	print '  -i, --single-img\n\tVerifica uma única imagem.'
	print
	print '  -g, --gui-mode\n\tInicia a interface gráfica após verificar as imagens.'
	print
	print '  -w, --web-upload\n\tRoda o programa no modo upload. As imagens serão carregadas para o site.'
	print
	print '  -f, --force-update\n\tRoda o programa fazendo a atualização forçada (leitura, upload para o site e registro no bd) das imagens que não foram modificadas (-w ativado por padrão).'
	print
	print 'Exemplo:'
	print '  python cifonauta.py -f -n 15\n\tFaz a atualização forçada das primeiras 15 imagens que o programa encontrar na pasta padrão (srcdir, especificada dentro do script).'
	print

def main(argv):
	'''
	Função principal do programa. Lê os argumentos se houver e chama as outras funções.
	'''
	# Lista de categorias presentes no site
	global catlist

	global log
	
	# Valores padrão para argumentos
	global force_update
	force_update = False
	global n_max
	n_max = 20
	global web_upload
	web_upload = False
	global gui_mode
	gui_mode = False
	global single_img
	single_img = False

	# Verifica se argumentos foram passados com a execução do programa
	try:
		opts, args = getopt.getopt(argv, 'higwfn:', ['help', 'single-img', 'gui-mode', 'web-upload', 'force-update', 'n='])
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
		elif opt in ('-i', '--single-img'):
			single_img = True
			fname = arg
			print fname
			sys.exit()
		elif opt in ('-g', '--gui-mode'):
			gui_mode = True
		elif opt in ('-w', '--web-upload'):
			web_upload = True
		elif opt in ('-f', '--force-update'):
			force_update = True
			web_upload = True
	
	# Imprime resumo do que o programa vai fazer
	if web_upload == True:
		print '\n%d novas imagens serão verificadas e carregadas, se necessário.\n(argumento "-w" utilizado)\n' % n_max
		# Objeto com lista de categorias
		catlist = []
		for c in getCatList():
			catlist.append(c.name)
	elif force_update == True:
		print '\n%d imagens serão atualizadas de forma forçada.\n(argumento "-f" utilizado)\n' % n_max
	elif gui_mode == True:
		print '\n%d imagens serão verificadas e registradas no banco de dados. A interface gráfica do usuário será iniciada em seguida\n(argumento "-g" utilizado)\n' % n_max
	elif single_img == True:
		print '\nImagem %s será analisada.\n(argumento "-i" utilizado)\n' % fname
	else:
		print '\n%d imagens serão verificadas e registradas no banco de dados.\n' % n_max

	# Cria o arquivo log
	logname = 'log_%s' % time.strftime('%Y.%m.%d_%I:%M:%S', time.localtime())
	log = open(logname, 'a+b')

	# Inicia o cifonauta...
	imgGrab()
	
	# Deletando arquivo log se ele estiver vazio
	if log.read(1024) == '':
		#Fechando a imagem
		log.close()
		# Deletando log vazio
		os.remove(logname)
	else:
		# Fechando arquivo de log
		log.close()
	
	# Abrir e/ou criar arquivo do banco de dados
	imgdb = db.DB()
	imgdb.open(dbname, db.DB_BTREE, db.DB_READ_UNCOMMITTED)
		
	# Abrindo o arquivo texto
	csv = 'lista.csv'
	lista = open(csv, 'w')
	
	print '\nCriando um arquivo final, legível...'

	# Cria lista que gerará a tabela da interface gráfica
	global tabgui
	tabgui = []
	
	# Ativando o cursor
	cursor = imgdb.cursor()
	
	rec = cursor.first()
	
	lista.write('Arquivo|Timestamp|PostID|Autor|Título|Legenda|Keywords|Sublocal|Cidade|Estado|País|Táxon|Espécie|Tamanho|Especialista|Direitos|WWW|MOD\n')
	
	while rec:
		finaldata = eval(rec[1])
		lista.write('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (
			finaldata['nome'],
			finaldata['timestamp'],
			finaldata['postid'],
			finaldata['autor'],
			finaldata['titulo'],
			finaldata['legenda'],
			finaldata['keywords'],
			finaldata['sublocal'],
			finaldata['cidade'],
			finaldata['estado'],
			finaldata['pais'],
			finaldata['taxon'],
			finaldata['spp'],
			finaldata['tamanho'],
			finaldata['especialista'],
			finaldata['direitos'],
			finaldata['www'],
			finaldata['mod']
			))

		tabgui.append([
			finaldata['nome'],
			Image(filename='imagens/thumbs/300px/%s' % finaldata['nome']),
			finaldata['timestamp'],
			finaldata['postid'],
			finaldata['autor'],
			finaldata['titulo'],
			finaldata['legenda'],
			finaldata['keywords'],
			finaldata['sublocal'],
			finaldata['cidade'],
			finaldata['estado'],
			finaldata['pais'],
			finaldata['taxon'],
			finaldata['spp'],
			finaldata['tamanho'],
			finaldata['especialista'],
			finaldata['direitos'],
			finaldata['www'],
			finaldata['mod']
			])

		rec = cursor.next()
			
	# Fechando o cursor
	cursor.close()
	
	#Fechando a imagem
	lista.close()

	# Fechando o banco
	imgdb.close()
	
	print '\nDe %d imagens verificadas, %d atualizadas e %d novas imagens carregadas no site' % (n, n_up, n_new)
	print '%d imagens pendentes' % n_to
	t = int(time.time() - t0)
	if t > 60:
		print '\nTempo de execução:', t / 60, 'min', t % 60, 's'
	else:
		print '\nTempo de execução:', t, 's'
	print

	if gui_mode == True:
		print 'Iniciando a interface do usuário... [BETA]'
		tabfile = open('tablist', 'w')
		tabfile.write(str(tabgui))
		tabfile.close()
		
		app = App(title='Metadados',
				center=(
					Entry(id='search_box', label='Busca:', callback=busca_gui),
					Table('table', 'Tabela de Metadados', tabgui,
						headers=['Arquivo', 'Thumb', 'Timestamp', 'PostID', 'Autor', 'Título', 'Legenda', 'Keywords', 'Sublocal', 'Cidade', 'Estado', 'País', 'Táxon', 'Espécie', 'Tamanho', 'Especialista', 'Direitos', 'WWW', 'MOD'],
						editable=True,
						repositioning=False,
						expand_columns_indexes=None,
						data_changed_callback=data_changed,
						selection_callback=selection_changed
						),
					)
				)
		run()




# Início do programa
if __name__ == '__main__':
	# Marca a hora inicial
	t0 = time.time()

	# Inicia função principal, lendo os argumentos (se houver)
	main(sys.argv[1:])
