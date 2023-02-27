import os

from .settings import *

ALLOWED_HOSTS = (
    os.environ["ALLOWED_HOSTS"].split(",")
    if "ALLOWED_HOSTS" in os.environ
    else []
) + [os.environ.get("WEBSITE_HOSTNAME", "localhost")]


if "ALLOWED_ORIGINS" in os.environ:
    if os.environ["ALLOWED_ORIGINS"] == "*":
        CORS_ALLOW_ALL_ORIGINS = True
    else:
        CSRF_TRUSTED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
        CORS_ORIGIN_WHITELIST = os.environ["ALLOWED_ORIGINS"].split(",")
else:
    CSRF_TRUSTED_ORIGINS = []
    CORS_ORIGIN_WHITELIST = []

CORS_ALLOW_CREDENTIALS = True

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
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
