from pymysql.err import IntegrityError

from src._config import base_logger
from src._database_pymysql import (
    MysqlClient,
    MySqlNoConnectionError,
    MySqlNoUpdateValuesError,
    MySqlNoValueInsertionError,
    MySqlWrongQueryError,
)
from src._exceptions import (
    AlreadyExistsException,
    NotFoundException,
    WrongAttributesException,
)
from src._github_api import (
    GithubClient,
    GithubRequestException,
    GithubWrongAttributesException,
)
from src.models import GitUser, Repository


def add_repository(name: str, owner: str) -> Repository:
    mysql_client = MysqlClient(logger=base_logger)
    github_client = GithubClient(logger=base_logger)

    def quit():
        mysql_client.close()
        github_client.close()

    # 1. Call Github to get the info about the repo (nodeId)
    try:
        repo = github_client.get_repository_info(name=name, owner=owner)
    except (GithubRequestException, GithubWrongAttributesException) as e:
        quit()
        raise e

    # 2. Add user in DB
    # 2.1 Get user info
    try:
        github_user = github_client.get_user_info(id=str(repo.ownerId))
    except (GithubRequestException, GithubWrongAttributesException) as e:
        quit()
        raise e

    # 2.2 Add user if not present
    try:
        existence = mysql_client.select_by_id(
            table_name=GitUser.__tablename__, id=str(github_user.id)
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        quit()
        raise e

    if not existence:
        try:
            mysql_client.insert_one(
                table_name=GitUser.__tablename__, values=github_user.to_dict()
            )
        except (
            MySqlNoValueInsertionError,
            MySqlNoConnectionError,
            MySqlWrongQueryError,
        ) as e:
            quit()
            raise e

    # 3. Add repo in DB

    try:
        mysql_client.insert_one(
            table_name=Repository.__tablename__, values=repo.to_dict()
        )
    except (
        MySqlNoValueInsertionError,
        MySqlNoConnectionError,
        MySqlWrongQueryError,
    ) as e:
        quit()
        raise e
    except IntegrityError as e:
        quit()
        raise AlreadyExistsException(table_name=Repository.__tablename__, detail=str(e))

    quit()
    # 4. Return created one
    return repo
