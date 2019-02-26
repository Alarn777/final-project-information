
from os import curdir, sep, os

STATIC_ROOT = os.path.join(BASE_DIR,"deploy_to_server")
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)