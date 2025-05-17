from fastapi import APIRouter

from _database_pymysql import (
    MySqlNoConnectionError,
    MySqlNoUpdateValuesError,
    MySqlNoValueInsertionError,
    MySqlWrongQueryError,
)
from _exceptions import (
    AlreadyExistsException,
    HTTPServerException,
    HTTPSNotFoundException,
    HTTPSqlmodelAlreadyExistsException,
    HTTPWrongAttributesException,
    NotFoundException,
    WrongAttributesException,
)
from _github_api import GithubNoDataResponseError, GithubServerError
from _schemas import DataResponse, MessageResponse

router = APIRouter(prefix="/template")
