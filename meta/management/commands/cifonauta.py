from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video
from optparse import make_option
import os


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
    n = 0
    n_new = 0
    n_up = 0

    def handle(self, *args, **options):
        '''Command execution trunk.'''

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

        print(photo_filepaths)
        print(video_filepaths)

        self.stdout.write('%d unique names. -p:%s, -m:%s' % (options['number'],
                                                             options['photos'],
                                                             options['videos']))
        self.stdout.write('Source:%s' % self.SITE_MEDIA)


class Database:
    '''Define objeto que interage com o banco de dados.'''
    def __init__(self):
        pass

    def search_db(self, media):
        '''Query database for filename.

        Compare timestamps, if equal, skip, if different, update.
        '''
        print
        print('Procurando %s (%s) no banco de dados...',
                media.filename, media.source_filepath)
        photopath = 'photos/'
        videopath = 'videos/'

        try:
            if media.type == "photo":
                # Busca pelo nome exato do arquivo, para evitar confuso.
                record = Image.objects.get(web_filepath=photopath + media.filename)
            elif media.type == "video":
                try:
                    record = Video.objects.get(webm_filepath=videopath + media.filename.split('.')[0] + '.webm')
                except:
                    try:
                        record = Video.objects.get(mp4_filepath=videopath + media.filename.split('.')[0] + '.mp4')
                    except:
                        try:
                            record = Video.objects.get(ogg_filepath=videopath + media.filename.split('.')[0] + '.ogv')
                        except:
                            print('%s no est no banco de dados.',
                                    media.filename)
                            return False
            print('Bingo! Registro de %s encontrado.', media.filename)
            print('Comparando timestamp do arquivo com o registro...')
            # XXX Dirty hack to make naive timestamp.
            record.timestamp = record.timestamp.replace(tzinfo=None)
            if record.timestamp != media.timestamp:
                print('Arquivo mudou! Retorna 1')
                return 1
            else:
                print('Arquivo no mudou! Retorna 2')
                return 2
        except Image.DoesNotExist:
            print('Registro no encontrado (Image.DoesNotExist).')
            return False

    def update_db(self, media, update=False):
        '''Cria ou atualiza registro no banco de dados.'''
        print('Atualizando o banco de dados...')
        # Instancia metadados pra no dar conflito.
        media_meta = media.meta
        # Guarda objeto com infos taxonmicas.
        taxa = media_meta['taxon']
        del media_meta['taxon']
        # Preveno contra extinto campo de espcie.
        try:
            del media_meta['genus_sp']
        except:
            pass
        # Guarda objeto com autores
        authors = media_meta['author']
        # Guarda objeto com especialistas
        sources = media_meta['source']
        del media_meta['source']
        # Guarda objeto com tags
        tags = media_meta['tags']
        del media_meta['tags']
        # Guarda objeto com referncias
        refs = media_meta['references']
        del media_meta['references']

        # No deixar entrada pblica se faltar ttulo ou autor
        if media_meta['title'] == '' or not media_meta['author']:
            print('Mdia %s sem ttulo ou autor!',
                    media_meta['source_filepath'])
            media_meta['is_public'] = False
        else:
            media_meta['is_public'] = True
        # Deleta para inserir autores separadamente.
        del media_meta['author']

        # Transforma valores em instncias dos modelos
        toget = ['size', 'rights', 'sublocation',
                'city', 'state', 'country']
        for k in toget:
            print('META (%s): %s', k, media_meta[k])
            # Apenas criar se no estiver em branco.
            if media_meta[k]:
                media_meta[k] = self.get_instance(k, media_meta[k])
                print('INSTANCES FOUND: %s', media_meta[k])
            else:
                del media_meta[k]

        if not update:
            if media.type == 'photo':
                entry = Image(**media_meta)
            elif media.type == 'video':
                entry = Video(**media_meta)
            # Tem que salvar para criar id, usado na hora de salvar as tags
            entry.save()
        else:
            if media.type == 'photo':
                entry = Image.objects.get(web_filepath__icontains=media.filename)
            elif media.type == 'video':
                entry = Video.objects.get(webm_filepath__icontains=media.filename.split('.')[0])
            for k, v in media_meta.iteritems():
                setattr(entry, k, v)

        # Atualiza autores
        entry = self.update_sets(entry, 'author', authors)

        # Atualiza especialistas
        entry = self.update_sets(entry, 'source', sources)

        # Atualiza txons
        entry = self.update_sets(entry, 'taxon', taxa)

        # Atualiza marcadores
        entry = self.update_sets(entry, 'tag', tags)

        # Atualiza referncias
        entry = self.update_sets(entry, 'reference', refs)

        # Salvando modificaes
        entry.save()

        print('Registro no banco de dados atualizado!')

    def get_instance(self, table, value):
        '''Retorna o id a partir do nome.'''
        # TODO Create hook to avoid badly formatted characters to be saved.
        # Any new tag should be manually confirmed and corrected.
        #model, new = eval('%s.objects.get_or_create(name="%s")' % (table.capitalize(), value))

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
                fixed_value = raw_input('\nNovo metadado. Digite para confirmar: ')
            try:
                model, new = eval('%s.objects.get_or_create(name="%s")' % (table.capitalize(), fixed_value))
                if new:
                    print('Novo metadado %s criado!' % fixed_value)
                else:
                    print('Metadado %s j existia!' % fixed_value)
                    # Add to bad data dictionary.
                    bad_data[value] = fixed_value
                    bad_data_file = open('bad_data.pkl', 'wb')
                    pickle.dump(bad_data, bad_data_file)
                    bad_data_file.close()
                # TODO Fix metadata field on original image!!!
            except:
                print('Objeto %s no foi encontrado! Abortando...' % fixed_value)

        # Consulta ITIS para extrair txons.
        if table == 'taxon' and new:
            taxon = self.get_itis(value)
            # Refora, caso a conexo falhe.
            if not taxon:
                taxon = self.get_itis(value)
                if not taxon:
                    print('Nova tentativa em 5s...')
                    time.sleep(5)
                    taxon = self.get_itis(value)
            try:
                # Por fim, atualizar o modelo.
                model = taxon.update_model(model)
            except:
                print('No rolou pegar hierarquia...')
        return model

    def update_sets(self, entry, field, meta):
        '''Atualiza campos many to many do banco de dados.

        Verifica se o value no est em branco, para no adicionar entradas em
        branco no banco.
        '''
        print('META (%s): %s', field, meta)
        meta_instances = [self.get_instance(field, value) for value in meta if value.strip()]
        print('INSTANCES FOUND: %s', meta_instances)
        eval('entry.%s_set.clear()' % field)
        [eval('entry.%s_set.add(value)' % field) for value in meta_instances if meta_instances]
        return entry

    def get_itis(self, name):
        '''Consulta banco de dados do ITIS.

        Extrai o txon pai e o ranking. Valores so guardados em:

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
    '''Classes de objetos para lidar com as pastas e seus arquivos.

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
            print('%d files found.', n)

        return self.files

