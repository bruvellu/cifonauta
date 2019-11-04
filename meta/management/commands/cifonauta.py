import os
import pickle
import time

from optparse import make_option
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.utils import timezone

from cifonauta.settings import BASE_DIR, SOURCE_ROOT, MEDIA_ROOT, PHOTO_EXTENSIONS, VIDEO_EXTENSIONS, MEDIA_EXTENSIONS
from media_utils import *
from linking import LinkManager
from meta import models
from worms import Aphia


class Command(BaseCommand):
    args = ''
    help = 'Main function of the Cifonauta database.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', action='store',
                        dest='number', default=20000,
                        help='Number of files to scan.')
        parser.add_argument('-p', '--only-photos', action='store_true',
                        dest='photos', default=False,
                        help='Only scan photos.')
        parser.add_argument('-m', '--only-movies', action='store_true',
                        dest='videos', default=False,
                        help='Only scan videos.')

    def handle(self, *args, **options):
        '''Command execution trunk.'''

        # Stats.
        t0 = time.time()
        n = 0
        n_new = 0
        n_updated = 0

        # Some variables.
        n_max = int(options['number'])
        only_photos = options['photos']
        only_videos = options['videos']

        # Choose which file extensions.
        if only_photos:
            extensions = PHOTO_EXTENSIONS
        elif only_videos:
            extensions = VIDEO_EXTENSIONS
        else:
            extensions = MEDIA_EXTENSIONS

        # Initiate database instance.
        cbm = Database()

        # Get list of files in source_media.
        source_media = Folder(SOURCE_ROOT, extensions, n_max)

        self.stdout.write('\nProcessing {} file(s)...'.format(n_max))

        # Process files in source_media.
        for src_file in source_media.files[:n_max]:
            # Search database.
            record, modified = cbm.search_db(src_file)
            # Entry exists and timestamp has not changed.
            if record and not modified:
                self.stdout.write('\nENTRY UP-TO-DATE! NEXT...')
            # Entry exists and timestamps differ.
            elif record and modified:
                self.stdout.write('\nUPDATING ENTRY...')
                src_file.create_meta(record)
                cbm.update_db(src_file, update=True)
                self.stdout.write('\nPROCESSING MEDIA...')
                src_file.process_media()
                n_updated += 1
            # Entry does not exits in the database.
            elif not record:
                self.stdout.write('NEW FILE!')
                src_file.create_meta()
                cbm.update_db(src_file)
                self.stdout.write('\nPROCESSING MEDIA...')
                src_file.process_media()
                n_new += 1


        # Number of files analyzed.
        n = len(source_media.files[:n_max])

        # Statistics.
        self.stdout.write('\nFINISHED!')
        self.stdout.write('{} files'.format(n))
        self.stdout.write('{} new'.format(n_new))
        self.stdout.write('{} updated'.format(n_updated))
        t = time.time() - t0
        if t > 60:
            self.stdout.write('\nRunning time: {} min {} s\n'.format(int(t / 60), int(t % 60)))
        else:
            self.stdout.write('\nRunning time: {:.1f} s\n'.format(t))


