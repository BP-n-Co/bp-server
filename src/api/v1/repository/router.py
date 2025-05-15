import traceback

from fastapi import APIRouter
from pymysql.err import IntegrityError

from _schemas import DataResponse, MessageResponse
from src._database_pymysql import (
    MySqlNoConnectionError,
    MySqlNoUpdateValuesError,
    MySqlNoValueInsertionError,
    MySqlWrongQueryError,
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
from src._github_api import GithubNoDataResponseError, GithubServerError
from src.models import Repository

from .schema import RepositoryTrackInput
from .service import add_repository, get_commits, get_repositories

router = APIRouter(prefix="/repositories")


@router.get("", response_model=DataResponse)
def fetch_repositories() -> DataResponse:
    try:
        repos = get_repositories()
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.print_exc()}}")
    return DataResponse(data=repos)


@router.post("", status_code=201, response_model=DataResponse)
def track_repository(repository_input: RepositoryTrackInput) -> DataResponse:
    try:
        repo = add_repository(
            name=repository_input.name,
            owner_login=repository_input.owner_login,
            branch_name=repository_input.branch_name,
        )
    except AlreadyExistsException as e:
        raise HTTPSqlmodelAlreadyExistsException(
            entity_name=Repository.__tablename__,
            entity_bm=repository_input,
            detail=str(e),
        )
    except (
        GithubNoDataResponseError,
        GithubServerError,
        MySqlNoConnectionError,
        MySqlWrongQueryError,
    ) as e:
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.print_exc()}}")
    except (MySqlNoValueInsertionError, WrongAttributesException) as e:
        raise HTTPWrongAttributesException(detail=f"{str(e)}")

    return DataResponse(data=repo)


@router.get("/commits", response_model=DataResponse)
def fetch_commits(name: str, ownerId: str) -> DataResponse:
    try:
        commits = get_commits(name=name, ownerId=ownerId)
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.print_exc()}}")
    except WrongAttributesException as e:
        raise HTTPWrongAttributesException(detail=str(e))
    return DataResponse(data=commits)
