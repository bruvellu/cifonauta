#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Cliente que acessa o banco de dados do ITIS (http://www.itis.gov/).

Baseado no nome do táxon ele busca a entrada para descobrir o nome do táxon pai
e o ranking (Reino, Filo, Classe...).

Algoritmo:
    - Abre URL através da API do ITIS e salva o XML, se houver (get_tsn)
    - Usa ElementTree pra parse o XML a partir da raiz
    - Busca as tags "unitName1" e "tsn" e salva em lista
    - Se houver mais de 1 ou nenhum emitir aviso
    - Do contrário, procurar pai do primeiro elemento (get_parent)
    - Usa novamente API do ITIS para buscar pai pelo TSN
    - Se existir, descobrir seu ranqueamento e se é icônico (get_rank)
    - Caso não seja, buscar pelo pai do pai (get_parent) até primeira categoria icônica
    - Achado o táxon é necessário traduzir (translate) e salvar no objeto
'''

from suds.client import Client
import logging

# Criando o logger.
logger = logging.getLogger('itis')
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
file_handler = logging.FileHandler('logs/itis.log')
file_handler.setLevel(logging.DEBUG)
# Define a formatação para o arquivo.log.
file_handler.setFormatter(formatter)
# Adiciona o arquivo.log para o logger.
logger.addHandler(file_handler)


class Itis:
    '''Interação com o ITIS'''
    def __init__(self, query):
        print 'Iniciando contato com ITIS.'

        self.url = 'http://www.itis.gov/ITISWebService.xml'
        try:
            self.client = Client(self.url)
        except:
            print u'Não conseguiu conectar o cliente!'

        self.query = query
        self.name = None #TODO Definir nome.
        self.tsn = None
        self.rank = None
        self.parent = {}
        self.parents = None
        self.hierarchy = None

        self.ranks = ['Kingdom', 'Phylum', 'Class', 'Order',
                'Family', 'Genus', 'Species']

        self.search_by_scientific_name(self.query)
        if self.tsn:
            self.hierarchy = self.get_full_hierarchy(self.tsn)

    def translate(self, rank):
        '''Traduz nome do ranking pra português.'''

        en2pt = {
                'Subform': u'Subforma',
                'Superorder': u'Superordem',
                'Variety': u'Variedade',
                'Infraorder': u'Infraordem',
                'Section': u'Seção',
                'Subclass': u'Subclasse',
                'Subsection': u'Subseção',
                'Kingdom': u'Reino',
                'Division': u'Divisão',
                'Subtribe': u'Subtribo',
                'Aberration': u'Aberração',
                'InfraOrder': u'Infraordem',
                'Subkingdom': u'Subreino',
                'Infraclass': u'Infraclasse',
                'Subfamily': u'Subfamília',
                'Class': u'Classe',
                'Superfamily': u'Superfamília',
                'Subdivision': u'Subdivisão',
                'Morph': u'Morfotipo',
                'Race': u'Raça',
                'Unspecified': u'Não especificado',
                'Suborder': u'Subordem',
                'Genus': u'Gênero',
                'Order': u'Ordem',
                'Subvariety': u'Subvariedade',
                'Tribe': u'Tribo',
                'Subgenus': u'Subgênero',
                'Form': u'Forma',
                'Family': u'Família',
                'Subphylum': u'Subfilo',
                'Stirp': u'Estirpe',
                'Phylum': u'Filo',
                'Superclass': u'Superclasse',
                'Subspecies': u'Subespécie',
                'Species': u'Espécie',
                }

        rank_pt = en2pt[rank]

        if rank_pt:
            return rank_pt
        else:
            return rank

    def search_by_scientific_name(self, query, attempt=0):
        '''Busca nome científico no ITIS.

        Função é um wrapper para searchByScientificName method:
        http://www.itis.gov/ws_searchApiDescription.html#SrchBySciName

        Exemplo do XML para a busca "Crustacea":

        http://www.itis.gov/ITISWebService/services/ITISService/searchByScientificName?srchKey=Crustacea

        <ns:searchByScientificNameResponse>
            <ns:return type="org.usgs.itis.itis_service.data.SvcScientificNameList">
                <ax23:scientificNames type="org.usgs.itis.itis_service.data.SvcScientificName">
                    <ax23:combinedName>Crustacea</ax23:combinedName>
                    <ax23:unitInd1/>
                    <ax23:unitInd2/>
                    <ax23:unitInd3/>
                    <ax23:unitInd4/>
                    <ax23:unitName1>Crustacea</ax23:unitName1>
                    <ax23:unitName2/>
                    <ax23:unitName3/>
                    <ax23:unitName4/>
                    <ax23:tsn>83677</ax23:tsn>
                </ax23:scientificNames>

                <ax23:scientificNames type="org.usgs.itis.itis_service.data.SvcScientificName">
                    <ax23:combinedName>Schizoporella crustacea</ax23:combinedName>
                    <ax23:unitInd1/>
                    <ax23:unitInd2/>
                    <ax23:unitInd3/>
                    <ax23:unitInd4/>
                    <ax23:unitName1>Schizoporella</ax23:unitName1>
                    <ax23:unitName2>crustacea</ax23:unitName2>
                    <ax23:unitName3/>
                    <ax23:unitName4/>
                    <ax23:tsn>156303</ax23:tsn>
                </ax23:scientificNames>
            </ns:return>
        </ns:searchByScientificNameResponse>

        '''
        logger.info('Procurando TSN de %s...', query)

        # Tenta executar a busca usando o query. Caso a conexão falhe, tenta 
        # novamente.
        try:
            results = self.client.service.searchByScientificName(query)
        except:
            while attempt < 3:
                logger.warning('Não conseguiu conectar... tentativa=%d' % attempt)
                attempt += 1
                self.search_by_scientific_name(query, attempt)
            logger.critical('Terminando conexão. Não está rolando.')
            results = None

        # Le os resultados para encontrar o táxon.
        if results.scientificNames:
            # Se houver mais de 1 resultado, comparar valores.
            if len(results.scientificNames) > 1:
                logger.debug('Mais de um táxon encontrado!')
                theone = []
                # Tentando encontrar o táxon certo.
                for entry in results.scientificNames:
                    if entry.combinedName == query:
                        theone.append(entry)
                if len(theone) == 1:
                    taxon = theone[0]
                    self.name = taxon.combinedName
                    self.tsn = taxon.tsn
                else:
                    #XXX Pensar em algo.
                    logger.critical('Mais de uma entrada com o nome de %s. O que fazer?',
                            query)
            else:
                taxon = results.scientificNames[0]
                self.name = taxon.combinedName
                self.tsn = taxon.tsn
        else:
            logger.info('Nenhum táxon com o nome de %s foi encontrado.', query)

    def get_full_hierarchy(self, tsn):
        '''Encontra hierarquia e converte valores.

        Usa: http://www.itis.gov/ws_hierApiDescription.html#getFullHierarchy

        O formato vindo do SOAP não serve para criar as instâncias no Django.
        Por isso é necessário converter em unicode e int, além de traduzir os
        rankings.

        Exemplo:
        http://www.itis.gov/ITISWebService/services/ITISService/getFullHierarchyFromTSN?tsn=1378
        '''
        logger.info('Pegando hierarquia...')

        # Tenta se conectar.
        try:
            hierarchy = self.client.service.getFullHierarchyFromTSN(tsn)
        except:
            logger.warning('Erro ao puxar a hierarquia de %s, problema na conexão', tsn)

        try:
            # Último ítem é o táxon em questão.
            taxon = hierarchy.hierarchyList[-1]
            # Salva propriedades.
            self.rank = self.translate(taxon.rankName)
            self.parent['name'] = unicode(taxon.parentName)
            self.parent['tsn'] = int(taxon.parentTsn)
            self.parents = hierarchy.hierarchyList
            # Remove o último item, referente ao próprio táxon.
            # Deixa somente os parents mesmo.
            self.parents.pop()

            # Traduz para português.
            for taxon in self.parents:
                taxon.rankName = self.translate(taxon.rankName)
                taxon.taxonName = unicode(taxon.taxonName)
                taxon.tsn = int(taxon.tsn)
                if taxon.parentName and taxon.parentTsn:
                    taxon.parentName = unicode(taxon.parentName)
                    taxon.parentTsn = int(taxon.parentTsn)
        except:
            logger.debug('Táxon não retornou classificação completa...')

    def get_parent(self, tsn):
        '''Encontra o táxon pai.

        Exemplo do XML de input:

        <ns:getHierarchyUpFromTSNResponse>
            <ns:return type="org.usgs.itis.itis_service.data.SvcHierarchyRecord">
                <ax23:parentName>Arthropoda</ax23:parentName>
                <ax23:parentTsn>82696</ax23:parentTsn>
                <ax23:rankName>Subphylum</ax23:rankName>
                <ax23:taxonName>Crustacea</ax23:taxonName>
                <ax23:tsn>83677</ax23:tsn>
            </ns:return>
        </ns:getHierarchyUpFromTSNResponse>

        http://www.itis.gov/ITISWebService/services/ITISService/getHierarchyUpFromTSN?tsn=83677 
        '''
        if tsn:
            print u'Pegando o táxon pai...'
            try:
                up = self.client.service.getHierarchyUpFromTSN(tsn)
            except:
                #TODO O que fazer quando isso acontecer?
                print u'Não conseguiu conectar...'
                up = None
            if up.parentName and up.parentTsn:
                self.rank = self.translate(up.rankName)
                self.parent_rank = self.translate(
                        self.get_rank(up.parentTsn)
                        )
                self.parent = up.parentName
                self.parent_tsn = up.parentTsn
            else:
                print u'Táxon inválido? Ou sem pai mesmo?'
                #FIXME None evita táxon pai em branco?
                #FIXME E táxon inválido?
                self.parent, self.parent_tsn, self.parent_rank = None, None, None
                self.rank = self.translate(up.rankName)
        else:
            print u'Salvando do loop infinito...'
            pass

    def get_rank(self, tsn):
        '''Retorna o nome do rank do táxon.'''
        try:
            rank = self.client.service.getTaxonomicRankNameFromTSN(tsn)
            return rank.rankName
        except:
            #TODO O que fazer quando isso acontecer?
            print u'Não conseguiu conectar...'
            return None

    def open_service(self, function, value):
        '''Abre o url e retorna a resposta.'''
        try:
            print 'Conectando ao itis.gov...'
            query = eval('self.client.service.%s(%s)' % (function, value))
        except:
            print 'Acabou o tempo e não houve retorno do ITIS. Nova tentativa:'
            try:
                print 'Conectando ao itis.gov... (2)'
                query = eval('self.client.service.%s(%s)' % (function, value))
            except:
                print 'Acabou o tempo e não houve retorno do ITIS. Nova tentativa:'
                try:
                    print 'Conectando ao itis.gov... (3)'
                    query = eval('self.client.service.%s(%s)' % (function, value))
                except:
                    print 'Não houve retorno do ITIS. Desisto.'
                    return None
        print 'Sucesso!'
        return query

def main():
    pass

# Início do programa
if __name__ == '__main__':
    # Inicia.
    main()
