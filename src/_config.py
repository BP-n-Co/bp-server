import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

root_path = Path(__file__).resolve()
sys.path.append(str(root_path))

load_dotenv(override=False)

base_logger = logging.getLogger(name="BP_logger")


class ServiceEnv:
    local = "local"
    staging = "staging"
    production = "production"


ENV = os.getenv("ENV", "local")

APP_PORT = int(os.getenv("PORT", 8080))
UVICORN_MODE_DEBUG = bool(os.getenv("UVICORN_MODE_DEBUG", False))

MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
