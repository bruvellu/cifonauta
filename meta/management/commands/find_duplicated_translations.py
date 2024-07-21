import socket

from django.core.management.base import BaseCommand
from django.db.models import F
from lingua import Language, LanguageDetectorBuilder
from meta.models import Media


class Command(BaseCommand):
    help = 'Find duplicated translation in Media fields.'
    args = ''

    def add_arguments(self, parser):

        # Resolve duplicated translations interactively
        parser.add_argument('-i', '--resolve-interactively', action='store_true', dest='resolve_interactively', help='Interactively resolve translation duplicates.')

    def handle(self, *args, **options):
        
        # Parse options
        self.resolve_interactively = options['resolve_interactively']

        # Hostname
        # hostname = socket.gethostname()
        # self.stdout.write(f'HOSTNAME: {hostname}')

        # Initiate language detector
        languages = [Language.ENGLISH, Language.PORTUGUESE]
        self.detector = LanguageDetectorBuilder.from_languages(*languages).build()

        # Models and fields to check
        model_field_pairs = [{'model': Media, 'field': 'title'},
                             {'model': Media, 'field': 'caption'},
                             {'model': Media, 'field': 'acknowledgments'},]

        # Loop over model-field pairs
        for modelfield in model_field_pairs:
            model = modelfield['model']
            field = modelfield['field']
            self.check_duplicated_translations(model, field)


    def check_duplicated_translations(self, model, field):
        '''Pipeline for checking duplicated translations.'''

        # Get model name
        model_name = model.__name__

        # Define translation fields
        field_pt_br = f'{field}_pt_br'
        field_en = f'{field}_en'

        # Create filter and exclude queries
        filter_dups = {field_pt_br: F(field_en)}
        exclude_empty = {field_pt_br: ''}

        # Get entries with non-empty duplicated translations
        entries_with_duplicated_translations = model.objects.filter(**filter_dups).exclude(**exclude_empty)

        # Get values of duplicated translations
        duplicated_translations = entries_with_duplicated_translations.order_by(field_pt_br).values_list(field_pt_br, flat=True).distinct()

        # Print out statistics
        self.stdout.write(f'\nFound {entries_with_duplicated_translations.count()} "{model_name}" entries with duplicated "{field}" translations')

        # Loop over duplicated translation values
        for value in duplicated_translations:

            # Suggested outcome
            field_to_be_cleared = ''

            # Get entries matching this value
            files = entries_with_duplicated_translations.filter(**{field_pt_br: value})

            # Get list of IDs
            ids = files.values_list('id', flat=True)

            # Detect language of value
            lang = self.detector.detect_language_of(value)

            # Print diagnostics
            self.stdout.write(f'\n{field.upper()}: {value}')
            self.stdout.write(f'LANGUAGE: {lang.name}')
            self.stdout.write(f'{model_name} ID(s): {", ".join([str(id) for id in ids])}')
            self.stdout.write(f'TOTAL: {files.count()} entries')
            self.stdout.write(f'SUGGESTED:')
            if lang.name == 'PORTUGUESE':
                self.stdout.write(f'\t{field_pt_br}: {value}')
                self.stdout.write(f'\t{field_en}: \'\'')
                field_to_be_cleared = field_en
            elif lang.name == 'ENGLISH':
                self.stdout.write(f'\t{field_pt_br}: \'\'')
                self.stdout.write(f'\t{field_en}: {value}')
                field_to_be_cleared = field_pt_br

            # Manually resolve duplicated translations
            if self.resolve_interactively:

                # Wait for user confirmation
                self.stdout.write(f'ACCEPT?')
                self.stdout.write(f'This will apply the suggested changes to all entries above.')

                choice = input('ANSWER (yes/no): ')
                self.stdout.write(f'ACTION:')

                # Apply actions
                if choice == 'yes':
                    updated = files.update(**{field_to_be_cleared: ''})
                    self.stdout.write(f'\t{field_to_be_cleared} cleared in {updated} entries')
                else:
                    self.stdout.write(f'\tNo changes. Skipping...')


