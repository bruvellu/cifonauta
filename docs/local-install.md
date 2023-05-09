# Local installation on Linux (Ubuntu)

## Install system packages

First, open a terminal and install the required system packages (needs admin privileges):

```
sudo apt install git python3 python3-dev python3-pip python3-venv python3-gi postgresql postgresql-server-dev-all libpq-dev yui-compressor ffmpeg imagemagick gettext language-pack-pt gir1.2-gexiv2-0.10 libjpeg-dev zlib1g-dev
```

## Clone the repository

Then, change to a directory where you want to install the Cifonauta and clone the repository using [`git`](https://git-scm.com/):

```
git clone https://github.com/bruvellu/cifonauta.git
```

If you only want to clone a specific branch, execute:

```
git clone --branch <branchname> https://github.com/bruvellu/cifonauta.git
```

## Create Python virtual environment

To install the remaining packages, we need to create a self-contained virtual environment.
Go into the repository directory you just cloned and run the python commands below to create and activate the virtual environment.

```
cd cifonauta
python3 -m venv virtual
source virtual/bin/activate
```

If this worked, you should see `(virtual)` on your command prompt:

```
(virtual) user@device:~/your/dir$
```

## Install Django packages

Now, we install the remaining packages using [`pip`](https://pypi.org/project/pip/):

```
pip install --upgrade -r requirements.txt
```

This will install all the Django-specific and other Python-packages needed to run the database.
Test if the installation worked by running:

```
python manage.py runserver
```

You should this message:

```
(virtual) user@device:~/your/dir$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 09, 2023 - 16:59:36
Django version 4.2.1, using settings 'cifonauta.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Press CTRL+C to kill the local server, for now.

## Create PostgreSQL database

Next, we create the PostgreSQL user and an empty database:

```
sudo -s -u postgres
createuser -s nelas
service postgresql restart
createdb -E UTF8 -T template0 -l pt_BR.UTF8 cebimar
```

## Load database

To populate the empty database with the latest dump:

```
gunzip < cebimar_2019-09-21_1234.sql.gz | psql cebimar
```

## Add media files

Unzip the media files into the `site_media` directory:

```
unzip -uv site_media.zip
```

## Run local server

Once the database and media files are ready, we can run the local server again:

```
python manage.py runserver
```

That’s it, you can access the local Cifonauta at http://127.0.0.1:8000/

