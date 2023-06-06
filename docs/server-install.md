# Server installation

## Current server

### Requirements

- [Ubuntu](https://ubuntu.com/): Linux server
- [Gunicorn](https://gunicorn.org/): HTTP server
- [Nginx](https://www.nginx.com/): Proxy server
- [PostgreSQL](https://www.postgresql.org/): Relational database
- [Memcached](https://www.memcached.org/): Caching system

### Install system packages

Become root:

```
su -l
```

Make sure packages are up-to-date:

```
apt update && apt upgrade
```

Set the desired timezone:

```
timedatectl status
               Local time: Mon 2023-06-05 20:53:02 UTC
           Universal time: Mon 2023-06-05 20:53:02 UTC
                 RTC time: Mon 2023-06-05 20:53:02
                Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no

timedatectl set-timezone America/Sao_Paulo
timedatectl status
               Local time: Mon 2023-06-05 17:53:39 -03
           Universal time: Mon 2023-06-05 20:53:39 UTC
                 RTC time: Mon 2023-06-05 20:53:39
                Time zone: America/Sao_Paulo (-03, -0300)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

Add the Brazilian Portuguese locale:

```
locale -a
C
C.utf8
POSIX
en_US.utf8

locale-gen pt_BR.UTF-8

locale -a
C
C.utf8
en_US.utf8
POSIX
pt_BR.utf8
```

Install Python pip and virtual env:

```
apt install python3-pip python3-venv
```

Install Git:

```
apt install git
```

Install unzip:

```
apt install unzip
```

Install PostgreSQL and a psycopg2 required library:

```
apt install postgresql libpq-dev
```

Create a PostgreSQL user as root:

```
su - postgres
createuser -s user
exit
```

Create directory in partition and give the rights to the proper user:

```
cd /mnt/partition
mkdir cifonauta
chown user:user cifonauta
```

Now as the user (not root) clone the repository:

```
cd /mnt/partition
git clone https://github.com/bruvellu/cifonauta.git cifonauta/
```

Create a home symlink for easier access:

```
cd
ln -s /mnt/partition/cifonauta ~/
```

Copy the database and images to server:

```
scp -v cebimar_2023-05-09_2117.sql.gz cifonauta-server:/mnt/partition/cifonauta/
scp -v site_media.zip cifonauta-server:/mnt/partition/cifonauta/
```

Create a virtual environment:

```
python3 -m venv virtual
source virtual/bin/activate
```

Install Django and other required packages:

```
pip install --upgrade -r requirements.txt
```

Create empty cebimar database as user:

```
createdb -E UTF8 -T template0 -l pt_BR.UTF-8 cebimar

```

If you get an error, restart PostgreSQL and try again:

```
service postgresql restart
```

Load a database backup:

```
gunzip < cebimar_2023-05-09_2117.sql.gz | psql cebimar
```

Unzip media files into the `site_media` directory:

```
unzip site_media.zip
```

Next steps soon...


## Legacy server

Apache, Nginx, PostgreSQL, mod_wsgi (daemon mode), Memcached.

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
