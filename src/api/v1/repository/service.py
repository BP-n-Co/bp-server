from pymysql.err import IntegrityError

from src._config import base_logger
from src._database_pymysql import (
    MysqlClient,
    NoConnectionError,
    NoUpdateValuesError,
    NoValueInsertionError,
)
from src._exceptions import (
    AlreadyExistsException,
    NotFoundException,
    WrongAttributesException,
)
from src._github_api import GithubClient, GithubRequestException
from src.models import GitUser, Repository


def add_repository(name: str, owner: str) -> Repository:
    mysql_client = MysqlClient(logger=base_logger)
    github_client = GithubClient(logger=base_logger)
    # 1. Call Github to get the info about the repo (nodeId)

    try:
        repo = github_client.get_repository_info(name=name, owner=owner)
    except GithubRequestException as e:
        mysql_client.close()
        github_client.close()
        raise e

    # 2. Add user in DB
    # 2.1 Get user info
    try:
        github_user = github_client.get_user_info(id=str(repo.ownerId))
    except GithubRequestException as e:
        mysql_client.close()
        github_client.close()
        raise e

    # 2.2 Add user if not present
    try:
        existence = mysql_client.select(
            table_name=GitUser.__tablename__,
            select_col=["id"],
            cond_eq={"id": str(github_user.id)},
        )
    except NoConnectionError as e:
        mysql_client.close()
        github_client.close()
        raise e

    if not existence:
        try:
            mysql_client.insert_one(
                table_name=GitUser.__tablename__, values=github_user.to_dict()
            )
        except (NoValueInsertionError, NoConnectionError) as e:
            mysql_client.close()
            github_client.close()
            raise e

    # 3. Add repo in DB

    try:
        mysql_client.insert_one(
            table_name=Repository.__tablename__, values=repo.to_dict()
        )
    except (NoValueInsertionError, NoConnectionError) as e:
        mysql_client.close()
        github_client.close()
        raise e
    except IntegrityError as e:
        mysql_client.close()
        github_client.close()
        raise AlreadyExistsException(table_name=Repository.__tablename__, error=e)

    mysql_client.close()
    github_client.close()
    # 4. Return created one
    return repo
