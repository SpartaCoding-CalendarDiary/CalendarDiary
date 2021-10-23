from os import getenv, environ
from utils import init_json_env

init_json_env()

DATABASES = {
    "username": getenv("DB_USERNAME", None),
    "password": getenv("DB_PASSWORD", None),
    "address": getenv("DB_ADDRESS", None)
}