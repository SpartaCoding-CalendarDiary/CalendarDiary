import json
import pipes
from os import getenv, path, environ

def init_json_env() -> None:
    """
    Initialize the environment with the json file
    """
    try:
        secrets = path.join(path.dirname(path.abspath(__file__)), 'secrets.json')
        with open(secrets, 'r') as json_file:
            for k, v in json.load(json_file).items():
                # print(k, v) # for testing
                environ[k] = str(v)
    except FileNotFoundError:
        return None
