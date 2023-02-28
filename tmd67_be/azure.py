import os

from .settings import *

ALLOWED_HOSTS = (
    [os.environ["WEBSITE_HOSTNAME"]]
    if "WEBSITE_HOSTNAME" in os.environ
    else []
) + ["localhost"]


if "ALLOWED_ORIGINS" in os.environ:
    CSRF_TRUSTED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
    CORS_ORIGIN_WHITELIST = os.environ["ALLOWED_ORIGINS"].split(",")
    CORS_ALLOW_CREDENTIALS = True
else:
    CSRF_TRUSTED_ORIGINS = []
    CORS_ORIGIN_WHITELIST = []
    CORS_ALLOW_CREDENTIALS = False
    CORS_ORIGIN_ALLOW_ALL = False


hostname = os.environ["DBHOST"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DBNAME"],
        "HOST": hostname + ".postgres.database.azure.com",
        "USER": os.environ["DBUSER"],
        "PASSWORD": os.environ["DBPASS"],
    }
}

# For some database connection types, USER is of the form os.environ['DBUSER'] + "@" + hostname.

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
