import traceback

from fastapi import APIRouter, Query

from _config import base_logger
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
from models import Repository

from .schema import RepositoryTrackInput
from .service import add_repository, get_commits, get_repositories

router = APIRouter(prefix="/repositories")


@router.get("", response_model=DataResponse)
async def fetch_repositories() -> DataResponse:
    try:
        repos = await get_repositories()
    except Exception as e:
        base_logger.error(
            f"Error while fetching for repositories, {type(e), str(e), {traceback.format_exc()}}"
        )
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.format_exc()}}")
    return DataResponse(data=repos)


@router.post("", status_code=201, response_model=DataResponse)
async def track_repository(repository_input: RepositoryTrackInput) -> DataResponse:
    try:
        repo = await add_repository(
            name=repository_input.name,
            owner_login=repository_input.owner,
            branch_name=repository_input.branch,
        )
    except AlreadyExistsException as e:
        raise HTTPSqlmodelAlreadyExistsException(
            entity_name=Repository.__tablename__,
            entity_bm=repository_input,
            detail=str(e),
        )
    except (MySqlNoValueInsertionError, WrongAttributesException) as e:
        raise HTTPWrongAttributesException(detail=f"{str(e)}")
    except Exception as e:
        base_logger.error(
            f"Error while adding {repository_input=}, {type(e), str(e), {traceback.format_exc()}}"
        )
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.format_exc()}}")

    return DataResponse(data=repo)


@router.get("/commits", response_model=DataResponse)
async def fetch_commits(repo_id: str = Query(...)) -> DataResponse:
    if not repo_id:
        raise HTTPWrongAttributesException(
            detail="repo_id query parameter is required to be not null"
        )
    try:
        commits = await get_commits(repo_id=repo_id)
    except WrongAttributesException as e:
        raise HTTPWrongAttributesException(detail=str(e))
    except Exception as e:
        base_logger.error(
            f"Error while fetching commits of {repo_id=}, {type(e), str(e), {traceback.format_exc()}}"
        )
        raise HTTPServerException(detail=f"{type(e), str(e), {traceback.format_exc()}}")
    return DataResponse(data=commits)
