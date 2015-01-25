from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video
from optparse import make_option
from datetime import datetime
from iptcinfo import IPTCInfo
from media_utils import check_file, dir_ready, get_exif, get_date, get_gps
from meta.models import *
import os
import pickle
import time


class Command(BaseCommand):
    args = ''
    help = 'Main function of the Cifonauta database organizer.'

    option_list = BaseCommand.option_list + (
            make_option('-n', '--number', action='store', type='int',
                        dest='number', default=20000,
                        help='Number of files to scan.'),
            make_option('-p', '--only-photos', action='store_true',
                        dest='photos', default=False,
                        help='Only scan photos.'),
            make_option('-m', '--only-movies', action='store_true',
                        dest='videos', default=False,
                        help='Only scan videos.'),
            )

    SITE_MEDIA = 'site_media'
    SITE_MEDIA_PHOTOS = 'site_media/photos'
    SITE_MEDIA_VIDEOS = 'site_media/videos'

    def handle(self, *args, **options):
        '''Command execution trunk.'''
        # Stats.
        t0 = time.time()
        n = 0
        n_new = 0
        n_updated = 0

        # Some variables.
        n_max = options['number']
        only_photos = options['photos']
        only_videos = options['videos']

        # Initiate database instance.
        cbm = Database()

        # Choose which filetype.
        if only_photos:
            photo_folder = Folder(self.SITE_MEDIA_PHOTOS, n_max)
            photo_filepaths = photo_folder.get_files()
            video_filepaths = []
        elif only_videos:
            video_folder = Folder(self.SITE_MEDIA_VIDEOS, n_max)
            video_filepaths = video_folder.get_files()
            photo_filepaths = []
        else:
            # Do photos first.
            photo_folder = Folder(self.SITE_MEDIA_PHOTOS, n_max)
            photo_filepaths = photo_folder.get_files()
            # Do videos last.
            video_folder = Folder(self.SITE_MEDIA_VIDEOS, n_max)
            video_filepaths = video_folder.get_files()

        # Process photos.
        for path in photo_filepaths:
            photo = Photo(path)
            # Search photo in database.
            query = cbm.search_db(photo)
            if not query:
                print('NEW FILE: %s.' % photo.filename)
                photo.create_meta()
                cbm.update_db(photo)
                n_new += 1
            else:
                if query == 2:
                    # Entry exists and timestamp has not changed.
                    print('ENTRY UP-TO-DATE! NEXT...')
                    continue
                else:
                    # Timestamps differ.
                    print('UPDATING ENTRY...')
                    photo.create_meta()
                    cbm.update_db(photo, update=True)
                    n_updated += 1
        n = len(photo_filepaths)

        print(photo_filepaths)
        print(video_filepaths)

        self.stdout.write('%d unique names. -p:%s, -m:%s' % (options['number'],
                                                             options['photos'],
                                                             options['videos']))

        # Statistics.
        print('\n%d ANALYZED FILES' % n)
        print('%d new' % n_new)
        print('%d updated' % n_updated)
        t = int(time.time() - t0)
        if t > 60:
            print('\nRunning time: ' + str(t / 60) + ' min ' + str(t % 60) + ' s')
        else:
            print('\nRunning time: ' + str(t) + ' s')
        print('\n%d analyzed, %d new, %d updated' % (n, n_new, n_updated))

