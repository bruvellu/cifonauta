# Server installation

## Requirements

- [Ubuntu](https://ubuntu.com/): Linux server
- [Gunicorn](https://gunicorn.org/): HTTP server
- [Nginx](https://www.nginx.com/): Proxy server
- [PostgreSQL](https://www.postgresql.org/): Relational database
- [Memcached](https://www.memcached.org/): Caching system

### Become root (or use `sudo`)

Become root to have the permissions to install system packages:

```
su -l
```

Or precede the commands with `sudo`.

### Update repository packages

Make sure the packages are up-to-date:

```
apt update && apt upgrade
```

### Update timezone

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

### Update locale

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

### Install translation-related packages

```
apt install gettext language-pack-pt
```

### Install and configure PostgreSQL

Install PostgreSQL, the relational database, and a required psycopg2 library:

```
apt install postgresql postgresql-server-dev-all libpq-dev
```

Create a PostgreSQL user using the name of your user (replace it below):

```
su - postgres
createuser --superuser --createrole --createdb user
exit
```

### Install and test memcached

Install memcached:

```
apt install memcached libmemcached-tools
```

Check if memcached is running by using telnet:

```
telnet localhost 11211
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.

stats
STAT pid 68841
STAT uptime 1156
STAT time 1686170212
STAT version 1.6.14
...
```

If not, start memcached:

```
service memcached start
```

The second package provides a tool for flushing the cache after an update:

```
memcflush --servers=127.0.0.1:11211
```

### Install Nginx server

Install Nginx:

```
apt install nginx
```

### Install git

Install Git to clone and manage the repository:

```
apt install git
```

### Install unzip tool

Needed to unzip media files:

```
apt install unzip
```

### Install Python packages

Install Python pip and env for installing packages and creating virtual environments:

```
apt install python3-pip python3-venv
```

### Install exiv2-related dependencies

These are needed to compile the `py3exiv2` package.
```
apt install libexiv2-dev libboost-python-dev python3-all-dev g++
```

### Install zlib for gzip compression

```
apt install zlib1g-dev
```

### Install media-related packages

FFmpeg for video processing, and the other is a dependency for JPG processing in Pillow.

```
apt install ffmpeg libjpeg-dev
```

### Install package for content types

This package helps to identify content types of uploaded files.

```
apt install libmagic1
```

### Set up directory

Create a directory in the main partition, and give its ownership to the proper user:

```
cd /mnt/partition
mkdir cifonauta
chown user:user cifonauta
```

### Clone repository

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

### Create virtual env and install requirements

Create a virtual environment and activate it:

```
cd cifonauta
python3 -m venv virtual
source virtual/bin/activate
```

Install Django and other required packages using pip:

```
pip install --upgrade -r requirements.txt
```

### Install memcache Python bindings

Install memcached binding library:

```
pip install pymemcache
```

### Install gunicorn

Install Gunicorn:

```
pip install gunicorn
```

### Create empty database

Create an empty `cebimar` database:

```
createdb -E UTF8 -T template0 -l pt_BR.UTF-8 cebimar
```

If you get an error, restart PostgreSQL and try again:

```
service postgresql restart
```

### Copy and load database dump

Copy the database dump and image files from your computer to the server:

```
scp -v cebimar_2023-05-09_2117.sql.gz cifonauta-server:/mnt/partition/cifonauta/
scp -v site_media.zip cifonauta-server:/mnt/partition/cifonauta/
```

Load a database backup:

```
gunzip < cebimar_2023-05-09_2117.sql.gz | psql cebimar
```

### Copy media files

Unzip media files into the `site_media` directory:

```
unzip site_media.zip
```

Or `rsync` media files:

```
rsync -ahu --progress source/media_files/ local/media_files/
```

### Create server settings

Create a `cifonauta/server_settings.py` with:

```
# Django settings for cifonauta production server.

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

ADMINS = (
    ('Nome Sobrenome', 'email@email.com'),
)

MANAGERS = ADMINS

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dbname',
            'USER': 'dbuser',
            }
        }

CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:PORT',
            }
        }

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 2592000
CACHE_MIDDLEWARE_KEY_PREFIX = 'prefix'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'your-secret-key'

ALLOWED_HOSTS = [
    'SERVER DOMAIN NAME',
    'SERVER IP ADDRESS',
    '127.0.0.1',
    '[::1]',
    ]
```

### Create .env file

Environment variables for production.

```
FILENAME_REGEX=^$
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
```

### Test gunicorn

Test Gunicorn:

```
gunicorn cifonauta.wsgi
[2023-06-07 17:42:41 -0300] [70104] [INFO] Starting gunicorn 20.1.0
[2023-06-07 17:42:41 -0300] [70104] [INFO] Listening at: http://127.0.0.1:8000 (70104)
[2023-06-07 17:42:41 -0300] [70104] [INFO] Using worker: sync
[2023-06-07 17:42:41 -0300] [70105] [INFO] Booting worker with pid: 70105
```

### Configure gunicorn services

Create systemd service for gunicorn (number of workers = cores*2+1):

Location: `/etc/systemd/system/gunicorn.service`

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=user
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/home/user/cifonauta
EnvironmentFile=/home/nelas/cifonauta/.env
ExecStart=/home/user/cifonauta/virtual/bin/gunicorn --access-logfile - --workers 17 --timeout 60 --bind unix:/run/gunicorn.sock cifonauta.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Create socket file:

Location: `/etc/systemd/system/gunicorn.socket`

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

Enable and start daemon:

```
systemctl enable --now gunicorn.socket
```

### Configure Nginx site

Create nginx configuration:

Location: `/etc/nginx/sites-available/cifonauta`

```
server {

        listen 80;

        server_name IPADDRESS DOMAIN;

        location = /favicon.ico { access_log off; log_not_found off; }

        location / {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
        }

        location /static/ {
                root /home/user/cifonauta/;
        }

        location /media_files/ {
                root /home/user/cifonauta/;
        }

        # Set file limit on server side
        client_max_body_size 500M;

}

```

Enable site:

```
ln -s /etc/nginx/sites-available/cifonauta /etc/nginx/sites-enabled/
```

### Password protect website

To password protect the entire site first install:

```
apt install apache2-utils
```

Then, create a user/pass combination:

```
htpasswd -c /etc/nginx/htpasswd user
```

And add to /etc/nginx/sites-available/cifonauta inside `location /`:

```
auth_basic "Cifonauta staging";
auth_basic_user_file /etc/nginx/htpasswd;
```

### Generate static files

Generate static directory for serving:

```
./manage.py collectstatic --noinput
```

If Nginx can’t access static or media and returns 403 forbidden error, add www-data to user group:

```
sudo gpasswd -a www-data user
```

### Test site

Test everything with:

```
sudo -u www-data curl --unix-socket /run/gunicorn.sock http
```

(may fail)

### Setting up HTTPS

As root:

```
apt install python3-certbot-nginx
certbot --nginx -d staging.cifonauta.cebimar.usp.br

Saving debug log to /var/log/letsencrypt/letsencrypt.log
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): cifonauta@usp.br

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.3-September-21-2022.pdf. You must
agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: Y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: N
Account registered.
Requesting a certificate for staging.cifonauta.cebimar.usp.br

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/staging.cifonauta.cebimar.usp.br/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/staging.cifonauta.cebimar.usp.br/privkey.pem
This certificate expires on 2023-10-28.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for staging.cifonauta.cebimar.usp.br to /etc/nginx/sites-enabled/cifonauta
Congratulations! You have successfully enabled HTTPS on https://staging.cifonauta.cebimar.usp.br

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

The domain must already be working on the current server.
Otherwise you get an error like this:

```
certbot --nginx -d cifonauta.cebimar.usp.br
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for cifonauta.cebimar.usp.br

Certbot failed to authenticate some domains (authenticator: nginx). The Certificate Authority reported these problems:
  Domain: cifonauta.cebimar.usp.br
  Type:   unauthorized
  Detail: XXX.XXX.XXX.XXX: Invalid response from http://cifonauta.cebimar.usp.br/.well-known/acme-challenge/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX: 404

Hint: The Certificate Authority failed to verify the temporary nginx configuration changes made by Certbot. Ensure the listed domains point to this nginx server and that it is accessible from the internet.

Some challenges have failed.
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.
```
