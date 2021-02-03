"""File that will setup the environment variables when the
application is running on Heroku."""

import environ
from learning_log.settings.base import *

env = environ.Env()

DEBUG = env.bool("DEBUG", False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
