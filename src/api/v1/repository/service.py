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
from src.models import Commit, GitUser, Repository


def add_repository(name: str, owner: str, branch_name: str) -> dict[str, object]:
    mysql_client = MysqlClient(logger=base_logger)
    github_client = GithubClient(logger=base_logger)

    def quit():
        mysql_client.close()
        github_client.close()

    ## 1. Call Github to get the info about the repo (nodeId)
    # 1.1 Get repo info
    try:
        repo = github_client.get_repository_info(name=name, owner=owner)
    except (GithubRequestException, GithubWrongAttributesException) as e:
        quit()
        raise e
    # 1.2 Check if branch is valid
    try:
        query = f"""
            query {{
                repository(owner: "{owner}", name: "{name}") {{
                    ref(qualifiedName: "refs/heads/{branch_name}") {{
                        target {{
                            ... on Commit {{
                                id
                            }}
                        }}
                    }}
                }}
            }}"""
        resp = github_client.graphql_post(query=query)
        if not resp["repository"]["ref"]:
            raise GithubWrongAttributesException("branch name cannot be found")
        repo.trackedBranchName = branch_name
        repo.trackedBranchRef = "refs/heads/" + branch_name
        repo.rootCommitIsReached = False
    except (GithubRequestException, GithubWrongAttributesException) as e:
        quit()
        raise e

    ## 2. Add user in DB
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
