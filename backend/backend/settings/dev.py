from . import *

DEBUG = True

INSTALLED_APPS.append(
    "django_nose"
)

TEST_RUNNER =  "django_nose.NoseTestSuiteRunner"

NOSE_ARGS = [
    "--with-coverage",
    "--cover-html",
    "--cover-package=apps"
]

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
