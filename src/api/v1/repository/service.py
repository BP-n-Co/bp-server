from pymysql.err import IntegrityError

from src._config import base_logger
from src._database_pymysql import (
    MysqlClient,
    NoConnectionError,
    NoUpdateValuesError,
    NoValueInsertionError,
)
from src._exceptions import (
    NotFoundException,
    WrongAttributesException,
    AlreadyExistsException,
)
from src._github_api import GithubClient, GithubRequestException
from src.models import Repository


def add_repository(name: str, owner: str) -> Repository:
    # 1. Call Github to get the info about the repo (nodeId)
    github_client = GithubClient(logger=base_logger)
    try:
        repo = github_client.get_repository_info(name=name, owner=owner)
    except GithubRequestException as e:
        github_client.close()
        raise e
    github_client.close()

    # 2. Add in DB
    mysql_client = MysqlClient(logger=base_logger)
    try:
        mysql_client.insert_one(
            table_name=Repository.__tablename__, values=repo.to_dict()
        )
    except NoValueInsertionError | NoConnectionError as e:
        mysql_client.close()
        raise e
    except IntegrityError as e:
        mysql_client.close()
        raise AlreadyExistsException(table_name=Repository.__tablename__, error=e)
    mysql_client.close()

    # 3. Return created one
    return repo