class Database:
    '''Database object.'''
    def __init__(self):
        pass

    def search_db(self, media):
        '''Query database for filename.

        Compare timestamps, if equal, skip, if different, update.
        '''
        print('Searching %s...' % media.filepath)
        photopath = 'photos/'
        videopath = 'videos/'

        # Query for the exact filename to avoid confusion.
        try:
            if media.type == 'photo':
                record = Image.objects.get(filename=media.filename)
            elif media.type == 'video':
                record = Video.objects.get(filename=media.filename)
            print('Bingo! Found %s.' % media.filename)
            print('Comparing timestamp between file and db...')
            # XXX Dirty hack to make naive timestamp.
            record.timestamp = record.timestamp.replace(tzinfo=None)
            if record.timestamp != media.timestamp:
                print('%s != %s' % (record.timestamp, media.timestamp))
                print('File has changed! Return 1')
                return 1
            else:
                print('File has not changed! Return 2')
                return 2
        except Image.DoesNotExist:
            print('Entry not found.')
            return False

    def update_db(self, media, update=False):
        '''Creates or updates database entry.'''
        print('Updating database...')
        # Instantiate metadata for processing.
        media_meta = media.metadata.dictionary

        #FIXME authors are not lists and this is not working with the save sets.
        # Taxonomic information.
        taxa = media_meta['taxon']
        del media_meta['taxon']

        # Prevent deprecated field to show up.
        try:
            del media_meta['genus_sp']
        except:
            pass

        # Authors.
        authors = media_meta['author']

        # Sources.
        sources = media_meta['source']
        del media_meta['source']

        # Tags.
        tags = media_meta['tags']
        del media_meta['tags']

        # References.
        refs = media_meta['references']
        del media_meta['references']

        # Keep media with incomplete metadata private.
        if media_meta['title'] == '' or not media_meta['author']:
            print('Media %s has no title or author!' % media_meta['source_filepath'])
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Delete key to insert authors separately.
        del media_meta['author']

        # Transform values in model instances.
        toget = ['size', 'rights', 'sublocation',
                'city', 'state', 'country']
        for k in toget:
            print('META (%s): %s' % (k, media_meta[k]))
            # Create only if not blank.
            if media_meta[k]:
                media_meta[k] = self.get_instance(k, media_meta[k])
                print('INSTANCES FOUND: %s' % media_meta[k])
            else:
                del media_meta[k]

        if not update:
            if media.type == 'photo':
                entry = Image(**media_meta)
            elif media.type == 'video':
                entry = Video(**media_meta)
            # Saving is needed to create an ID, necessary for saving remaining metadata.
            entry.save()
        else:
            if media.type == 'photo':
                entry = Image.objects.get(filename=media.filename)
            elif media.type == 'video':
                entry = Video.objects.get(filename=media.filename.split('.')[0])
            for k, v in media_meta.iteritems():
                setattr(entry, k, v)

        # Update authors.
        entry = self.update_sets(entry, 'author', authors)

        # Update sources.
        entry = self.update_sets(entry, 'source', sources)

        # Update taxa.
        entry = self.update_sets(entry, 'taxon', taxa)

        # Update tags.
        entry = self.update_sets(entry, 'tag', tags)

        # Update references.
        entry = self.update_sets(entry, 'reference', refs)

        # Saving modifications.
        entry.save()

        print('Database entry updated!')

    def get_instance(self, table, value):
        '''Returns ID from name.'''
        print('\nGET table: %s, value: %s' % (table, value))

        # Needs a default in case objects exists.
        new = False

        # Try to get object. If it doesn't exist, confirm to avoid bad metadata.
        try:
            model = eval('%s.objects.get(name="%s")' % (table.capitalize(), value))
        except:
            # Load bad data dictionary.
            bad_data_file = open('bad_data.pkl', 'rb')
            bad_data = pickle.load(bad_data_file)
            bad_data_file.close()
            try:
                fixed_value = bad_data[value]
                print('"%s" automatically fixed to "%s"' % (value, bad_data[value]))
            except:
                fixed_value = raw_input('\nNew metadata. Type to confirm: ')
                fixed_value = unicode(fixed_value, 'utf-8')
            try:
                model, new = eval('%s.objects.get_or_create(name="%s")' % (table.capitalize(), fixed_value))
                if new:
                    print('New metadata %s created!' % fixed_value)
                else:
                    print('Metadata %s already existed!' % fixed_value)
                    # Add to bad data dictionary.
                    bad_data[value] = fixed_value
                    bad_data_file = open('bad_data.pkl', 'wb')
                    pickle.dump(bad_data, bad_data_file)
                    bad_data_file.close()
                # TODO Fix metadata field on original image!!!
            except:
                print('Object %s not found! Aborting...' % fixed_value)

        # Check ITIS for taxonomic info.
        if table == 'taxon' and new:
            taxon = self.get_itis(value)
            # Retry if connection fails.
            if not taxon:
                taxon = self.get_itis(value)
                if not taxon:
                    print('New try in 5s...')
                    time.sleep(5)
                    taxon = self.get_itis(value)
            try:
                # Update model.
                model = taxon.update_model(model)
            except:
                print('Could not get taxonomic hierarchy...')
        return model

    def update_sets(self, entry, field, meta):
        '''Update many to many database fields.

        Verifies if value is blank.
        '''
        print('META (%s): %s' % (field, meta))
        meta_instances = [self.get_instance(field, value) for value in meta if value.strip()]
        print('INSTANCES FOUND: %s' % meta_instances)
        eval('entry.%s_set.clear()' % field)
        [eval('entry.%s_set.add(value)' % field) for value in meta_instances if meta_instances]
        return entry

    def get_itis(self, name):
        '''Access ITIS database.

        Extract parent taxon and ranking.

        taxon.name
        taxon.rank
        taxon.tsn
        taxon.parents
        taxon.parent['name']
        taxon.parent['tsn']
        '''
        try:
            taxon = Itis(name)
        except:
            return None
        return taxon


