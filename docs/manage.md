# Management

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
