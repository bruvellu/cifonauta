#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Cliente que acessa o banco de dados do ITIS (http://www.itis.gov/).

Baseado no nome do táxon ele busca a entrada para descobrir o nome do táxon pai
e o ranking (Reino, Filo, Classe...).
'''

import urllib2
from xml.etree import ElementTree

class Itis:
    '''Interação com o ITIS'''
    def __init__(self, query):
        print 'Iniciando contato com ITIS.'
        self.name = query
        self.tsn = ''
        self.rank = ''
        self.parent = ''
        self.parent_tsn = ''
        self.parent_rank = ''

        self.ranks = ['Kingdom', 'Phylum', 'Class', 'Order',
                'Family', 'Genus', 'Species']

        self.get_tsn(self.name)

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
                'Subfamily': u'Subfamily',
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

    def get_tsn(self, query):
        '''Encontra o identificador do táxon.
        
        Exemplo do XML de input:

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

        http://www.itis.gov/ITISWebService/services/ITISService/searchByScientificName?srchKey=Crustacea
        '''
        xml = self.open_url(
                'http://www.itis.gov/ITISWebService/services/ITISService/searchByScientificName?srchKey=%s'
                    % query, 10)
        if not xml:
            return None
        tree = ElementTree.parse(xml)
        root = tree.getroot()

        matches = []

        print u'Procurando o TSN de %s...' % query

        for results in root.getchildren():
            for children in results.getchildren():
                taxon = None
                tsn = None
                for child in children.getchildren():
                    if child.tag.split('}')[1] == 'unitName1':
                        taxon = child.text
                    if child.tag.split('}')[1] == 'tsn':
                        tsn = child.text
                if taxon == query:
                    print query, tsn
                    matches.append(tsn)
        if matches:
            if len(matches) > 1:
                print u'Mais de um táxon encontrado!'
            else:
                self.tsn = matches[0]
                self.get_parent(matches[0])
        else:
            print u'Nenhum táxon com o nome de %s foi encontrado' % query

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
            xml = self.open_url(
                    'http://www.itis.gov/ITISWebService/services/ITISService/getHierarchyUpFromTSN?tsn=%s'
                    % tsn, 10)
            if not xml:
                return None
            tree = ElementTree.parse(xml)
            root = tree.getroot()

            print u'Pegando o táxon pai...'
            for child in root.getiterator():
                if child.tag.split('}')[1] == 'parentName':
                    parent = child.text
                elif child.tag.split('}')[1] == 'parentTsn':
                    parent_tsn = child.text
                elif child.tag.split('}')[1] == 'rankName':
                    rank = child.text

            if parent and parent_tsn:
                print u'Descobrindo seu ranqueamento...'
                parent_rank = self.get_rank(parent_tsn)
                if parent_rank in self.ranks:
                    print parent + u' é: ' + self.translate(parent_rank)
                    self.rank = self.translate(rank)
                    self.parent_rank = self.translate(parent_rank)
                    self.parent = parent
                    self.parent_tsn = parent_tsn
                else:
                    self.get_parent(parent_tsn)
            else:
                print u'Táxon inválido? Ou sem pai mesmo?'
                self.parent, self.parent_tsn, self.parent_rank = '', '', ''
                self.rank = self.translate(rank)
        else:
            print u'Salvando do loop infinito...'
            pass

    def get_rank(self, tsn):
        '''Retorna o nome do rank do táxon.'''
        xml = self.open_url(
                'http://www.itis.gov/ITISWebService/services/ITISService/getTaxonomicRankNameFromTSN?tsn=%s'
                % tsn, 10)
        if not xml:
            return None
        tree = ElementTree.parse(xml)
        root = tree.getroot()

        for child in root.getiterator():
            if child.tag.split('}')[1] == 'rankName':
                return child.text
        return None

    def open_url(self, url, timeout):
        '''Abre o url e retorna a resposta.'''
        try:
            print 'Conectando ao itis.gov...'
            xml = urllib2.urlopen(url, None, timeout)
        except:
            print 'Acabou o tempo e não houve retorno do ITIS. Nova tentativa:'
            try:
                print 'Conectando ao itis.gov... (2)'
                xml = urllib2.urlopen(url, None, timeout)
            except:
                print 'Acabou o tempo e não houve retorno do ITIS. Nova tentativa:'
                try:
                    print 'Conectando ao itis.gov... (3)'
                    xml = urllib2.urlopen(url, None, 10)
                except:
                    print 'Não houve retorno do ITIS. Desisto.'
                    return None
        print 'Sucesso!'
        return xml

def main():
    pass

# Início do programa
if __name__ == '__main__':
    main()
