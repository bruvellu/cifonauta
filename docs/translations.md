# Translations management

## Application

The translations for template strings is handled by Django’s built-in localization and internationalization support.

To make a string translatable in models or views use:

```
from django.utils.translation import gettext_lazy as _
string = _('This is a translatable string')
```

To make translatable strings in templates use:

```
{% load i18n %}

{% trans 'This is a translatable string' %}

{% blocktrans %}This is a long translatable paragraph.{% endblocktrans %}
```

To generate and compile localization files run:

```
cd meta
python3 ../manage.py makemessages --no-obsolete --all
python3 ../manage.py compilemessages
```

To edit translations, we use [Rosetta](https://django-rosetta.readthedocs.io).

## Models

The translation of model fields is handled by [modeltranslation](https://django-modeltranslation.readthedocs.io/en/latest/) and by custom management commands from `model_translator`.

To dump all translatable model fields into a regular python file named `values_for_translation.py` as translatable strings run:

```
python3 manage.py model_translator_dump_values
```

Now run `makemessages` and `compilemessages` within the `model_translator` directory to generate translations:

```
cd meta
python3 ../manage.py makemessages --no-obsolete --all
python3 ../manage.py compilemessages
```

Finally, edit the translations in the Rosetta interface.

There’s also a management command to synchronize identical translations and resolve translation conflicts between the database and the locale file.
The command will fill empty values if a translation exists, which is useful if there are many images with the same title, for example.
To run:

```
python3 manage.py model_translator_sync_values
```
