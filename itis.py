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

from django.conf import settings
from suds.client import Client
from meta.models import Taxon


class Itis:
    '''Interação com o ITIS'''
    def __init__(self, query):
        print('Iniciando contato com ITIS.')

        self.url = 'http://www.itis.gov/ITISWebService/services/ITISService?wsdl'
        try:
            self.client = Client(self.url)
        except:
            print('Não conseguiu conectar o cliente!')

        self.query = query
        self.name = u''
        self.tsn = None
        self.rank = u''
        self.valid = False
        self.parent = {}
        self.parents = []

        # Busca e identifica táxon pelo nome e tsn.
        taxon_data = self.parse_results(self.query)
        #XXX Melhorar isso...
        # Popula dados.
        if taxon_data:
            self.name = taxon_data['name']
            self.tsn = taxon_data['tsn']
            self.valid = taxon_data['valid']

        # Tenta ao menos encontrar o gênero.
        if not self.tsn:
            self.search_genus()
        else:
            # Se tiver encontrado algum TSN.
            # Checa se táxon é válido (XXX necessário?).
            if not self.valid:
                self.valid = self.is_valid(self.tsn)
            if self.valid:
                # Se for válido, pegar hierarquia.
                tree_data = self.parse_hierarchy(self.tsn)
                if tree_data:
                    self.rank = tree_data['rank']
                    self.parent['name'] = tree_data['parent_name']
                    self.parent['tsn'] = tree_data['parent_tsn']
                    self.parents = tree_data['parents']

                    # Traduz para português.
                    for taxon in self.parents:
                        taxon.rankName = self.translate(taxon.rankName)
                        taxon.taxonName = unicode(taxon.taxonName)
                        taxon.tsn = int(taxon.tsn)
                        if taxon.parentName and taxon.parentTsn:
                            taxon.parentName = unicode(taxon.parentName)
                            taxon.parentTsn = int(taxon.parentTsn)

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
                'Infrakingdom': u'Infrareino',
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

    def translate_pt2en(self, rank):
        '''Traduz nome do ranking pro inglês.'''

        pt2en = {
                'Subforma': u'Subform',
                'Superordem': u'Superorder',
                'Variedade': u'Variety',
                'Infraordem': u'Infraorder',
                'Seção': u'Section',
                'Subclasse': u'Subclass',
                'Subseção': u'Subsection',
                'Reino': u'Kingdom',
                'Infrareino': u'Infrakingdom',
                'Divisão': u'Division',
                'Subtribo': u'Subtribe',
                'Aberração': u'Aberration',
                'Infraordem': u'InfraOrder',
                'Subreino': u'Subkingdom',
                'Infraclasse': u'Infraclass',
                'Subfamília': u'Subfamily',
                'Classe': u'Class',
                'Superfamília': u'Superfamily',
                'Subdivisão': u'Subdivision',
                'Morfotipo': u'Morph',
                'Raça': u'Race',
                'Não especificado': u'Unspecified',
                'Subordem': u'Suborder',
                'Gênero': u'Genus',
                'Ordem': u'Order',
                'Subvariedade': u'Subvariety',
                'Tribo': u'Tribe',
                'Subgênero': u'Subgenus',
                'Forma': u'Form',
                'Família': u'Family',
                'Subfilo': u'Subphylum',
                'Estirpe': u'Stirp',
                'Filo': u'Phylum',
                'Superclasse': u'Superclass',
                'Subespécie': u'Subspecies',
                'Espécie': u'Species',
                }

        rank_en = pt2en[rank]

        if rank_en:
            return rank_en
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
        print('Procurando TSN de %s...' % query)

        # Tenta executar a busca usando o query. Caso a conexão falhe, tenta
        # novamente.
        try:
            results = self.client.service.searchByScientificName(query)
        except:
            while attempt < 3:
                print('Não conseguiu conectar... tentativa=%d' % attempt)
                attempt += 1
                self.search_by_scientific_name(query, attempt)
            print('Terminando conexão. Não está rolando.')
            results = None
        return results

    def parse_results(self, query):
        '''Manuseia resultados da busca.'''
        # Objeto que guarda dados e é retornado.
        data = {}

        # Busca no Itis.
        results = self.search_by_scientific_name(query)

        #FIXME Se ele não consegue se conectar no Itis os results vem vazios e
        #dá erro!
        # Le os resultados para encontrar o táxon.
        if results.scientificNames:
            # Se houver mais de 1 resultado, comparar valores.
            if len(results.scientificNames) > 1:
                print('Mais de um táxon encontrado!')
                theone = []
                # Tentando encontrar o táxon certo.
                for entry in results.scientificNames:
                    print(entry.combinedName)
                    if self.fix(entry.combinedName) == query:
                        theone.append(entry)
                if len(theone) == 1:
                    taxon = theone[0]
                    data['name'] = self.fix(taxon.combinedName)
                    data['tsn'] = taxon.tsn
                    data['valid'] = self.is_valid(taxon.tsn)
                    print('Táxon com nome exato encontrado: %s' % data['name'])
                elif len(theone) > 1:
                    # Checa qual destes táxons é válido.
                    for entry in theone:
                        valid = self.is_valid(entry.tsn)
                        # Quando não há nomes alternativos, o táxon é válido.
                        if valid:
                            data['name'] = self.fix(entry.combinedName)
                            data['tsn'] = entry.tsn
                            data['valid'] = True
                            print('Táxon válido encontrado: %s' % data['name'])
                            # Assume que só existe 1 táxon oficialmente aceito.
                            #TODO Verificar isso...
                            break
                    else:
                        print('Nenhum táxon com nome %s é válido.' % query)
                else:
                    print('Nenhum táxon com o nome exato %s foi encontrado.' % query)
                    #TODO busca pelo gênero.
            else:
                taxon = results.scientificNames[0]
                data['name'] = self.fix(taxon.combinedName)
                data['tsn'] = taxon.tsn
                data['valid'] = self.is_valid(taxon.tsn)
        else:
            print('Nenhum táxon com o nome de %s foi encontrado.' % query)
            #TODO busca pelo gênero.
        return data

    def fix(self, combinedName):
        '''Arruma combinedName do ITIS.'''
        fixed = ' '.join(combinedName.split())
        return fixed

    def is_valid(self, tsn):
        '''Checa se táxon é válido e retorna BOOL.'''
        #TODO Retorna o tsn da sinonímia???
        response = self.get_accepted_names_from_tsn(tsn)
        # Quando não há nomes alternativos, o táxon é válido.
        if response.acceptedNames == []:
            return True
        else:
            return False

    def get_accepted_names_from_tsn(self, tsn):
        '''Entre táxons com mesmo nome confere qual TSNs é válido.'''
        try:
            response = self.client.service.getAcceptedNamesFromTSN(tsn)
        except:
            print('Problema na conexão para checar a validade de %d' % tsn)
            response = None
        return response

    def get_full_hierarchy(self, tsn):
        '''Encontra hierarquia e converte valores.

        Usa: http://www.itis.gov/ws_hierApiDescription.html#getFullHierarchy

        O formato vindo do SOAP não serve para criar as instâncias no Django.
        Por isso é necessário converter em unicode e int, além de traduzir os
        rankings.

        Exemplo:
        http://www.itis.gov/ITISWebService/services/ITISService/getFullHierarchyFromTSN?tsn=1378
        '''
        #XXX Garantir que o táxon é válido antes de puxar a hierarquia.
        print('Pegando hierarquia...')

        # Tenta se conectar.
        try:
            hierarchy = self.client.service.getFullHierarchyFromTSN(tsn)
        except:
            print('Erro ao puxar a hierarquia de %s, problema na conexão' % tsn)
            hierarchy = None
        return hierarchy

    def parse_hierarchy(self, tsn):
        '''Le e retorna hierarquia.'''
        # Data.
        data = {}

        # Pega hierarquia.
        hierarchy = self.get_full_hierarchy(tsn)

        # Processa.
        if not hierarchy.hierarchyList:
            # Hierarquia vazia só é Reino para táxons válidos.
            # Apenas busca hierarquia de táxons válidos.
            data['rank'] = self.translate(u'Kingdom')
            data['parents'] = hierarchy.hierarchyList
        else:
            # Define new sliced tree without children.
            tree_up = []
            # Remove children from tree.
            for node in hierarchy.hierarchyList:
                tree_up.append(node)
                if node.tsn == tsn:
                    break
            # Último ítem é o táxon em questão.
            taxon = tree_up.pop()
            # Salva propriedades.
            data['rank'] = self.translate(taxon.rankName)
            data['parent_name'] = unicode(taxon.parentName)
            data['parent_tsn'] = int(taxon.parentTsn)
            data['parents'] = tree_up
        return data

    def search_genus(self):
        '''Search ITIS for the genus, if possible.'''
        split_query = self.query.split()
        if len(split_query) > 1:
            pseudo_genus = split_query[0]
            genus_data = self.parse_results(pseudo_genus)
            if genus_data['valid']:
                self.name = self.query
                self.rank = u'Espécie'
                self.parent['name'] = genus_data['name']
                self.parent['tsn'] = genus_data['tsn']
                tree_data = self.parse_hierarchy(genus_data['tsn'])
                self.parents = tree_data['parents']

    def update_model(self, taxon):
        '''Update database table with newly fetched records.'''
        if not self.name:
            print('No taxon is defined! Aborting...')

        #XXX Melhor se perguntar se o táxon é válido, ou não?

        # Update parents.
        if self.parents:
            for parent in self.parents:
                print('Atualizando %s...' % parent.taxonName)
                above, new = Taxon.objects.get_or_create(name=parent.taxonName)
                above.rank = parent.rankName
                above.tsn = parent.tsn
                if parent.parentName:
                    above.parent = Taxon.objects.get(name=parent.parentName)
                above.save()
                print('%s salvo!' % above.name)

        # Atualiza o táxon em questão.
        print('Atualizando %s...' % self.name)
        taxon.rank = self.rank
        taxon.tsn = self.tsn
        if self.parent:
            taxon.parent = Taxon.objects.get(name=self.parent['name'])
        taxon.save()
        print('%s salvo!' % self.name)
        return taxon


def main():
    pass

# Início do programa
if __name__ == '__main__':
    # Inicia.
    main()