class Folder:
    '''Take care of directories and its files.

    >>> dir = 'source_media'
    >>> folder = Folder(dir, 100)
    >>> os.path.isdir(folder.folder_path)
    True
    >>> filepaths = folder.get_files()
    >>> isinstance(filepaths, list)
    True
    '''
    def __init__(self, folder, n_max):
        self.folder_path = folder
        self.n_max = n_max
        self.files = []
        print('Pasta a ser analisada: %s' % self.folder_path)

    def get_files(self):
        '''Search .jpg files recursively in a directory.

        Since photos and videos have a .jpg version created before this script only identifies the .jpg files.
        Returns a list of filepaths.
        '''
        n = 0
        EXTENSION = ('.jpg')

        # File searcher.
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                if filepath.lower().endswith(EXTENSION) and n < self.n_max:
                    self.files.append(filepath)
                    n += 1
                    continue
            else:
                continue
        else:
            print('%d files found.' % n)

        return self.files


class Meta:
    '''Metadata object'''
    def __init__(self, media):
        '''Initialize metadata.'''

        print('Parsing %s metadata.' % media.filename)

        if media.type == 'photo':
            self.photo_init(media)
        elif media.type == 'video':
            self.video_init(media)

        # Prepare some fields for the database.
        self.prepare_meta()

        # Make dictionary.
        self.build_dictionary()

    def photo_init(self, media):
        'Initialize photo metadata.'
        # Create metadata object.
        info = IPTCInfo(media.filepath, True, 'utf-8')
        # Check if file has IPTC data.
        if len(info.data) < 4:
            print('%s has no IPTC data!' % media.filename)

        # Define metadata.
        self.filename = media.filename
        self.filepath = os.path.relpath(media.filepath, 'site_media')
        self.title = info.data['object name']                      #5
        self.tags = info.data['keywords']                          #25
        self.author = info.data['by-line']                         #80
        self.city = info.data['city']                              #90
        self.sublocation = info.data['sub-location']               #92
        self.state = info.data['province/state']                   #95
        self.country = info.data['country/primary location name']  #101
        self.taxon = info.data['headline']                        #105
        self.rights = info.data['copyright notice']                #116
        self.caption = info.data['caption/abstract']               #120
        self.size = info.data['special instructions']              #40
        self.source = info.data['source']                          #115
        self.references = info.data['credit']                      #110
        self.timestamp = media.timestamp
        self.notes = u''

    def none_to_empty(self, metadata):
        '''Convert None to empty string.'''
        if metadata is None:
            return u''
        else:
            return metadata

    def prepare_meta(self):
        '''Cleanup metadata for database input.'''
        # Convert None to empty string.
        self.title = self.none_to_empty(self.title)
        self.tags = self.none_to_empty(self.tags)
        self.author = self.none_to_empty(self.author)
        self.city = self.none_to_empty(self.city)
        self.sublocation = self.none_to_empty(self.sublocation)
        self.state = self.none_to_empty(self.state)
        self.country = self.none_to_empty(self.country)
        self.taxon = self.none_to_empty(self.taxon)
        self.rights = self.none_to_empty(self.rights)
        self.caption = self.none_to_empty(self.caption)
        self.size = self.none_to_empty(self.size)
        self.source = self.none_to_empty(self.source)
        self.references = self.none_to_empty(self.references)

        #FIXME Check if tags are bundled in a list.
        #if not isinstance(meta['tags'], list):

        # Transform to list.
        self.author = [a.strip() for a in self.author.split(',')]
        self.source = [a.strip() for a in self.source.split(',')]
        self.references = [a.strip() for a in self.references.split(',')]

        #XXX Take care of aff. and species with 3 names?
        #meta['taxon'] = [a.strip() for a in meta['taxon'].split(',')]
        temp_taxa = [a.strip() for a in self.taxon.split(',')]
        clean_taxa = []
        for taxon in temp_taxa:
            tsplit = taxon.split()
            if len(tsplit) == 2 and tsplit[-1] in ['sp', 'sp.', 'spp']:
                tsplit.pop()
                clean_taxa.append(tsplit[0])
            else:
                clean_taxa.append(taxon)
        self.taxon = clean_taxa

    def build_dictionary(self):
        '''Generates dictionary for canonical database processing.'''

        self.dictionary = {
            'filename': self.filename,
            'filepath': self.filepath,
            'title': self.title,
            'tags': self.tags,
            'author': self.author,
            'city': self.city,
            'sublocation': self.sublocation,
            'state': self.state,
            'country': self.country,
            'taxon': self.taxon,
            'rights': self.rights,
            'caption': self.caption,
            'size': self.size,
            'source': self.source,
            'references': self.references,
            'timestamp': self.timestamp,
            'notes': self.notes,
            }


