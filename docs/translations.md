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

## Duplicates

To identify duplicated translations in `Media` entries, run:

```
python3 manage.py find_duplicated_translations
```

This will find entries where the translated fields, `title_pt_br` and `title_en`, for example, have identical values.
The command will detect the language of the field, and output some diagnostics and a suggested resolution:

```
TITLE: Vista geral do substrato rochoso
LANGUAGE: PORTUGUESE
ENTRIES: 10696
TOTAL: 1 files
SUGGESTED:
	title_pt_br: Vista geral do substrato rochoso
	title_en: ''

TITLE: "Man-of-war fish"
LANGUAGE: ENGLISH
ENTRIES: 9686
TOTAL: 1 files
SUGGESTED:
	title_pt_br: ''
	title_en: "Man-of-war fish"
```

Note that the language detection is not 100% accurate, and sometimes entries in Portuguese and English will have the same names.
But with the provided entry IDs, one can fix the duplicated translations using the admin interface.

To interactively fix these duplicated values, run the command with the `-i` option:

```
python3 manage.py find_duplicated_translations -i
```

The output now will ask if you want to apply the suggested change:

```
TITLE: Anfioxo - região anterior, vista dorsal
LANGUAGE: PORTUGUESE
ENTRIES: 7176, 7178, 7179, 7181, 7182, 7183, 7185, 7186, 7188, 7189, 7191
TOTAL: 11 files
SUGGESTED:
	title_pt_br: Anfioxo - região anterior, vista dorsal
	title_en: ''
ACCEPT?
This will apply the suggested changes to all entries above.
ANSWER (yes/no): yes
ACTION:
	title_en cleared in 11 entries
```

If the choice is `yes`, one of the fields will be set to an empty string in all the entries having this identical value.
The changes are applied directly to the database, therefore, be careful.

