
# Precise Financial API

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
ex: DATABASE_URL=postgres://financial:123456@postgres:5432/financial
```


## Using Virtualenv
```bash
# 1. Create and activate virtualenv
$ virtualenv venv
$ source ./venv/bin/activate

# 2. Install depencencies
$ pip install poetry==1.6.1
$ poetry install

# 3. Migrate database
$ ./manage.py migrate # using option --database=<name> for multi db

# 4. Migrate db table template
$ ./manage.py migrate_db_table_template

# 5. Start Django
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
    'app.financial.apps.UserConfig',
    'app.APP_NAME',
)

```

## Running App Tenancies
    1. go in to the bash shell of the django app in the docker container
    cmd: docker exec -it <container-django-name> bash
    
    
## Running test App Tenancies Command
    cmd: coverage run --source='.' manage.py test
    
## Command run fake data sale , sale charge and cost and sale items to model
    cmd: python manage.py fake_sale_items --my_int_number <int> --client_id <str>

## Command run fake data sale , sale charge and cost and sale items to file excel
    cmd: python manage.py fake_data_sale_items --path <path_save_file> --n <number_fake>
        - Ex: python manage.py fake_data_sale_items --path D:\\fake-sale-item.xlsx --n 50000
        
## command sync data source
    cmd: python manage.py sync_datasource
        - using --help check infomation
        
## Command sync live feed
    cmd: python manage.py sync_live_feed --client_id <str> --from_date <str> --to_date <str>
        - using --help check infomation

## Merge migrations for app (using when the app have many file migrations)
    step 1: access table django_migrations and clear all migrations relate app
    step 2: run python manage.py migrate <app name> --fake-initial command
    step 3: python manage.py migrate