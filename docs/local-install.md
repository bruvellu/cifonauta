# Local installation

## Install system packages

First, open a terminal and install the required system packages (requires admin privileges):

```
sudo apt install git python3 python3-dev python3-pip python3-venv python3-gi postgresql postgresql-server-dev-all libpq-dev yui-compressor ffmpeg imagemagick gettext language-pack-pt gir1.2-gexiv2-0.10 libjpeg-dev zlib1g-dev
```

## Clone the repository

Then, change to a directory where you want to install the Cifonauta (can be any) and clone the repository using [`git`](https://git-scm.com/):

```
git clone https://github.com/bruvellu/cifonauta.git
```

## Create Python virtual environment

To install the remaining packages, we need to create a self-contained virtual environment.
Go into the repository directory you just cloned and run the python commands below to create and activate the virtual environment.

```
cd cifonauta
python3 -m venv virtual
source virtual/bin/activate
```

If this worked, you should see `(virtual)` on your command prompt.

## Install Django packages

Now, we install the remaining packages using [`pip`](https://pypi.org/project/pip/):

```
pip install --upgrade -r requirements.txt
```

This will install all the Django-specific and other Python-packages needed to run the database.
Test if the installation worked by running:

```
python manage runserver
```

You should this message:

```
(virtual) nelas@pilidium:~/CEBIMar/cifonauta$ python manage.py runserver 
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 08, 2023 - 16:16:46
Django version 2.2.28, using settings 'cifonauta.settings'
Starting development server at http://127.0.0.1:8000/
```

Press CTRL+C to kill it, for now.

## Create PostgreSQL database

Next, we create the PostgreSQL user and an empty database:

```
sudo -s -u postgres
createuser -s nelas
service postgresql restart
createdb -E UTF8 -T template0 -l pt_BR.UTF8 cebimar
```

If you have a database dump, now is the time to load it:

```
gunzip < cebimar_2019-09-21_1234.sql.gz | psql cebimar
```

## Run local server

With that, we can run the Cifonauta database using Django’s built-in local server:

```
python manage.py runserver
```

That’s it, you can access the local Cifonauta at http://127.0.0.1:8000/

**Note:** if you close the terminal, you’ll first need to activate the virtual environment to be able to run the local server again (for example, after a system restart).
For that, just go the repository directory and run:

```
source virtual/bin/activate
```

