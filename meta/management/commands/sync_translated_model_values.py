from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video, Tag, TagCategory, Taxon, City, State, Country, Tour, Size
from django.utils import translation
import polib
import re

# Dictionary to get model object.
models = {
        'Image': Image,
        'Video': Video,
        'Tag': Tag,
        'TagCategory': TagCategory,
        'Taxon': Taxon,
        'City': City,
        'State': State,
        'Country': Country,
        'Tour': Tour,
        'Size': Size,
        }

class Command(BaseCommand):
    help = 'Sync translated model values to database.'

    def handle(self, *args, **options):
        # Make sure all content is returned in default language.
        translation.activate('pt-br')
        self.stdout.write('\nLANGUAGE: {}'.format(translation.get_language()))
        # Open .po file.
        filepath = 'model_translator/locale/en/LC_MESSAGES/django.po'
        po_entries = polib.pofile(filepath)
        self.stdout.write('FILE: {}'.format(filepath))
        # RegEx to identify model and field.
        regex = re.compile(r'model=(?P<model>\w+), field=(?P<field>\w+).')
        # Read entries.
        for entry in po_entries:
            # Skip if translation does not exist.
            if not entry.msgstr:
                continue
            # Identify model and field.
            search = regex.search(entry.comment)
            model = models[search.group('model')]
            field = search.group('field')
            self.stdout.write(u'\nUPDATING: {model} -> {field}'.format(model=model.__name__, field=field))
            # Query for all instances with the exact msgid.
            self.stdout.write(u'\n\tmsgid: {msgid}'.format(msgid=entry.msgid))
            self.stdout.write(u'\tmsgstr: {msgstr}'.format(msgstr=entry.msgstr))
            query = {field: entry.msgid}
            instances = model.objects.filter(**query)
            # Update values for each instance.
            for instance in instances:
                # Field to be updated.
                field_en = '{field}_en'.format(field=field)
                translated_field = getattr(instance, field_en)
                # Decide whether to update or skip.
                if translated_field == entry.msgstr:
                    self.stdout.write(u'\n\tSKIPPED: {id}'.format(id=instance.id))
                else:
                    # Apply with setattr and save()
                    setattr(instance, field_en, entry.msgstr)
                    instance.save()
                    self.stdout.write(u'\n\tSAVED: {id}'.format(id=instance.id))


