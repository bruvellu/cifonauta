from django.core.management.base import BaseCommand, CommandError
from meta.models import Media, Tag, TagCategory, Taxon, City, State, Country, Tour
from django.utils import translation
import polib
import re

# Dictionary to get model object.
models = {
        'Media': Media,
        'Tag': Tag,
        'TagCategory': TagCategory,
        'Taxon': Taxon,
        'City': City,
        'State': State,
        'Country': Country,
        'Tour': Tour,
        }

class Command(BaseCommand):
    help = 'Sync translated model values to database.'

    def handle(self, *args, **options):

        # Make sure all content is returned in default language.
        translation.activate('pt-br')
        self.stdout.write('\nLANGUAGE: {}'.format(translation.get_language()))

        # Open .po file.
        filepath = 'model_translator/locale/en/LC_MESSAGES/django.po'
        po = polib.pofile(filepath)
        self.stdout.write('FILE: {}'.format(filepath))

        # Get non-obsolete entries only
        valid_entries = [e for e in po if not e.obsolete]

        # RegEx to identify model and field.
        regex = re.compile(r'model=(?P<model>\w+), field=(?P<field>\w+).')

        # Read po valid entries.
        for entry in valid_entries:

            # Identify model and field.
            search = regex.search(entry.comment)
            model = models[search.group('model')]
            field = search.group('field')

            # Query all instances with the exact msgid.
            self.stdout.write('\nmsgid: {msgid}'.format(msgid=entry.msgid))
            self.stdout.write('msgstr: {msgstr}'.format(msgstr=entry.msgstr))
            query = {field: entry.msgid}
            instances = model.objects.filter(**query)

            # Update values for each instance.
            for instance in instances:

                # Field to be updated.
                field_en = '{field}_en'.format(field=field)
                translated_field = getattr(instance, field_en)

                # Both field and translation are empty, skip.
                if not translated_field and not entry.msgstr:
                    message = 'EMPTY VALUES, SKIPPING...'

                # Translation is empty, save model field to po file.
                elif translated_field and not entry.msgstr:
                    entry.msgstr = translated_field
                    po.save(filepath)
                    message = 'SAVED TO PO FILE.'

                # Field and translation are identical, skip.
                elif translated_field == entry.msgstr:
                    message = 'IDENTICAL, SKIPPING...'

                # Both exist, save msgstr to model field.
                else:
                    # Apply with setattr and save()
                    setattr(instance, field_en, entry.msgstr)
                    instance.save()
                    message = 'SAVED TO MODEL.'

                self.stdout.write('{model} (ID={id}) {field}: {message}'.format(model=model.__name__, id=instance.id, field=field_en, message=message))
