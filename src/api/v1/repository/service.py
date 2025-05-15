from datetime import datetime

from pymysql.err import IntegrityError

from src._config import DateTimeFormat, base_logger
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
from src._github_api import GithubClient, GithubNoDataResponseError, GithubServerError
from src.models import Commit, GitUser, Repository


def add_repository(name: str, owner_login: str, branch_name: str) -> dict[str, object]:
    mysql_client = MysqlClient(logger=base_logger)
    github_client = GithubClient(logger=base_logger)

    def quit():
        mysql_client.close()
        github_client.close()

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
    except (GithubServerError, GithubNoDataResponseError) as e:
        quit()
        raise e
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

    # 1.2 Check if branch is valid
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
        }}"""
    try:
        resp = github_client.graphql_post(query=query)
    except (GithubServerError, GithubNoDataResponseError) as e:
        quit()
        raise e
    if not resp["repository"]["ref"]:
        raise WrongAttributesException("branch name cannot be found")

    repo.trackedBranchName = branch_name
    repo.trackedBranchRef = "refs/heads/" + branch_name
    repo.rootCommitIsReached = False

    ## 2. Add user in DB
    # 2.1 Get user info
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
        user_info = github_client.graphql_post(query=query)
    except (GithubServerError, GithubNoDataResponseError) as e:
        quit()
        raise e
    if not user_info or not user_info["node"]:
        message = f"could not retreive any user info for {str(repo.ownerId)=}"
        base_logger.warning(message)
        raise WrongAttributesException(message)
    user_info = user_info["node"]
    github_user = GitUser(
        id=str(repo.ownerId),
        avatarUrl=user_info["avatarUrl"],
        email=user_info["email"],
        name=user_info["name"],
        login=user_info["login"],
    )

    # 2.2 Add user if not present
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
    return repo.to_dict()


def get_commits(name: str, ownerId: str) -> list[dict[str, object]]:
    mysql_client = MysqlClient(logger=base_logger)

    def quit():
        mysql_client.close()

    try:
        repo = mysql_client.select(
            table_name=Repository.__tablename__,
            select_col=["id"],
            cond_eq={"name": name, "ownerId": ownerId},
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        quit()
        raise e
    if not repo:
        quit()
        raise WrongAttributesException(
            "cannot fetch any repository, make sure to add it first on the repositories to track"
        )

    repo_id = repo[0]["id"]
    try:
        commits = mysql_client.select(
            table_name=Commit.__tablename__,
            select_col=[
                "additions",
                "deletions",
                "committedDate",
                "committerAvatarUrl",
                "committerEmail",
                "committerName",
            ],
            cond_eq={"repositoryId": repo_id},
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        quit()
        raise e

    quit()
    return [c for c in commits]


def get_repositories() -> list[dict[str, object]]:
    mysql_client = MysqlClient(logger=base_logger)

    def quit():
        mysql_client.close()

    try:
        repos = mysql_client.select(
            table_name=Repository.__tablename__, select_col=["id", "ownerId", "name"]
        )
    except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
        quit()
        raise e
    for repo in repos:
        try:
            owner = mysql_client.select_by_id(
                table_name=GitUser.__tablename__,
                select_col=["login"],
                id=str(repo["ownerId"]),
            )
        except (MySqlNoConnectionError, MySqlWrongQueryError) as e:
            quit()
            raise e
        print(owner)
        repo["ownerLogin"] = owner["login"]
    return [r for r in repos]