class Photo:
    '''Photo object.'''
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.timestamp = datetime.fromtimestamp(
                os.path.getmtime(self.filepath))
        self.type = 'photo'

    def create_meta(self):
        '''Parse and instantiate photo metadata.

        Uses iptcinfo.py and pyexiv2 libraries for IPTC and EXIF.
        '''
        self.metadata = Meta(self)

        # Extracting EXIF metadata.
        exif = get_exif(self.filepath)
        # Extracting data.
        self.metadata.date = get_date(exif)
        self.metadata.dictionary['date'] = self.metadata.date
        # Extracting geolocation.
        self.metadata.gps = get_gps(exif)
        self.metadata.dictionary['geolocation'] = self.metadata.gps['geolocation']
        self.metadata.dictionary['latitude'] = self.metadata.gps['latitude']
        self.metadata.dictionary['longitude'] = self.metadata.gps['longitude']

        print
        print '\tVariable\tMetadata'
        print '\t' + 40 * '-'
        print '\t' + self.filepath
        print '\t' + 40 * '-'
        print '\tTitle:\t\t%s' % self.metadata.title
        print '\tCaption:\t%s' % self.metadata.caption
        print '\tTaxon:\t\t%s' % ', '.join(self.metadata.taxon)
        print '\tTags:\t\t%s' % '\n\t\t\t'.join(self.metadata.tags)
        print '\tSize:\t\t%s' % self.metadata.size
        print '\tSource:\t%s' % ', '.join(self.metadata.source)
        print '\tAuthor:\t\t%s' % ', '.join(self.metadata.author)
        print '\tSublocation:\t%s' % self.metadata.sublocation
        print '\tCity:\t\t%s' % self.metadata.city
        print '\tState:\t\t%s' % self.metadata.state
        print '\tCountry:\t%s' % self.metadata.country
        print '\tRights:\t\t%s' % self.metadata.rights
        print '\tDate:\t\t%s' % self.metadata.date
        print
        print '\tGeolocation:\t%s' % self.metadata.gps['geolocation'].decode("utf8")
        print '\tDecimal:\t%s, %s' % (self.metadata.gps['latitude'],
                self.metadata.gps['longitude'])
        print

