from fastapi import APIRouter

from _schemas import DataResponse, MessageResponse
from src._database_pymysql import (
    NoConnectionError,
    NoUpdateValuesError,
    NoValueInsertionError,
)
from src._exceptions import (
    HTTPSNotFoundException,
    HTTPWrongAttributesException,
    NotFoundException,
    WrongAttributesException,
)

router = APIRouter(prefix="")
