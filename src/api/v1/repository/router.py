from fastapi import APIRouter
from pymysql.err import IntegrityError

from _schemas import DataResponse, MessageResponse
from src._database_pymysql import (
    NoConnectionError,
    NoUpdateValuesError,
    NoValueInsertionError,
)
from src._exceptions import (
    AlreadyExistsException,
    HTTPServerException,
    HTTPSNotFoundException,
    HTTPSqlmodelAlreadyExistsException,
    HTTPWrongAttributesException,
    NotFoundException,
    WrongAttributesException,
)
from src._github_api import GithubRequestException
from src.models import Repository

from .schema import RepositoryTrackInput
from .service import add_repository

router = APIRouter(prefix="/repositories")


## TODO: error handling
@router.post("", status_code=201, response_model=DataResponse)
def track_repository(repository_input: RepositoryTrackInput) -> DataResponse:
    try:
        resp = add_repository(name=repository_input.name, owner=repository_input.owner)
    except AlreadyExistsException:
        raise HTTPSqlmodelAlreadyExistsException(
            entity_name=Repository.__tablename__, entity_bm=repository_input
        )
    except NoConnectionError | GithubRequestException as e:
        raise HTTPServerException(error=e)
    except NoValueInsertionError as e:
        raise HTTPWrongAttributesException(error=e)

    return DataResponse(data=resp.to_dict())
