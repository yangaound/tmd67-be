import os

from .settings import *

ALLOWED_HOSTS = (
    [os.environ["WEBSITE_HOSTNAME"]]
    if "WEBSITE_HOSTNAME" in os.environ
    else []
)

if "ALLOWED_ORIGINS" in os.environ:
    if os.environ["ALLOWED_ORIGINS"] == "*":
        CORS_ALLOW_ALL_ORIGINS = True
    else:
        CSRF_TRUSTED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
        CORS_ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
else:
    CSRF_TRUSTED_ORIGINS = []
    CORS_ALLOWED_ORIGINS = []

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
    # Enables whitenoise for serving static files
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
