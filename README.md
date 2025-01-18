# Revamp Horeca Django Project

Backend Service for Probaar HORECA Mobile App.

## Using Docker for development

You can also start a development environment with `docker` and `docker compose` for easy
setup and isolation.

Make sure you have in your .env file
```
APP_ENV="development"
DJANGO_LOG_FILE="django.log"
```

Since this container shares a volume with your host machine (for hot-reloading), you'll need to export your
user and group IDs as environment variables:

```bash
export UID GID
# add it to your .bashrc to avoid running it every time
```

In order to build, bootstrap the database and create a superuser you'll need to run (once):

```bash
# Make sure you set APP_ENV="development" in your .env file
docker compose run --rm probaar-dev setup
```

Now start the development server, and you're good to go:

```bash
docker compose up --build
```

While the container is running, you can run commands inside it, for example:

```bash
# Getting an interactive shell
docker compose exec probaar-revamp-dev bash

# Or running commands directly:
docker compose exec probaar-revamp-dev ./manage.py test

# You might want to run this at least once to create the database and a superuser:
docker compose exec probaar-revamp-dev ./manage.py migrate
docker compose exec probaar-revamp-dev ./manage.py createsuperuser
```
