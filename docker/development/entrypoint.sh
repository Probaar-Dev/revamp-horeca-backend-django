#!/bin/bash
__probaar="\e[1mprob\e[34mɑ\e[35mɒ\e[97mr\e[0m"
__usage="
${__probaar}'s development environment.

\e[1mUSAGE\e[0m:

  docker compose up                      Starts the development server at
                                         http://localhost:8000
  docker compose run probaar-dev setup   Sets up the development environment.
                                         Should be run at least once.
  docker compose run probaar-dev flush   Drops the development database and migrates it

  docker compose run probaar-dev [cmd]   Runs the 'cmd' command in the container.
                                         (e.g. 'bash', './manage.py shell', etc.)

docker compose run vs docker compose exec:
  The first one is used to run a command in a new container, and rebuilds it
  if necessary. The second one runs the command in an existing and running
  container, but ignoring this entrypoint.
  Since this container uses the host's project directory as a shared volume
  there is no much difference between them. The first one is preferred.
"

# Starts the nvm environment (with Node 14.20.1)
. $NVM_DIR/nvm.sh

case "$1" in
  --help|-h)
    echo -e "$__usage"
    ;;
  setup)
    # Collect the static files, compile the translations and install the panel dependencies
    mkdir -p assets

    # Install the massive-load modules (Carga masiva)
    ./data_load/install_and_build.sh
    # Install the panel dependencies. See .yarnrc
    yarn

    python manage.py collectstatic --no-input
    python manage.py makemessages --all
    python manage.py compilemessages
    ;;
  flush)
    # Drops the development database
    python manage.py flush --no-input
    python manage.py migrate
    ;;
  *)
    exec "$@"
    ;;
esac
