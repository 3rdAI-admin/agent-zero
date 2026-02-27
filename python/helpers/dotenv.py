import os
import re
from typing import Any

from .files import get_abs_path
from dotenv import load_dotenv as _load_dotenv

KEY_AUTH_LOGIN = "AUTH_LOGIN"
KEY_AUTH_PASSWORD = "AUTH_PASSWORD"
KEY_RFC_PASSWORD = "RFC_PASSWORD"
KEY_ROOT_PASSWORD = "ROOT_PASSWORD"


def load_dotenv():
    # Load repo/root .env first (e.g. /a0/.env in Docker, or repo .env on host)
    root_env = get_abs_path(".env")
    if os.path.isfile(root_env):
        _load_dotenv(root_env, override=False)
    # Then load usr/.env so Settings-page saves and volume env win (override=True)
    _load_dotenv(get_dotenv_file_path(), override=True)


def get_dotenv_file_path():
    return get_abs_path("usr/.env")


def get_dotenv_value(key: str, default: Any = None):
    # load_dotenv()
    return os.getenv(key, default)


def save_dotenv_value(key: str, value: str):
    if value is None:
        value = ""
    dotenv_path = get_dotenv_file_path()
    if not os.path.isfile(dotenv_path):
        with open(dotenv_path, "w") as f:
            f.write("")
    with open(dotenv_path, "r+") as f:
        lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if re.match(rf"^\s*{key}\s*=", line):
                lines[i] = f"{key}={value}\n"
                found = True
        if not found:
            lines.append(f"\n{key}={value}\n")
        f.seek(0)
        f.writelines(lines)
        f.truncate()
    load_dotenv()
