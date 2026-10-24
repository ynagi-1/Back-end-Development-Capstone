# Back-end-Development-Capstone

Djirection band website based on the official IBM Skills Network
sfvih-Back-end-Development-Capstone template. Django provides the website,
accounts, concert administration and RSVP storage. Flask microservices provide
Songs from MongoDB and Pictures from the course dataset.

## Python 3.9 development environment

Validated locally with Python 3.9.25, Django 4.2.30 and SQLite.
All seven Django flow tests passed against authentication, RSVP and page behavior.

```sh
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt greenlet==3.1.1
python manage.py migrate
python manage.py test
export SONGS_SERVICE_URL=http://127.0.0.1:8080/song
export PICTURES_SERVICE_URL=http://127.0.0.1:3000/picture
python manage.py runserver 0.0.0.0:8000
```

On Windows, activate .venv/Scripts/activate and use Windows environment variable
syntax. The course Linux lab also provides bash ./bin/setup.sh. Start the two
Flask services before opening the Songs and Photos pages.

## Implemented features

- Home page, band introduction and navigation.
- Songs from the Songs API, with a Bootstrap lyrics dialog.
- Photos from the Pictures API, with event location and date.
- Validated signup, password hashing and duplicate username checks.
- Login and CSRF-protected POST logout.
- Authenticated concert details and one RSVP per user and concert.
- Attendance updates scoped to the signed-in user; invalid choices rejected.
- Concert and attendance models registered in the Django admin.
- Committed database migrations; unmanaged Song and Photo models describe external data.

## Configuration and administration

Set SONGS_SERVICE_URL and PICTURES_SERVICE_URL to the deployed service endpoints.
Set DJANGO_SECRET_KEY to a private value for a persistent deployment and configure
DJANGO_ALLOWED_HOSTS as a comma-separated list. The lab defaults support localhost
and the course cognitiveclass.ai and appdomain.cloud hosts. No account passwords
or database credentials are committed.

Create an administrator using python manage.py createsuperuser, then visit /admin/.
Registered users can use /concerts/ to update attendance. The container initializes
one sample concert. SQLite data is local to the container; use persistent storage
when data must survive replacement of the pod.

## Container and deployment

```sh
docker build -t djangoserver:1 .
docker run --rm -p 8000:8000 -e SONGS_SERVICE_URL=https://your-songs-route/song -e PICTURES_SERVICE_URL=https://your-pictures-endpoint/picture djangoserver:1
```

Set the image and service URLs in deployment.yml, then apply with
kubectl apply -f deployment.yml. Expose port 8000 through the course application
launcher or an OpenShift route. The entrypoint applies migrations and creates the
sample concert before starting the application. This is a course lab deployment.