class Database:
    '''Database object.'''
    def __init__(self):
        # Set language to Portuguese.
        translation.activate('pt-br')

    def search_db(self, media):
        '''Query database for filename.

        Compare timestamps and return record and status (True or False).
        '''
        print('\nQUERY: {}'.format(media.filepath))

        # Query for the exact filename to avoid confusion.
        try:
            record = models.Media.objects.get(filepath=media.filepath)
            print('DB RECORD: Yes -> {}'.format(record))
            if record.timestamp != media.timestamp:
                print()
                print('MODIFIED: Yes -> {} != {}'.format(record.timestamp, media.timestamp))
                return record, True
            else:
                print('MODIFIED: No')
                return record, False
        except:
            print('DB RECORD: No')
            return None, False

    def update_db(self, media, update=False):
        '''Creates or updates database entry.'''
        print('\nDATABASE:')

        # Instantiate metadata for processing.
        media_meta = media.metadata.dictionary

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
        #refs = media_meta['references']
        #del media_meta['references']

        # Keep media with incomplete metadata private.
        if media_meta['title'] == '' or not media_meta['author']:
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Delete key to insert authors separately.
        del media_meta['author']

        # Transform values in model instances.
        toget = ['location', 'city', 'state', 'country']
        for k in toget:
            # Create only if not blank.
            if media_meta[k]:
                media_meta[k] = self.get_instance(k, media_meta[k])
            else:
                del media_meta[k]

        # Saving is needed to create an ID.
        if not update:
            entry = models.Media(**media_meta)
            entry.save()
        else:
            entry = models.Media.objects.get(filepath=media_meta['filepath'])
            for k, v in media_meta.items():
                setattr(entry, k, v)

        # Update authors.
        entry = self.update_sets(entry, 'author', authors)

        # Update sources.
        entry = self.update_sets(entry, 'person', sources)

        # Update taxa.
        entry = self.update_sets(entry, 'taxon', taxa)

        # Update tags.
        entry = self.update_sets(entry, 'tag', tags)

        # Update references.
        #entry = self.update_sets(entry, 'reference', refs)

        # Saving modifications.
        entry.save()

        print('Entry updated!')

    def get_instance(self, table, value):
        '''Returns ID from name.'''

        # Set language to Portuguese.
        translation.activate('pt-br')

        print('  {} = {}'.format(table, value))

        # Needs a default in case objects exists.
        new = False

        # Try to get object. If it doesn't exist, confirm to avoid bad metadata.
        try:
            if table == 'author':
                empty_model = getattr(models, 'person'.capitalize())
                model = empty_model.objects.get(name=value)
                model.is_author = True
                model.save()
            else:
                empty_model = getattr(models, table.capitalize())
                model = empty_model.objects.get(name=value)
        except:
            # Load bad data dictionary.
            try:
                bad_data_file = open('bad_data.pkl', 'rb')
                bad_data = pickle.load(bad_data_file)
                bad_data_file.close()
            except:
                bad_data = {}
            try:
                fixed_value = bad_data[value]
                print('  "{}" automatically fixed to "{}"'.format(value, bad_data[value]))
            except:
                fixed_value = input('\n     Press enter to confirm OR type the correct value: ') or value
            try:
                if table == 'author':
                    empty_model = getattr(models, 'person'.capitalize())
                    model, new = empty_model.objects.get_or_create(name=fixed_value, is_author=True)
                else:
                    empty_model = getattr(models, table.capitalize())
                    model, new = empty_model.objects.get_or_create(name=fixed_value)
                if new:
                    print('     > "{}" created!\n'.format(fixed_value))
                else:
                    print('     > "{}" already existed!\n'.format(fixed_value))
                    # Add to bad data dictionary.
                    bad_data[value] = fixed_value
                    bad_data_file = open('bad_data.pkl', 'wb')
                    pickle.dump(bad_data, bad_data_file)
                    bad_data_file.close()
                # TODO Fix metadata field on original image!!!
            except:
                print('Object "{}" not found! Or auto-fix failed.'.format(fixed_value))

        # Check WoRMS for taxonomic info.
        if table == 'taxon' and new:
            taxon = self.get_worms(value)
            if taxon:
                model = taxon
        return model

    def update_sets(self, entry, field, meta):
        '''Update many to many database fields.

        Verifies if value is blank.
        '''
        if meta:
            meta_instances = [self.get_instance(field, value) for value in meta if value.strip()]
            # Get set and clear it.
            if field == 'author':
                field = 'person'
            meta_set = getattr(entry, field + '_set')
            meta_set.clear()
            # Add updated values to set.
            if meta_instances:
                for value in meta_instances:
                    meta_set.add(value)
        return entry

    def get_worms(self, name):
        '''Query WoRMS database and get valid record.'''
        aphia = Aphia()
        record = aphia.get_best_match(name)
        if record:
            taxon, new = models.Taxon.objects.get_or_create(name=record['scientificname'])
            taxon.rank_en = record['rank']
            taxon.aphia = record['AphiaID']
            taxon.timestamp = timezone.now()
            taxon.save()
        else:
            return None


