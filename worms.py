#!/usr/bin/env python

'''Client to access the web services of the WoRMS database (http://www.marinespecies.org/).

For a full description refer to: http://marinespecies.org/aphia.php?p=soap

Usage:

    from worms import Aphia
    aphia = Aphia()
    results = aphia.get_aphia_records('Priapulus caudatus')
    print(results)

Services:

    [y] getAphiaID
    [y] getAphiaRecords
    [y] getAphiaNameByID
    [y] getAphiaRecordByID
    [ ] getAphiaRecordsByIDs
    [y] getAphiaRecordByExtID
    [y] getExtIDbyAphiaID
    [y] getAphiaRecordsByNames
    [y] getAphiaRecordsByVernacular
    [y] getAphiaRecordsByDate
    [y] getAphiaClassificationByID
    [y] getSourcesByAphiaID
    [y] getAphiaSynonymsByID
    [y] getAphiaVernacularsByID
    [y] getAphiaChildrenByID
    [y] matchAphiaRecordsByNames
    [y] getAphiaDistributionsByID
    [ ] getAphiaTaxonRanksByID
    [ ] getAphiaTaxonRanksByName
    [ ] getAphiaRecordsByTaxonRankID
    [ ] getAphiaAttributeKeysByID
    [ ] getAphiaAttributeValuesByCategoryID
    [ ] getAphiaIDsByAttributeKeyID
    [ ] getAphiaAttributesByAphiaID

'''

# TODO: Migrate to REST
# TODO: Allow passing additional arguments

from suds import null, WebFault
from suds.client import Client
import logging

# Create logger.
logger = logging.getLogger('worms')
logger.setLevel(logging.DEBUG)
logger.propagate = False
formatter = logging.Formatter('[%(levelname)s] %(asctime)s @ %(module)s %(funcName)s (l%(lineno)d): %(message)s')

# Console handler for logger.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class Aphia:
    '''WoRMS interactor.'''
    def __init__(self):
        self.url = 'http://www.marinespecies.org/aphia.php?p=soap&wsdl=1'
        logger.info('Initiating contact with WoRMS...')
        try:
            self.client = Client(self.url)
            logger.info('Connected to WoRMS web services.')
        except:
            print('Could not connect to client!')

    def wire(self, service, query, attempt=0):
        '''Manage re-connections between client and WoRMS.'''
        try:
            results = service(query)
        except:
            while attempt < 3:
                logger.warning('Could not connect... try=%d' % attempt)
                attempt += 1
                self.wire(service, query, attempt)
            logger.critical('Closing up the connection. I failed.')
            results = None
        return results

    def get_aphia_id(self, query):
        '''Get the AphiaID for a given name.'''
        logger.info('Searching for the name "%s"', query)
        results = self.wire(self.client.service.getAphiaID, query)
        return results

    def get_aphia_records(self, query):
        '''Get one or more matching AphiaRecords for a given name.'''
        logger.info('Searching for the name "%s"', query)
        results = self.wire(self.client.service.getAphiaRecords, query)
        self.show_results(results)
        return results

    def get_aphia_name_by_id(self, query):
        '''Get the correct name for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaNameByID, query)
        return results

    def get_aphia_record_by_id(self, query):
        '''Get the complete AphiaRecord for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaRecordByID, query)
        return results

    def get_aphia_record_by_external_id(self, query, dbtype=''):
        '''Get the Aphia Record for a given external identifier.'''
        #TODO define type parameter.
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaRecordByExtID, query)
        return results

    def get_external_id_by_aphia_id(self, query):
        '''Get any external identifier(s) for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getExtIDbyAphiaID, query)
        return results

    def get_aphia_records_by_names(self, query):
        '''For each given scientific name, try to find one or more AphiaRecords.

        This allows you to match multiple names in one call. Limited to 500
        names at once for performance reasons.
        '''
        logger.info('Searching for the name(s) "%s"', query)
        results = self.wire(self.client.service.getAphiaRecordsByNames, query)
        return results

    def get_aphia_records_by_vernacular(self, query):
        '''Get one or more Aphia Records for a given vernacular.'''
        logger.info('Searching for the name "%s"', query)
        results = self.wire(self.client.service.getAphiaRecordsByVernacular, query)
        return results

    def get_aphia_records_by_date(self, query):
        '''Lists all AphiaRecords (taxa) modified or added between a specific time interval.'''
        #TODO Define startdate parameters.
        logger.info('Searching between dates "%s"', query)
        results = self.wire(self.client.service.getAphiaRecordsByDate, query)
        return results

    def get_aphia_classification_by_id(self, query):
        '''Get the complete classification for one taxon.

        This also includes any sub or super ranks.
        '''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaClassificationByID, query)
        return results

    def get_sources_by_aphia_id(self, query):
        '''Get one or more sources/references including links, for one AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getSourcesByAphiaID, query)
        return results

    def get_aphia_synonyms_by_id(self, query):
        '''Get all synonyms for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaSynonymsByID, query)
        return results

    def get_aphia_vernaculars_by_id(self, query):
        '''Get all vernaculars for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaVernacularsByID, query)
        return results

    def get_aphia_children_by_id(self, query):
        '''Get the direct children for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaChildrenByID, query)
        return results

    def match_aphia_records_by_names(self, query):
        '''For each given scientific name (may include authority), try to find one or more AphiaRecords, using the TAXAMATCH fuzzy matching algorithm by Tony Rees.

        This allows you to (fuzzy) match multiple names in one call. Limited to
        50 names at once for performance reasons.
        '''
        logger.info('Searching for the name(s) "%s"', query)
        results = self.wire(self.client.service.matchAphiaRecordsByNames, query)
        return results

    def get_aphia_distributions_by_id(self, query):
        '''Get all distributions for a given AphiaID.'''
        logger.info('Searching for the ID "%s"', query)
        results = self.wire(self.client.service.getAphiaDistributionsByID, query)
        return results

    def show_results(self, results):
        '''Print relevant information about the results.'''
        if results:
            logger.info('Found {} record(s)'.format(len(results)))
            for result in results:
                self.print_record(result)
        else:
            logger.info('Found no records.')

    def print_record(self, record, pre=''):
        '''Print taxon information.'''
        # logger.info('ID: {0}, Name: {1}, Authority: {2}, Rank: {3}, Status: {4}'.format(
        logger.info('{0}{1} / {2} / {3} / {4} / {5}'.format(
            pre,
            record['AphiaID'],
            record['scientificname'],
            record['authority'],
            record['rank'],
            record['status'])
            )

if __name__ == '__main__':
    print('Command line not implemented yet.')
