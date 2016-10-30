import re
import csv

# Iterate through PO file.
# Write every line.
# When untranslated string is found, check if translation is available.
# Write to file the translated version.

# Translation files.
pofile = open('model_translator/locale/en/LC_MESSAGES/django.po', 'r')
outfile = open('model_translator/locale/en/LC_MESSAGES/trans.po', 'w')

# Translatable queries in csv.
csv_path = open('translation_queries/all.csv', 'r')
csv_file = csv.reader(csv_path)

# Create dictionary to store translations.
translations = {}
for row in csv_file:
    if row and len(row) > 2:
        print row
        translations[row[0]] = row[2]

# Define variables.
msgid = u''
msgstr = u''

# RegEx pattern.
regex = re.compile(r'msgid "(?P<msgid>.*)"')

# Iterate through file lines.
for line in pofile:
    if line.startswith('msgstr'):
        if msgtr_write:
            outfile.write(line)
        continue
    if line.startswith('msgid'):
        search = regex.search(line)
        msgid = search.group('msgid')
        if msgid and msgid in translations.keys():
            msgstr = translations[msgid]
            print(msgstr)
            outfile.write(line)
            outfile.write('msgstr "{}"\n'.format(msgstr))
            msgtr_write = False
        else:
            outfile.write(line)
            msgtr_write = True
    else:
        outfile.write(line)

outfile.close()
