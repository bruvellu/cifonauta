# Server installation

## Current server

### Requirements

- [Ubuntu](https://ubuntu.com/): Linux server
- [Gunicorn](https://gunicorn.org/): HTTP server
- [Nginx](https://www.nginx.com/): Proxy server
- [PostgreSQL](https://www.postgresql.org/): Relational database
- [Memcached](https://www.memcached.org/): Caching system

### Configure and install system packages (as root)

Become root to have the permissions to install system packages:

```
su -l
```

Make sure the package repositories are up-to-date:

```
apt update && apt upgrade
```

Check the server timezone setting:

```
timedatectl status
               Local time: Mon 2023-06-05 20:53:02 UTC
           Universal time: Mon 2023-06-05 20:53:02 UTC
                 RTC time: Mon 2023-06-05 20:53:02
                Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

Set the server’s desired timezone (`America/Sao_Paulo`):

```
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

For the database, it’s important to enable the proper system locale.
Check the enabled locales:

```
locale -a
C
C.utf8
POSIX
en_US.utf8
```

Add the Brazilian Portuguese locale (`pt_BR.UTF-8`):

```
locale-gen pt_BR.UTF-8

locale -a
C
C.utf8
en_US.utf8
POSIX
pt_BR.utf8
```

Install Python pip and env for installing packages and creating virtual environments:

```
apt install python3-pip python3-venv
```

Install Git to clone and manage the repository:

```
apt install git
```

Install unzip to unzip media files:

```
apt install unzip
```

Install PostgreSQL, the relational database, and a required psycopg2 library:

```
apt install postgresql libpq-dev
```

Create a PostgreSQL user using the same user name as your user:

```
su - postgres
createuser -s user
exit
```

Create a directory in the main partition, and give its ownership to the proper user:

```
cd /mnt/partition
mkdir cifonauta
chown user:user cifonauta
```

### Configure and install Cifonauta packages (as user)

Now as user (not root), clone the Cifonauta’s repository:

```
cd /mnt/partition
git clone https://github.com/bruvellu/cifonauta.git cifonauta/
```

Create a symlink to the repository in your home for easier access:

```
cd
ln -s /mnt/partition/cifonauta ~/
```

Create a virtual environment and activate it:

```
python3 -m venv virtual
source virtual/bin/activate
```

Install Django and other required packages using pip:

```
pip install --upgrade -r requirements.txt
```

Create an empty `cebimar` database:

```
createdb -E UTF8 -T template0 -l pt_BR.UTF-8 cebimar
```

If you get an error, restart PostgreSQL and try again:

```
service postgresql restart
```

Copy the database dump and image files from your computer to the server:

```
scp -v cebimar_2023-05-09_2117.sql.gz cifonauta-server:/mnt/partition/cifonauta/
scp -v site_media.zip cifonauta-server:/mnt/partition/cifonauta/
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
