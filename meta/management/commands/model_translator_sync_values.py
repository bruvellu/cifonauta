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

            # Expected:
            # entry.msgid == field_pt_br
            # entry.msgstr == field_en

            # Query all instances with the exact msgid (field_pt_br)
            query = {field_pt_br: entry.msgid}
            instances = model.objects.filter(**query)

            # Skip entries with specific values
            skip = ''

            # Update values for each instance
            for instance in instances:

                # Get current model fields from instance
                model_field_pt_br = getattr(instance, field_pt_br)
                model_field_en = getattr(instance, field_en)
                self.stdout.write(f'\nMODEL={model.__name__} (id={instance.id})')

                # Skip instances with specific values
                if model_field_pt_br == skip:
                    continue

                # Show current fields for inspection
                self.stdout.write(f'FIELD={field}')
                self.stdout.write(f'      PT_DB: {model_field_pt_br.replace(" ", "·")}')
                self.stdout.write(f'      PT_PO: {entry.msgid.replace(" ", "·")}')
                self.stdout.write(f'  [1] EN_DB: {model_field_en.replace(" ", "·")}')
                self.stdout.write(f'  [2] EN_PO: {entry.msgstr.replace(" ", "·")}')

                #TODO: Add case, if msgid == msgstr, empty msgstr

                # Deal with model and pofile duplicated translations

                # Skip instances with duplicated model translations
                if model_field_pt_br == model_field_en:
                    self.stdout.write('DUPLICATED MODEL TRANSLATION, SKIPPING...')
                    # Run ./manage.py find_duplicated_translations
                    continue

                # Clear duplicated pofile translations
                elif entry.msgid == entry.msgstr:
                    entry.msgstr = ''
                    po.save(filepath)
                    self.stdout.write('DUPLICATED POFILE TRANSLATION, CLEARING...')

                # Sync non-duplicated translation values

                # Model and pofile translations are empty
                if not model_field_en and not entry.msgstr:
                    message = 'EMPTY VALUES, SKIPPING...'

                # Model and pofile translations are identical
                elif model_field_en == entry.msgstr:
                    message = 'IDENTICAL VALUES, SKIPPING...'

                # Pofile translation is empty and model field is not duplicated
                elif not entry.msgstr and model_field_en and (model_field_en != model_field_pt_br):
                    entry.msgstr = model_field_en
                    po.save(filepath)
                    message = 'SAVED TO POFILE.'

                # Model field is empty and pofile translation is not duplicated
                elif not model_field_en and entry.msgstr and (entry.msgstr != entry.msgid):
                    setattr(instance, field_en, entry.msgstr)
                    instance.save()
                    message = 'SAVED TO MODEL.'

                # Model and pofile translations exist
                elif model_field_en and entry.msgstr:
                    if resolve_conflicts:
                        choice = input('CONFLICT! Select the correct translation. Type 1 or 2: ')
                        if choice == '1':
                            entry.msgstr = model_field_en
                            po.save(filepath)
                            message = 'CONFLICT! SAVED TO POFILE.'
                        elif choice == '2':
                            setattr(instance, field_en, entry.msgstr)
                            instance.save()
                            message = 'CONFLICT! SAVED TO MODEL.'
                        elif choice == 's':
                            skip = model_field_pt_br
                            message = 'SKIPPING SUBSEQUENT IDENTICAL INSTANCES...'
                        else:
                            message = 'CONFLICT NOT RESOLVED...'
                    else:
                        message = 'CONFLICT! SKIPPING FOR LATER...'

                # Remaining conditions (should not happen)
                else:
                    message = 'YOU SHOULD NOT SEE THIS...'

                self.stdout.write(f'{message}')

