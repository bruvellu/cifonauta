import socket

from django.core.management.base import BaseCommand
from django.db.models import F
from meta.models import Media


class Command(BaseCommand):
    help = 'Fix missing Portuguese translations in Media fields.'
    args = ''

    def handle(self, *args, **options):
        
        # Models and fields to check
        model_field_pairs = [{'model': Media, 'field': 'title'},
                             {'model': Media, 'field': 'caption'},
                             {'model': Media, 'field': 'acknowledgments'},
                             ]

        # Loop over model-field pairs
        for modelfield in model_field_pairs:
            model = modelfield['model']
            field = modelfield['field']
            self.fix_missing_translations(model, field)


    def fix_missing_translations(self, model, field):
        '''Pipeline for fixing missing Portuguese translations.'''

        # Get model name
        model_name = model.__name__

        # Define translation fields
        field_pt_br = f'{field}_pt_br'
        field_en = f'{field}_en'

        # Create filter and exclude queries
        filter_missing = {field_pt_br: ''}
        exclude_missing = {field_en: ''}

        # Get entries missing Portuguese translations
        entries_missing_translations = model.objects.filter(**filter_missing).exclude(**exclude_missing)

        # Get English values for missing Portuguese translations
        missing_translations = entries_missing_translations.order_by(field_en).values_list(field_en, flat=True).distinct()

        # Print out statistics
        self.stdout.write(f'\nFound {entries_missing_translations.count()} "{model_name}" entries missing the "{field}" translation in Portuguese')

        # Loop over duplicated translation values
        for value in missing_translations:

            # Get entries matching this value
            files = entries_missing_translations.filter(**{field_en: value})

            # Get list of IDs
            ids = files.values_list('id', flat=True)

            # Print diagnostics
            self.stdout.write(f'\n{model_name} ID(s): {", ".join([str(id) for id in ids])}')
            self.stdout.write(f'TOTAL: {files.count()} entries')
            self.stdout.write(f'\t{field_pt_br}: ')
            self.stdout.write(f'\t   {field_en}: {value}')
            choice = input('TRANSLATE? (yes/no): ')
            if choice == 'yes':
                translation = input(f'TYPE: ')
                self.stdout.write(f'\t{field_pt_br}: {translation}')
                self.stdout.write(f'\t   {field_en}: {value}')
                confirmation = input(f'CONFIRM? (yes/no): ')
                if confirmation == 'yes':
                    updated = files.update(**{field_pt_br: translation})
                    self.stdout.write(f'\t{field_pt_br} saved in {updated} entries')
                else:
                    self.stdout.write(f'\tNo changes. Skipping...')
            else:
                self.stdout.write(f'\tNo changes. Skipping...')


