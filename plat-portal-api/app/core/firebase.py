import json
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

from django.conf import settings

# Fetch the service account key JSON file contents
cred = credentials.Certificate(settings.FIRE_BASE_ACCESS_KEY)
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': settings.FIRE_BASE_REAL_TIME_DB_URL
})

# As an admin, the app has access to read and write all data, regardless of Security Rules
ref = db.reference(settings.FIRE_BASE_REF)


def fire_base_set_key_value(key, value):
    ref.update({json.dumps(key): value})
