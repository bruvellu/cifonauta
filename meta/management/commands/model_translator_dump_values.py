from django.core.management.base import BaseCommand, CommandError
from meta.models import Media, Tag, Category, Taxon, City, State, Country, Tour


# Model fields that need translation
all_fields = [
        (Media, ['title_pt_br', 'caption_pt_br', 'acknowledgments_pt_br']),
        (Taxon, ['rank_pt_br', 'status_pt_br']),
        (Tag, ['name_pt_br', 'description_pt_br']),
        (Category, ['name_pt_br', 'description_pt_br']),
        # (City, ['name_pt_br']),
        # (State, ['name_pt_br']),
        # (Country, ['name_pt_br']),
        (Tour, ['name_pt_br', 'description_pt_br']),
        ]


class Command(BaseCommand):
    help = 'Dump translatable fields to a python file.'

    def handle(self, *args, **options):
        # Create python file for output
        #TODO: Add as an option to settings
        filepath = 'meta/values_for_translation.py'
        self.stdout.write(f'FILE: {filepath}')

        # Open file and begin
        trans_file = open(filepath, 'w')
        trans_file.write('from django.utils.translation import gettext_lazy as _\n\n')

        # Loop through models
        for translator in all_fields:
            model = translator[0]
            fields = translator[1]
            self.stdout.write(f'\nMODEL: {model.__name__}')

            # Loop through fields
            for field in fields:
                values = model.objects.order_by(field).values_list(field, flat=True).distinct()
                # Write values to file
                for value in values:
                    if value:
                        # Escape single quotes and strip empty values
                        escaped_value = value.replace("'", "\\'").strip()
                        if escaped_value:
                            trans_file.write(f'# Translators: model={model.__name__}, field={field}.\n')
                            trans_file.write(f'_(\'{escaped_value}\')\n')
                self.stdout.write(f'  {field}... done.')
        self.stdout.write(f'\n')

        # Close file
        trans_file.close()