class Folder:
    '''Take care of directories and its files.'''

    def __init__(self, folder, extensions, n_max):
        self.folder_path = folder
        self.extensions = extensions
        self.n_max = n_max
        self.files = []

        print('\nDIRECTORY: {}'.format(self.folder_path))

        # Call function to get files.
        self.get_files()

    def get_files(self):
        '''Recursively search files in the directory.'''
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if filename.lower().endswith(self.extensions):
                    #print(root, dirs, filename)
                    rel_dir = os.path.relpath(root, BASE_DIR)
                    filepath = os.path.join(rel_dir, filename)
                    source_file = File(filepath)
                    self.files.append(source_file)
                else:
                    continue
            else:
                continue
        else:
            print('FILES: {}'.format(len(self.files)))

        # Is the folder empty?
        if not self.files:
            print('Empty folder {}?'.format(self.folder_path))
        return self.files


class File:
    '''A general file model.'''
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.timestamp = timezone.make_aware(datetime.fromtimestamp(
            os.path.getmtime(self.filepath)))
        self.type = self.get_filetype()
        self.metadata = None

    def __str__(self):
        return self.filepath

    def get_filetype(self):
        '''Find out if photo or video based on the extension.'''
        if self.filepath.lower().endswith(PHOTO_EXTENSIONS):
            return 'photo'
        elif self.filepath.lower().endswith(VIDEO_EXTENSIONS):
            return 'video'
        else:
            return 'unknown'

    def create_meta(self, db_entry=None):
        '''Parse and instantiate media metadata.

        Uses GExiv2 library for IPTC and EXIF.
        '''
        self.metadata = Meta(self, db_entry)

    def process_media(self):
        '''Copy and process files to site_media.'''

        if self.type == 'photo':
            # TODO: Replace site_media by MEDIA_ROOT
            # Process photo.
            photo_sitepath = os.path.join('site_media', self.metadata.sitepath)
            photo_to_web(self.filepath, photo_sitepath)
            # Process photo cover.
            photo_coverpath = os.path.join('site_media', self.metadata.coverpath)
            photo_to_web(self.filepath, photo_coverpath, size=512)
        elif self.type == 'video':
            # Process video.
            video_sitepath = os.path.join('site_media', self.metadata.sitepath)
            video_to_web(self.filepath, video_sitepath, self.metadata)
            # Process video cover.
            video_coverpath = os.path.join('site_media', self.metadata.coverpath)
            grab_still(self.filepath, video_coverpath)



