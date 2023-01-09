from . import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['ulysselacour.com', 'musik.ulysselacour.com', 'jolify.ulysselacour.com']

CORS_ALLOWED_ORIGINS = [
    "https://ulysselacour.com",
    "https://musik.ulysselacour.com",
    "https://jolify.ulysselacour.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://ulysselacour.com",
    "https://musik.ulysselacour.com",
    "https://jolify.ulysselacour.com",
]
