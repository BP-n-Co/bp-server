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
from src._github_api import GithubRequestException, GithubWrongAttributesException
from src.models import Repository

from .schema import RepositoryTrackInput
from .service import add_repository, get_commits

router = APIRouter(prefix="/repositories")


@router.post("", status_code=201, response_model=DataResponse)
def track_repository(repository_input: RepositoryTrackInput) -> DataResponse:
    try:
        repo = add_repository(
            name=repository_input.name,
            owner=repository_input.owner,
            branch_name=repository_input.branch_name,
        )
    except AlreadyExistsException as e:
        raise HTTPSqlmodelAlreadyExistsException(
            entity_name=Repository.__tablename__,
            entity_bm=repository_input,
            detail=str(e),
        )
    except (MySqlNoConnectionError, GithubRequestException, MySqlWrongQueryError) as e:
        raise HTTPServerException(detail=f"{type(e)=}, {str(e)}")
    except (GithubWrongAttributesException, MySqlNoValueInsertionError) as e:
        raise HTTPWrongAttributesException(detail=f"{str(e)}")

    return DataResponse(data=repo)


@router.get("/commits", response_model=DataResponse)
def fetch_commits(name: str, ownerId: str) -> DataResponse:
    try:
        commits = get_commits(name=name, ownerId=ownerId)
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        raise HTTPServerException(detail=f"{type(e)=}, {str(e)}")
    except WrongAttributesException as e:
        raise HTTPWrongAttributesException(detail=str(e))
    return DataResponse(data=commits)
