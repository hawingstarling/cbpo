from .common import *
DEBUG = env.bool('DEBUG', default=False)

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware', ]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECRET_KEY = env('DJANGO_SECRET_KEY')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default='template-api.hdwebsoft.co')

# DATABASES
# ------------------------------------------------------------------------------
DATABASES['default'] = env.db('DATABASE_URL')  # noqa F405
DATABASES['default']['ATOMIC_REQUESTS'] = True  # noqa F405
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)  # noqa F405
