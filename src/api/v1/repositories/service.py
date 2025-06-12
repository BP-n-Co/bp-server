import traceback
from datetime import datetime

from pymysql.err import IntegrityError

from _config import DateTimeFormat, base_logger
from _database_pymysql import (
    MysqlClient,
    MySqlNoConnectionError,
    MySqlNoUpdateValuesError,
    MySqlNoValueInsertionError,
    MySqlWrongQueryError,
)
from _exceptions import (
    AlreadyExistsException,
    NotFoundException,
    WrongAttributesException,
)
from _github_api import GithubClient, GithubNoDataResponseError, GithubServerError
from models import Commit, GitUser, Repository


def add_repository(name: str, owner_login: str, branch_name: str) -> dict[str, object]:
    base_logger.debug(
        f"trying to add repository with {name=}, {owner_login=}, {branch_name=}"
    )
    mysql_client = MysqlClient(logger=base_logger)
    github_client = GithubClient(logger=base_logger)

    ## 1. Call Github to get the info about the repo (nodeId)
    # 1.1 Get repo info
    query = f"""
    query {{
        repository(owner: "{owner_login}", name: "{name}") {{ 
            id
            isPrivate
            createdAt
            owner {{
                id
            }}
        }}
    }}
    """
    try:
        repo_info = github_client.graphql_post(query=query)["repository"]
    except (GithubServerError, GithubNoDataResponseError):
        base_logger.warning(
            f"Error while fetching Github with {name=}, {owner_login=}, {traceback.format_exc()}"
        )
        raise
    if not repo_info:
        message = f"could not retreive any repository info for {name=}, {owner_login=}"
        base_logger.warning(message)
        raise WrongAttributesException(message)

    repo = Repository(
        id=repo_info["id"],
        name=name,
        ownerId=repo_info["owner"]["id"],
        isPrivate=repo_info["isPrivate"] == "True",
        createdAt=datetime.strptime(repo_info["createdAt"], DateTimeFormat.github),
    )
    base_logger.debug(f"created object {repo=}")

    # 1.2 Check if branch is valid
    base_logger.debug(f"checking if {branch_name=} is a valid branch")
    query = f"""
    query {{
        repository(owner: "{owner_login}", name: "{name}") {{
            ref(qualifiedName: "refs/heads/{branch_name}") {{
                target {{
                    ... on Commit {{
                        id
                    }}
                }}
            }}
        }}
    }}
    """
    try:
        resp = github_client.graphql_post(query=query)
    except (GithubServerError, GithubNoDataResponseError):
        base_logger.warning(
            f"Error while fetching Github with {name=}, {owner_login=}, {branch_name=}, {traceback.format_exc()}"
        )
        raise
    if not resp["repository"]["ref"]:
        message = (
            f"could not retreive any info with {name=}, {owner_login=}, {branch_name=}"
        )
        base_logger.warning(message)
        raise WrongAttributesException(message)

    repo.trackedBranchName = branch_name
    repo.trackedBranchRef = "refs/heads/" + branch_name
    repo.rootCommitIsReached = False

    ## 2. Add user in DB
    # 2.1 Get user info
    base_logger.debug(f"trying to get github user info from github")
    query = f"""
    query {{
        node(id: "{str(repo.ownerId)}") {{
            ... on User {{
                avatarUrl
                email
                name
                login
            }}
        }}
    }}
    """
    try:
        user_info = github_client.graphql_post(query=query)["node"]
    except (GithubServerError, GithubNoDataResponseError):
        base_logger.warning(
            f"Error while fetching Github with {repo.ownerId=}, {traceback.format_exc()}"
        )
        raise
    if not user_info:
        message = f"could not retreive any user info for {repo.ownerId=}"
        base_logger.warning(message)
        raise WrongAttributesException(message)
    github_user = GitUser(
        id=str(repo.ownerId),
        avatarUrl=user_info["avatarUrl"],
        email=user_info["email"],
        name=user_info["name"],
        login=user_info["login"],
    )
    base_logger.debug(f"got {github_user=}")

    # 2.2 Add user if not present
    base_logger.debug(f"adding github user in database")
    try:
        if not mysql_client.id_exists(
            table_name=GitUser.__tablename__, id=str(github_user.id)
        ):
            mysql_client.insert_one(
                table_name=GitUser.__tablename__, values=github_user.to_dict()
            )
    except (
        MySqlNoConnectionError,
        MySqlWrongQueryError,
        MySqlNoValueInsertionError,
    ):
        base_logger.warning(
            f"Error when adding {github_user=} to bd {traceback.format_exc()}"
        )
        raise
    base_logger.debug(f"successfuly added / updated {github_user=}")

    # 3. Add repo in DB
    base_logger.debug(f"trying to add {repo=} in db, {repo=}")
    try:
        mysql_client.insert_one(
            table_name=Repository.__tablename__, values=repo.to_dict()
        )
    except (
        MySqlNoValueInsertionError,
        MySqlNoConnectionError,
        MySqlWrongQueryError,
    ):
        base_logger.warning(
            f"Error when adding {repo=} to db, {traceback.format_exc()}"
        )
        raise
    except IntegrityError as e:
        raise AlreadyExistsException(table_name=Repository.__tablename__, detail=str(e))
    base_logger.debug(f"successfully added to db {repo=}")

    # 4. Return created one
    return repo.to_dict()


def get_commits(repo_id: str) -> list[dict[str, object]]:
    base_logger.debug(f"fetching commits of {repo_id=}")
    mysql_client = MysqlClient(logger=base_logger)

    try:
        commits = mysql_client.select(
            table_name=Commit.__tablename__,
            select_col=[
                "id",
                "additions",
                "deletions",
                "committedDate",
                "authorAvatarUrl",
                "authorName",
            ],
            cond_eq={"repositoryId": repo_id},
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError):
        base_logger.warning(
            f"Error when fetching commits from db for {repo_id=}, {traceback.format_exc()}"
        )
        raise
    base_logger.debug(f"got commits for {repo_id=} from db, {commits=}")

    return [c for c in commits]


def get_repositories() -> list[dict[str, object]]:
    base_logger.debug(f"fetching repositories from db")
    mysql_client = MysqlClient(logger=base_logger)

    try:
        repos = mysql_client.select(
            table_name=Repository.__tablename__, select_col=["id", "ownerId", "name"]
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError):
        base_logger.warning(
            f"Error when fetching db for repositories, {traceback.format_exc()}"
        )
        raise
    base_logger.debug(f"got repositories from db, {repos=}")

    for repo in repos:
        base_logger.debug(f"fetching user from db for {repo=}")
        try:
            owner = mysql_client.select_by_id(
                table_name=GitUser.__tablename__,
                id=str(repo["ownerId"]),
                select_col=["login"],
            )
        except (MySqlNoConnectionError, MySqlWrongQueryError):
            base_logger.warning(
                f"Error when fetching db for github user, {traceback.format_exc()}"
            )
            raise
        repo["ownerLogin"] = owner["login"]
        base_logger.debug(f"got user from db for {repo=}")

    base_logger.debug(f"final info for repositories from db, {repos=}")
    return [r for r in repos]
