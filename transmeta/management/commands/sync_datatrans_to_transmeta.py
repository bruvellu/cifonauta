"""
 Rebuild translations from datatrans to transmeta

"""

from optparse import make_option
from django.core.management.base import BaseCommand

from transmeta import get_languages, LANGUAGE_CODE, get_real_fieldname

from datatrans.utils import REGISTRY, KeyValue


class Command(BaseCommand):
    help = "Rebuild translations from datatrans to transmeta"

    option_list = BaseCommand.option_list + (
        make_option('-y', '--yes', action='store_true', dest='assume_yes',
                    help="Assume YES on all queries"),
        )

    def handle(self, *args, **options):
        """ command execution """
#        assume_yes = options.get('assume_yes', False)
        # for each language
        for lang in get_languages():
            lang_code = lang[LANGUAGE_CODE]
            for model in REGISTRY:
                fields = REGISTRY[model].values()
                total = model.objects.count()
                current = 0
                for instance in model.objects.all():
                    current += 1
                    save = False
                    for field in fields:
                        realname = get_real_fieldname(field.name, lang_code)
                        value = getattr(instance, field.name)
                        # if it's not the default message
                        if value != getattr(instance, realname):
                            new_value = KeyValue.objects.lookup(value, lang_code)
                            # if it's not the same value
                            if new_value != getattr(instance, realname):
                                setattr(instance, realname, new_value)
                                save = True
                    if save:
                        instance.save()
                    print "(Lang %s) Processed %s model, %04d / %04d" % (lang_code, model, current, total)
