# Upload new images and videos

Describes the general procedure for uploading new media to the Cifonauta database. Follow the steps.

Create unique_names dump.

`some manage.py command.`

1. Add new media files to the "oficial" directory. The directories are organized by Author/Taxa/Species.
2. Run linking.py. The script will create symbolic links for all the files in "oficial" to the directory "linked_media". All the subsequent procedures is done at the "linked_media" folder. `python linking.py`
3. Run handle_ids.py. The script will create unique names for the new files after checking with the latest dump file of unique names. `python handle_ids.py`
4. Run manage.py cifonauta. `./manage.py cifonauta`

Rebuild index
`./manage.py rebuild_index -v 2 -b 100`

If something fails check if tags have non-empty values

---

Outdated

# How to add and manage content

- Add original media files to `source_media` directory.

# Create unique_names.pkl dump.
./manage.py dump_filenames_from_db

# Add new media files to the "oficial" directory. The directories are
# organized by Author/Taxa/Species.

# Run linking.py. The script will create symbolic links for all the files in
# "oficial" to the directory "linked_media". All the subsequent procedures is
# done at the "linked_media" folder.
./linking.py

# Run handle_ids.py. The script will create unique names for the new files
# after checking with the latest dump file of unique names.
./handle_ids.py

# Run manage.py cifonauta. It'll create or update the website database.
./manage.py cifonauta

## Caveats.
# - Taxon fetching is not working.
# - Timestamp needs not to be naive.
# - Fix bad_data only works for non-utf8.
# - Does not fix metadata of original image.
# - Eventually just check capture photo for videos.

# Translate.
cd model_translator
django-admin makemessages -a
# Translate everything using rosetta.
django-admin compilemessages
cd ..
./manage.py sync_translated_model_values

# Rebuild ElasticSearch index.
./manage.py rebuild_index -v 2 -b 100
