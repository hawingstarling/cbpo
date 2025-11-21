
# Django Template API

## Prerequisites
- Python 3.6 (Ignore if using Docker)
- Virtualenv (Ignore if using Docker)
- Postgres 9.6 + (Ignore if using Docker)
- Docker (Optional)
- Docker Compose (Optional)

## Installation

```bash
# 1. Clone source code
- CD to project folder

# 2. Copy .env.example to ./config/settings/.env
$ cp .env.example ./config/settings/.env

# 3. Edit env files in ./config/settings/.env
ex: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, ...

# 4. Edit DATABASE_URL in ./config/settings/.env from above information
ex: DATABASE_URL=postgres://goldfish:123456@postgres:5432/goldfish
```


## Using Virtualenv
```bash
# 1. Create and activate virtualenv
$ virtualenv venv
$ source ./venv/bin/activate

# 2. Install depencencies
$ pip install -r requirements/local.txt

# 3. Migrate database
$ ./manage.py migrate

# 4. Start Django
$ ./manage.py runserver 0.0.0.0:8000
```

## Build and Start App using Docker
```bash
# Build
$ docker-compose -f dev.yml build

# Start container
$ docker-compose -d dev.yml up -d

# Stop container
$ docker-compose -f dev.yml down
```

## Create super user
```bash
# 1. SSH to docker container
$ docker exec template_api_django bash
$ ./manage.py createsuperuser

# 2. Enter email, username, password
```

## Django Admin
- URL: http://localhost:8000/admin

## Swagger Document
- URL: http://localhost:8000/docs

## API Authentication
- Both OAuth2 and Auth Token are supported

## Create OAuth2 Application
- Login to Django Admin
- Click Application to create new application
    + Choose an User
    + Client type: public
    + Authorization Grant type: Resource owner password-based
    + Enter application name
    + Save

## Oauth2 API
- URL: http://localhost:8000/v1/o/token/
- Method: POST
- Example

<img src="./docs/images/oauth2.png">


## Create new App

```bash
# 1. SSH to API Container
$ docker exec -ti <CONTAINER ID|NAME> bash

# 2. Create new app folder
$ mkdir -p app/[APP_NAME]

# 3. Create new app
$ ./manage.py startapp [APP_NAME] app/[APP_NAME]

# 4. Update your app name in app config in app/[APP_NAME]/apps.py

name = 'app.[APP_NAME]'


# 5. Add new app in config/settings/common
LOCAL_APPS = (
    'app.core.apps.CoreConfig',
    'app.users.apps.UserConfig',
    'app.APP_NAME',
)

```
## Best Practices
- separate into multiple small apps
- Avoid cycle dependency
- Should use UUID for Primary Key

Example

```python
user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

## Running App Tenancies
    1. go in to the bash shell of the django app in the docker container
    cmd: docker exec -it <container-django-name> bash
    
    2. init role data (using basecommand)
    cmd: python manage.py init_role_data
    
    
## Running test App Tenancies Command
    cmd: coverage run --source='.' manage.py test
    
# Permission Migrations

## init permission
python manage.py config_permission

## init access rule
python manage.py config_access_rule

## init custom role
python manage.py config_custom_role

## command migrate permssions of role USER from app tenancies to new app permissions (if first deploy skip this step)
python manage.py sync_permission_from_new_config

## Unit Test
```bash
# All
$ ./manage.py test

# Only App
$ ./manage.py test <app lable>

# Fixtures
$ ./manage.py dumpdata <app_lable> --format 'json' > <path_file_json> # -e for exclude Model of app
```