from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video, Tag, TagCategory, Taxon, City, State, Country, Tour, Size
from django.utils import translation

# Model fields that need translation.
all_fields = [
        (Image, ['title', 'caption']),
        (Video, ['title', 'caption']),
        (Tag, ['name', 'description']),
        (TagCategory, ['name', 'description']),
        (Taxon, ['common', 'rank']),
        (City, ['name']),
        (State, ['name']),
        (Country, ['name']),
        (Tour, ['name', 'description']),
        (Size, ['description'])
        ]


class Command(BaseCommand):
    help = 'Dump translatable fields to a python file.'

    def handle(self, *args, **options):
        # Make sure all content is returned in default language.
        translation.activate('pt-br')
        self.stdout.write('\nLANGUAGE: {}'.format(translation.get_language()))
        # Output file.
        # Create python file for output.
        filepath = 'model_translator/values_for_translation.py'
        self.stdout.write('\nDUMP FILE: {}'.format(filepath))
        # Open file and begin.
        trans_file = open(filepath, 'wb')
        trans_file.write('from django.utils.translation import ugettext_lazy as _\n\n')

        # Loop through models.
        for translator in all_fields:
            model = translator[0]
            fields = translator[1]
            self.stdout.write('\nDumping {}'.format(model.__name__))

            # Loop through fields.
            for field in fields:
                values = model.objects.values_list(field, flat=True)
                # Write values to file.
                for v in values:
                    # TODO: Define the easiest to parse comment.
                    trans_file.write('# Translators: model={model}, field={field}.\n'.format(model=model.__name__, field=field))
                    trans_file.write('_(\'{}\')\n'.format(v.encode('utf-8')))
                self.stdout.write('\t{}... done.'.format(field))

        # Close file.
        trans_file.close()
