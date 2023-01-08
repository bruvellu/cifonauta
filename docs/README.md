# Cifonauta documentation

[Cifonauta](http://cifonauta.cebimar.usp.br/) database is built from the metadata embedded in the multimedia files (photos and videos). Using the desktop app [[Véliger]], we store information about the species, stage of life, habitat, geolocation, and other data about the depicted organisms. These files are read, processed, and uploaded (or updated) on the website.

## Requirements

- [Python](http://www.python.org/)
- [Django](http://www.djangoproject.com/)
- [PostgreSQL](http://www.postgresql.org/)

## Installation

Tested on Ubuntu only. Known to work in Debian and potentially any Linux server
if package names are adjusted to match the distribution.

## Local install

Install system packages:

```
sudo apt update && sudo apt upgrade

sudo apt install git python3 python3-dev python3-pip python3-venv python3-gi postgresql postgresql-server-dev-all libpq-dev yui-compressor ffmpeg imagemagick gettext language-pack-pt gir1.2-gexiv2-0.10 libjpeg62 libjpeg62-dev zlib1g-dev
```

Clone repository:

```
git clone git@github.com:nelas/cifonauta.git
cd cifonauta
```

Create virtual environment:

```
python3 -m venv virtual
source virtual/bin/activate
```

Install Python packages using pip:

```
pip install --upgrade -r requirements.txt
ln -s /usr/lib/python3/dist-packages/gi virtual/lib/python3.7/site-packages/
```

Create PostgreSQL database:

```
sudo -s -u postgres
createuser -s nelas
service postgresql restart
createdb -E UTF8 -T template0 -l pt_BR.UTF8 cebimar
```

Load a database backup:

```
psql cebimar < database_dump.sql
```

Or create tables from scratch and load initial data (still incomplete):

```
./manage.py makemigrations
./manage.py migrate
./manage.py loaddata data/flatpages.json
```

Create superuser:

```
./manage.py createsuperuser
```

Prepare static files:

```
./manage.py collectstatic --noinput
```

Run local server:

```
./manage.py runserver
```

---

## Server install

For server install:

```
su -l

apt update && apt upgrade

apt install git python3 python3-dev python3-pip python3-venv python3-gi postgresql postgresql-server-dev-all libpq-dev yui-compressor ffmpeg imagemagick gettext language-pack-pt gir1.2-gexiv2-0.10 libjpeg62 libjpeg62-dev zlib1g-dev apache2 nginx rsync python3-markdown python3-memcache memcached libapache2-mod-wsgi-py3 policykit-1
```

Clone repository:

```
git clone https://github.com/nelas/cifonauta.git
cd cifonauta
```

Install Python packages using pip as root:

```
pip install --upgrade -r requirements.txt
```

Configure PostgreSQL database as root:

```
su - postgres
createuser -s nelas
exit
```

Restart PostgreSQL just in case:

```
systemctl restart postgresql
```

Create empty cebimar database as user nelas:

```
createdb -E UTF8 -T template0 -l pt_BR.UTF8 cebimar
```

Load a database backup:

```
gunzip < backups/cebimar_2019-09-21_1234.sql.gz | psql cebimar
```

Replace `peer` to `trust` in `/etc/postgresql/9.5/main/pg_hba.conf`:

``` 
# "local" is for Unix domain socket connections only
local   all             all                                     trust
```

First copy the local `server` directory into the remote project root:

```
scp -r server cifonauta:cifonauta/
```

Then copy the settings for the production site to the appropriate folder.

```
cp server/server_settings.py cifonauta/
```

As root, copy site configuration files:

```
cp server/etc_apache2_sites-enabled_cifonauta /etc/apache2/sites-available/cifonauta.conf
cp server/etc_nginx_sites-enabled_cifonauta /etc/nginx/sites-available/cifonauta.conf
```

If you get a 502 Gateway error, disable `Listen 80` in Apache’s `ports.conf`.

Update paths to reflect the current installation and activate sites:

```
a2ensite cifonauta
ln -s /etc/nginx/sites-available/cifonauta.conf /etc/nginx/sites-enabled/
```

Fix permissions for `site_media`:

```
groupadd www-users
adduser www-data www-users
adduser nelas www-users
adduser memcache www-users
chgrp -R www-users site_media/
chmod -R 760 site_media/
chgrp -R www-users static/
chmod -R 760 static/
```

### Local

### Server

## Management

## How to upgrade the Django version

1. Go into the local Cifonauta repository directory using `cd`
2. Run `source virtual/bin/activate` to activate the virtual environment
3. Open `requirements.txt` and modify `django==2.2.24` to the latest version
4. Run `pip install --upgrade -r requirements.txt` to update locally
5. Start a local server using `./manage.py runserver` and check website 
6. If all is fine, commit the change to the repository
7. Push the change to GitHub and deploy to server using `invoke deploy`
8. Access the server remotely using `ssh`
9. Become root and `cd` into the cifonauta directory
10. Run `pip3 install --upgrade -r requirements.txt`
11. Restart the server and check if the live website is fine

## How to clear expired/missing thumbnails

Thumbnails key/value pairs may stale and the images will not load. To fix it
run: `./manage.py thumbnail cleanup`.

## Upload new media

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


--- Outdated

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

# If something fails check if tags have non-empty values

## Reload database.


# Software

## Dependencies

Compiled in `requirements.txt`:

- wheel / handles Python packaging
- django==2.2.24 / core web framework
- psycopg2==2.8.6 / PostgreSQL adapter
- django-rosetta / translation framework
- django-modeltranslation / handles model translations
- requests / handles http requests
- django-mptt / handles tree models for taxa
- sorl-thumbnail / handles thumbnails
- pillow / handles image processing
- django-debug-toolbar / helps debugging django
- fabric / interface for deployment
- patchwork / handles remote shell calls

## Main

- [Python](http://www.python.org/)
- [Django](http://www.djangoproject.com/)
- [PostgreSQL](http://www.postgresql.org/)
- [Qt](http://qt.nokia.com/)
- [FFmpeg](http://www.ffmpeg.org/)
- [ImageMagick](http://www.imagemagick.org/)

## Python libs

- [IPTCInfo](https://bitbucket.org/gthomas/iptcinfo/)
- [pyexiv2](http://tilloy.net/dev/pyexiv2/)
- [Psycopg](http://initd.org/psycopg/)
- [python-oauth2](https://github.com/simplegeo/python-oauth2/)
- [python-suds](https://fedorahosted.org/suds/)
- [PyQt](http://www.riverbankcomputing.co.uk/software/pyqt/)
- [Fabric](http://fabfile.org/)

## Django packages

- [django-articles](https://github.com/codekoala/django-articles/)
- [django-mptt](https://github.com/django-mptt/django-mptt/)
- [django-rosetta](http://code.google.com/p/django-rosetta/)
- [django-datatrans](https://github.com/citylive/django-datatrans/)
- [django-debug-toolbar](https://github.com/robhudson/django-debug-toolbar/)
- [South](http://south.aeracode.org/)
- [sorl-thumbnail](https://github.com/sorl/sorl-thumbnail)
- [johnny-cache](http://packages.python.org/johnny-cache/)
- [dajaxice/dajax](http://www.dajaxproject.com/)

## Server

- [Apache](http://www.apache.org/)
- [Nginx](http://wiki.nginx.org/)
- [Memcached](http://memcached.org/)

## Web services

- [ITIS](http://www.itis.gov/)
- [Mendeley API](http://dev.mendeley.com/)

## HTML, CSS e JavaScript

- [jQuery](http://jquery.com/)
- [Blueprint](http://www.blueprintcss.org/)
- [VideoJS](http://videojs.com/)
- [HTML5 Boilerplate](http://html5boilerplate.com/)
- [Highslide JS](http://highslide.com/)
- [Slides](http://slidesjs.com/)
- [Treeview](http://bassistance.de/jquery-plugins/jquery-plugin-treeview/)

### Deprecated

- suds-jurko / SOAP client for biodiversity databases

# Véliger

[Véliger metadata editor](https://github.com/nelas/veliger) was developed in [Python](http://www.python.org/) with a [Qt](http://qt.nokia.com/) user interface. You can add/edit metadata from photos and videos, including geolocation (via GoogleMaps) and related bibliographic references (via MendeleyAPI). Below is a recent screenshot of the program interface:

![Véliger - Editor de Metadados](http://cifonauta.cebimar.usp.br/static/img/veliger2011_thumb.jpg)

# Roadmap


Feature wishlist for Cifonauta database.

## API development

Database is accessible with a structured url, but to really allow content integration with other services, mashups and programmatic access to data an API is essential.

## Mobile version

Implement responsive design for mobile browsing.


# Changelog

On this page you find the record of features and bugs being worked out and a revision history for our apps.

## Cifonauta

You can follow/fork/contribute with **Cifonauta** development via [github.com/nelas/cifonauta](https://github.com/nelas/cifonauta/).

### Alpha Tornária (current)

* Widget na barra lateral com vídeos relacionados com a foto (e vice-versa).
* Melhorar o tipo de paginação.
* Melhorar performance.  **[começado, mas continua]**
    - <del>Implementar cache.</del>
    - <del>Do servidor.</del>
    - <del>Otimizar queries ao banco de dados.</del>
* <del>Página com informações básicas para imprensa.</del>
* <del>Cache agressivo.</del>
* <del>Melhora sistema de logging para o cifonauta.py.</del>
* <del>Integração com o BHL SciELO.</del>
* <del>Remodelar a página principal para deixar mais informativa, leve e útil (e bonita).</del>
* <del>Padronização dos comentários.</del>
* <del>Dar uma geral nos feeds.</del>
* <del>Incluir duração dos vídeos nos thumbnails e página.</del>
* <del>Navegação rápida no rodapé.</del>
* <del>Gerar código para embed dos vídeos.</del>
* <del>Box "compartilhar" com saídas para apps sociais.</del>
* <del>Criar tours temáticos.</del>
* <del>Box "como citar?" para cada imagem.</del>
* <del>Implementar sistema de internacionalização e deixar site traduzível.</del>
* <del>Mostrar o tipo de metadado na página de um metadado.</del>
* <del>Coloquei buscador no cabeçalho.</del>
* <del>Arrumei página de literatura e páginas individuais das referências.</del>
* <del>Criar página para mostrar todas as imagens (e vídeos) com filtros por tipo de mídia, mais acessadas, etc.</del>
* <del>Melhoria no sistema de corrigir as infos de um táxon.</del>
* <del>Citações formatadas corretamente quando falta algum campo.</del>
* <del>Implementei sinal negativo no refinador e arrumei estilo.</del>
* <del>Fazer árvore taxonômica estar aberta no táxon mostrado.</del>
* <del>Reformulação do refinador para não usar o query.</del>
* <del>Lentidão para processar página de marcador.</del>
* <del>Erro na barra lateral do blog com apenas 1 post.</del>
* <del>Metadados de alguns vídeos não estão sendo importados.</del>

### Histórico das versões

#### v0.8.5

* <del>Melhorar aparência da árvore taxonômica.</del>
* <del>Página para arrumar os táxons sem hierarquia.</del>
* <del>Lidar com vídeos HD.</del>
* <del>Instalar South e mptt.</del>
* <del>Cria táxon vazio quando chega ao reino na hierarquia.</del>
* <del>Função recursiva para refinamento.</del>
* <del>Usar SOAP para interagir com ITIS.</del>

#### v0.8.4
* <del>Criar sistema de referências bibliográficas.</del>
* <del>Atualização e limpeza dos modelos para lidar com entradas em branco.</del>
* <del>Criar navegador linear.</del>
* <del>Sistema para consultar a hierarquia taxonômica do ITIS.</del>
* <del>Função para renomear arquivos.</del>

#### v0.8.2
* <del>Salvar vídeos no banco de dados.</del>
* <del>Funcionamento dos links para bancos externos.</del>
* <del>Adicionar favicon e logo.</del>
* <del>Implementar jQuery.</del>
* <del>Arrumação do layout.</del>
* <del>Aplicando DRY para urls.</del>
* <del>Preparação para internacionalização.</del>
* <del>Blog básico.</del>
* <del>Extração da geolocalização.</del>

## Véliger

Você também pode acompanhar as atualizações do **Véliger** pelo [github.com/nelas/veliger](https://github.com/nelas/veliger/).

### Atual

* Incorporar documentação na interface.
* Desenhar interface para facilitar a adição de marcadores.
* Importar perfil com metadados básicos e aplicar.

### Histórico das versões

#### v0.9.3

* <del>Módulo para aplicar metadados de uma entrada em uma pasta.</del>
* <del>Retirar campo espécie e mudar tamanho de lugar.</del>
* <del>Adequar atualização do timestamp dos vídeos.</del>
* <del>Acerto do Mendeley API para puxar referências sem paginação.</del>

#### v0.9.1

* <del>Bug na atualização das referências para Windows.</del>
* <del>Bug do GoogleMaps API.</del>
* <del>Lidar com fotos com EXIF incompleto.</del>

#### v0.9.0

* <del>Edição de metadados dos vídeos.</del>
* <del>Módulo de referências básico.</del>

#### v0.8.7

* <del>Bug da visibilidade do DockGeo.</del>
* <del>Substituir objetos pelo sinal certo PyQt_PyObject.</del>

#### v0.8.6

* <del>Validar geolocalização e data.</del>
* <del>Unificar a função de salvar, geo, editor e data.</del>
* <del>Widget para editar data da foto.</del>

#### v0.8.5

* <del>Implementar live update para deixar interface mais intuitiva.</del>
* <del>Unificar a função de salvar, geo, editor e data.</del>
* <del>Widget para editar data da foto.</del>

#### v0.8.2

* <del>Implementar geolocalização e integração com GoogleMaps.</del>

#### v0.8.1

* <del>Implementar autocomplete.</del>
* <del>Funcionar com ícones.</del>
* <del>Backups estratégicos.</del>
* <del>Edição de células múltiplas.</del>
* <del>Lista de imagens modificadas e notificações para usuários.</del>
* <del>Migrar para Qt.</del>
* <del>Transição para abandonar BerkeleyDB.</del>
* <del>Usando PIL (e não subprocess) para gerar thumbnails.</del>
