# Taxonomic management

To fetch taxonomic records from WoRMS run the command:

```
python3 manage.py update_taxa
```

In case of error run the `rebuild()` method from the Taxon model (based on django-mptt):

```
python3 manage.py shell
from meta.models import Taxon
Taxon.objects.rebuild()
```
