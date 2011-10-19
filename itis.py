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

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from meta.models import Taxon

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

        self.search_by_scientific_name(self.query)
        if self.tsn:
            self.get_full_hierarchy(self.tsn)

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
                    if self.fix(entry.combinedName) == query:
                        theone.append(entry)
                if len(theone) == 1:
                    taxon = theone[0]
                    self.name = self.fix(taxon.combinedName)
                    self.tsn = taxon.tsn
                elif len(theone) > 1:
                    # Checa qual destes táxons é válido.
                    taxon = self.get_accepted_names_from_tsn(theone)
                    if taxon:
                        self.name = self.fix(taxon.combinedName)
                        self.tsn = taxon.tsn
                    else:
                        logger.warning('Nenhum táxon com nome %s é válido.', query)
                else:
                    logger.info('Nenhum táxon com o nome exato %s foi encontrado.', query)
            else:
                taxon = results.scientificNames[0]
                self.name = self.fix(taxon.combinedName)
                self.tsn = taxon.tsn
        else:
            logger.info('Nenhum táxon com o nome de %s foi encontrado.', query)

    def fix(self, combinedName):
        '''Fix combinedName from ITIS.'''
        fixed = ' '.join(combinedName.split())
        return fixed

    def get_accepted_names_from_tsn(self, taxa):
        '''Entre táxons com mesmo nome confere qual TSNs é válido.'''
        for taxon in taxa:
            try:
                response = self.client.service.getAcceptedNamesFromTSN(taxon.tsn)
            except:
                logger.warning('Problema na conexão para checar a validade de %d', taxon.tsn)
            # Assume que só existe 1 táxon oficialmente aceito.
            #TODO Verificar isso...
            if not response.acceptedNames:
                # Quando não há nomes alternativos, o táxon é válido.
                return taxon
        else:
            return None

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

        if not hierarchy.hierarchyList:
            self.rank = self.translate(u'Kingdom')
            self.parents = hierarchy.hierarchyList
        else:
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

    def update_model(self):
        '''Update database table with newly fetched records.'''
        if not self.name:
            logger.critical('No taxon is defined! Aborting...')

        # Update parents.
        if self.parents:
            for parent in self.parents:
                logger.debug('Atualizando %s...', parent.taxonName)
                taxon, new = Taxon.objects.get_or_create(name=parent.taxonName)
                taxon.rank = parent.rankName
                taxon.tsn = parent.tsn
                if parent.parentName:
                    taxon.parent = Taxon.objects.get(name=parent.parentName)
                taxon.save()
                logger.debug('%s salvo!', taxon.name)

        # Atualiza o táxon em questão.
        this, new = Taxon.objects.get_or_create(name=self.name)
        this.rank = self.rank
        this.tsn = self.tsn
        if self.parent:
            this.parent = Taxon.objects.get(name=self.parent['name'])
        this.save()

def main():
    pass

# Início do programa
if __name__ == '__main__':
    # Inicia.
    main()
