BASE=docker-compose -f docker-compose.yml
PROJECT_NAME=whatsapp-scraper

build:
	call .\set_env.bat && $(BASE) build --build-arg ENVIRONMENT_FLAVOR=dev $(c)

start:
	call .\set_env.bat && $(BASE) up $(c)

down:
	call .\set_env.bat && $(BASE) down $(c)

shell_django:
	call .\set_env.bat && $(BASE) exec django bash -c "cd $(PROJECT_NAME) && python manage.py shell"

ssh:
	call .\set_env.bat && $(BASE) exec $(c) bash || $(BASE) exec $(c) sh || $(BASE) run $(c) bash