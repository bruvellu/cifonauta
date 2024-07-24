from django.core.management.base import BaseCommand, CommandError
from meta.models import Media, Tag, Category, Taxon, City, State, Country, Tour
from django.utils import translation
import polib
import re

# Dictionary to get model objects
models = {
        'Media': Media,
        'Taxon': Taxon,
        'Tag': Tag,
        'Category': Category,
        # 'City': City,
        # 'State': State,
        # 'Country': Country,
        'Tour': Tour,
        }

class Command(BaseCommand):
    help = 'Sync translated model values to database.'
    args = ''

    def add_arguments(self, parser):

        # Resolve translation conflicts between model field and PO file
        parser.add_argument('-r', '--resolve-conflicts', action='store_true', dest='resolve_conflicts', help='Manually resolve translation conflicts.')

    def handle(self, *args, **options):

        # Make sure all the content is returned in the default language
        translation.activate('pt-br')
        self.stdout.write(f'\nLANGUAGE: {translation.get_language()}')

        # Parse options
        resolve_conflicts = options['resolve_conflicts']

        # Open .po file
        #TODO: Check if this code still works with meta/values_for_translation.py
        # filepath = 'model_translator/locale/en/LC_MESSAGES/django.po'
        #TODO: This PO file also has other translations
        filepath = 'meta/locale/en/LC_MESSAGES/django.po'
        po = polib.pofile(filepath)
        self.stdout.write(f'FILE: {filepath}')

        # Get non-obsolete entries only
        valid_entries = [e for e in po if not e.obsolete]

        # RegEx to identify model and field
        regex = re.compile(r'model=(?P<model>\w+), field=(?P<field>\w+).')

        # Read .po valid entries
        for entry in valid_entries:

            # Search for model and field comment
            search = regex.search(entry.comment)

            # If not a model field, skip entry
            if not search:
                continue

            # Parse model and field
            model = models[search.group('model')]
            field = search.group('field')
            field_pt_br = f'{field}_pt_br'
            field_en = f'{field}_en'

            # Query all instances with the exact msgid (field_pt_br)
            query = {field: entry.msgid}
            instances = model.objects.filter(**query)

            # Update values for each instance
            for instance in instances:

                # Get current translated field from instance
                translated_field = getattr(instance, field_en)

                # Write current fields
                self.stdout.write(f'\nMODEL={model.__name__} (id={instance.id})')
                self.stdout.write(f'FIELD={field}')
                self.stdout.write(f'  [0] PT_DB: {entry.msgid}')
                self.stdout.write(f'  [1] EN_DB: {translated_field}')
                self.stdout.write(f'  [2] EN_PO: {entry.msgstr}')

                # Field and translation are empty, skip
                if not translated_field and not entry.msgstr:
                    message = 'EMPTY VALUES, SKIPPING...'

                # Field and translation are identical, skip
                elif translated_field == entry.msgstr:
                    message = 'IDENTICAL VALUES, SKIPPING...'

                # Translation is empty, save field to .po file
                elif translated_field and not entry.msgstr:
                    entry.msgstr = translated_field
                    po.save(filepath)
                    message = 'SAVED TO POFILE.'

                # Field is empty, save translation to model
                elif not translated_field and entry.msgstr:
                    setattr(instance, field_en, entry.msgstr)
                    instance.save()
                    message = 'SAVED TO MODEL.'

                # Field and translation exist, skip or resolve?
                elif translated_field and entry.msgstr:
                    if resolve_conflicts:
                        choice = input('CONFLICT! Select the correct translation. Type 1 or 2: ')
                        if choice == '1':
                            entry.msgstr = translated_field
                            po.save(filepath)
                            message = 'CONFLICT! SAVED TO POFILE.'
                        elif choice == '2':
                            setattr(instance, field_en, entry.msgstr)
                            instance.save()
                            message = 'CONFLICT! SAVED TO MODEL.'
                        else:
                            message = 'CONFLICT NOT RESOLVED...'
                    else:
                        message = 'CONFLICT! SKIPPING FOR LATER...'

                # Remaining conditions (should not happen)
                else:
                    message = 'YOU SHOULD NOT SEE THIS...'

                self.stdout.write(f'{message}')

