# Server installation (outdated!)

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
