PG_USER=$${USERNAME}
PG_DB=$${DATABASE}
BASE=docker-compose -f docker-compose.yml
PROJECT_NAME=whatsapp-scraper

build:
	(. ./set_env.sh && ${BASE} build --no-cache --progress=plain --build-arg ENVIRONMENT_FLAVOR=dev ${c})

start:
	(. ./set_env.sh && ${BASE} up ${c})

down:
	(. ./set_env.sh && ${BASE} down ${c})

shell_django:
	# i.e: `make shell_django`
	(. ./set_env.sh && ${BASE} exec django bash -c 'cd ${PROJECT_NAME} && python manage.py shell')

ssh:
	# c == container's name inside of the `docker-compose` file.
	# i.e: `make ssh c=django`
	(. ./set_env.sh && ${BASE} exec ${c} bash || ${BASE} exec ${c} sh || ${BASE} run ${c} bash)