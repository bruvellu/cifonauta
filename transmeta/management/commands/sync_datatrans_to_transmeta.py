"""
 Rebuild translations from datatrans to transmeta

"""

from optparse import make_option
from django.core.management.base import BaseCommand

from transmeta import get_languages, LANGUAGE_CODE, get_real_fieldname,\
    fallback_language

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
        default_language = fallback_language()
        for lang in get_languages():
            lang_code = lang[LANGUAGE_CODE]
            if lang_code == default_language:
                continue
            for model in REGISTRY:
                fields = REGISTRY[model].values()
                total = model.objects.count()
                current = 0
                for instance in model.objects.all():
                    current += 1
                    save = False
                    # for each field in this model
                    for field in fields:
                        # get the real field name (with language suffix)
                        realname = get_real_fieldname(field.name, lang_code)
                        # original language
                        original = get_real_fieldname(field.name, default_language)
                        # original value
                        original_value = getattr(instance, original)
                        # get current value
                        value = getattr(instance, realname)
                        if value == None:
                            value = ""
                        new_value = KeyValue.objects.lookup(original_value, lang_code)
                        # if it's not the default message
                        if new_value != value:
                            # if it's not the same value
                            setattr(instance, realname, new_value)
                            save = True
                    print "(Lang %s) Processed %s model, %04d / %04d" % (lang_code, model, current, total),
                    if save:
                        instance.save()
                        print " (changed)"
                    else:
                        print ""