class Meta:
    '''Metadata object'''
    def __init__(self, media, db_entry=None):
        '''Initialize metadata.'''
        self.media = media
        self.db_entry = db_entry
        self.dictionary = {}

        # Default values.
        self.filepath = self.media.filepath
        self.sitepath = ''
        self.coverpath = ''
        self.datatype = self.media.type
        self.timestamp = self.media.timestamp
        self.date = self.media.timestamp  # Default to modification date.
        self.title = ''
        self.caption = ''
        self.tags = ''
        self.author = ''
        self.city = ''
        self.location = ''
        self.state = ''
        self.country = ''
        self.taxon = ''
        self.size = ''
        self.source = ''
        #self.references = ''

        self.gps = {'geolocation':'','latitude':'','longitude':''}
        self.geolocation = ''
        self.latitude = ''
        self.longitude = ''

        self.duration = ''
        self.dimensions = ''

        # Parse metadata.
        if self.media.type == 'photo':
            self.parse_photo()
        elif self.media.type == 'video':
            self.parse_video()

        # Prepare some fields for the database.
        self.prepare_meta()

        # Define paths.
        self.define_paths()

        # Make dictionary.
        self.build_dictionary()

        # Print summary of metadata.
        self.print_metadata()

    def parse_photo(self):
        '''Parse photo metadata.'''

        # Create metadata object.
        info = read_photo_metadata(self.media.filepath)

        # Fill values with IPTC data.
        self.title = self.get_photo_tag(info, 'Iptc.Application2.ObjectName')         #5
        self.caption = self.get_photo_tag(info, 'Iptc.Application2.CaptionAbstract')  #120
        self.tags = self.get_photo_tag(info, 'Iptc.Application2.Keywords')            #25
        self.author = self.get_photo_tag(info, 'Iptc.Application2.Byline')            #80
        self.city = self.get_photo_tag(info, 'Iptc.Application2.City')                #90
        self.location = self.get_photo_tag(info, 'Iptc.Application2.SubLocation')     #92
        self.state = self.get_photo_tag(info, 'Iptc.Application2.ProvinceState')      #95
        self.country = self.get_photo_tag(info, 'Iptc.Application2.CountryName')      #101
        self.taxon = self.get_photo_tag(info, 'Iptc.Application2.Headline')           #105
        self.size = self.get_photo_tag(info, 'Iptc.Application2.SpecialInstructions') #40
        self.source = self.get_photo_tag(info, 'Iptc.Application2.Source')            #115
        #self.references = self.get_photo_tag(info, 'Iptc.Application2.Credit')        #110

        # Extracting EXIF data.
        self.date = get_date(info)
        self.gps = get_gps(info)
        self.geolocation = self.gps['geolocation']
        self.latitude = self.gps['latitude']
        self.longitude = self.gps['longitude']

    def get_photo_tag(self, info, tag):
        '''Get tag value or return empty string.'''
        # Keywords need a different command.
        multiples = ['Iptc.Application2.Keywords']
        try:
            if tag in multiples:
                value = info.get_tag_multiple(tag)
            else:
                value = info.get_tag_string(tag)
        except:
            value = ''
        return value

    def parse_video(self):
        '''Parse video metadata.'''

        # Check and get metadata from accessory txt file.
        txt_path = os.path.splitext(self.filepath)[0] + '.txt'
        try:
            os.lstat(txt_path)
            txt_file = open(txt_path, 'rb')
        except:
            txt_file = ''

        # Fill out metadata from accessory txt file.
        if txt_file:
            txt_dic = pickle.load(txt_file)

            # Define metadata.
            self.title = self.get_video_tag(txt_dic, 'title')
            self.tags = self.get_video_tag(txt_dic, 'tags')
            self.author = self.get_video_tag(txt_dic, 'author')
            self.city = self.get_video_tag(txt_dic, 'city')
            self.location = self.get_video_tag(txt_dic, 'sublocation')
            self.state = self.get_video_tag(txt_dic, 'state')
            self.country = self.get_video_tag(txt_dic, 'country')
            self.taxon = self.get_video_tag(txt_dic, 'taxon')
            self.rights = self.get_video_tag(txt_dic, 'rights')
            self.caption = self.get_video_tag(txt_dic, 'caption')
            self.size = self.get_video_tag(txt_dic, 'size')
            self.source = self.get_video_tag(txt_dic, 'source')
            #self.references = self.get_video_tag(txt_dic, 'references')
            self.date = self.get_video_tag(txt_dic, 'date')
            self.geolocation = self.get_video_tag(txt_dic, 'geolocation')
            self.latitude = self.get_video_tag(txt_dic, 'latitude')
            self.longitude = self.get_video_tag(txt_dic, 'longitude')

            # Close file.
            txt_file.close()

        # TODO: Check if geolocation is empty.

        # Extracts duration and dimensions
        infos = get_info(self.filepath)
        self.duration = infos['duration']
        self.dimensions = infos['dimensions']


    def get_video_tag(self, info, tag):
        '''Extracts tag from accessory text file.'''
        try:
            value = info[tag]
            if tag == 'date':
                # FIXME: This will fail silently if the date has no time.
                value = timezone.make_aware(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
        except:
            value = ''
        return value

    def none_to_empty(self, metadata):
        '''Convert None to empty string.'''
        if metadata is None:
            return ''
        else:
            return metadata

    def prepare_meta(self):
        '''Cleanup metadata for database input.'''
        # Convert None to empty string.
        self.title = self.none_to_empty(self.title)
        self.caption = self.none_to_empty(self.caption)
        self.tags = self.none_to_empty(self.tags)
        self.author = self.none_to_empty(self.author)
        self.city = self.none_to_empty(self.city)
        self.location = self.none_to_empty(self.location)
        self.state = self.none_to_empty(self.state)
        self.country = self.none_to_empty(self.country)
        self.taxon = self.none_to_empty(self.taxon)
        self.size = self.none_to_empty(self.size)
        self.source = self.none_to_empty(self.source)
        #self.references = self.none_to_empty(self.references)

        # Size choices.
        size_choices = {
                '<0,1 mm': 'micro',
                '0,1 - 1,0 mm': 'tiny',
                '1,0 - 10 mm': 'visible',
                '10 - 100 mm': 'large',
                '>100 mm': 'huge',
                }

        # Convert size to tag and use slug string.
        if self.size:
            self.tags.append(self.size)
            self.size = size_choices[self.size]
        else:
            self.size = 'none'

        # Transform to list.
        if self.author:
            self.author = [a.strip() for a in self.author.split(',')]
        else:
            self.author = []
        if self.source:
            self.source = [a.strip() for a in self.source.split(',')]
        else:
            self.source = []
        #self.references = [a.strip() for a in self.references.split(',')]

        if self.taxon:
            temp_taxa = [a.strip() for a in self.taxon.split(',')]
            clean_taxa = []
            # Take care of aff. and species with 3 names.
            for taxon in temp_taxa:
                tsplit = taxon.split()
                if len(tsplit) == 2 and tsplit[-1] in ['sp', 'sp.', 'spp']:
                    tsplit.pop()
                    clean_taxa.append(tsplit[0])
                else:
                    clean_taxa.append(taxon)
            self.taxon = clean_taxa
        else:
            self.taxon = []

    def define_paths(self):
        '''Define sitepaths.'''
        if self.db_entry:
            # Get names from database.
            self.sitepath = self.db_entry.sitepath.name
            self.coverpath = self.db_entry.coverpath.name
        else:
            # Create new sitename.
            self.sitename = create_filename(self.media.filename, self.author)

            # Create new sitepath.
            if self.media.type == 'photo':
                self.sitepath = '{}.jpg'.format(os.path.splitext(self.sitename)[0])
            elif self.media.type == 'video':
                self.sitepath = '{}.mp4'.format(os.path.splitext(self.sitename)[0])

            # Create new coverpath.
            self.coverpath = '{}_{}.jpg'.format(os.path.splitext(self.sitepath)[0], 'cover')

    def build_dictionary(self):
        '''Generates dictionary for canonical database processing.'''

        self.dictionary = {
            'filepath': self.filepath,
            'sitepath': self.sitepath,
            'coverpath': self.coverpath,
            'datatype': self.datatype,
            'title': self.title,
            'caption': self.caption,
            'tags': self.tags,
            'author': self.author,
            'city': self.city,
            'location': self.location,
            'state': self.state,
            'country': self.country,
            'taxon': self.taxon,
            'size': self.size,
            'source': self.source,
            #'references': self.references,
            'timestamp': self.timestamp,
            'date': self.date,
            'geolocation': self.geolocation,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'duration': self.duration,
            'dimensions': self.dimensions,
            }

    def print_metadata(self):
        '''Print metadata for reference.'''
        print('\nMETADATA:')
        for k, v in self.dictionary.items():
            if v:
                if isinstance(v, list):
                    print('  {}:'.format(k))
                    for i in v:
                        print('    {}'.format(i))
                else:
                    print('  {} = {}'.format(k, v))

