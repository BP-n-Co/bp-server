from datetime import datetime
from logging import Logger

from requests import Session

from src._config import GITHUB_TOKEN
from src.models import Repository


class GithubRequestException(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(f"Error when requesting Github Api, {detail}")


class GithubClient:
    def __init__(self, logger: Logger | None = None, token: str | None = None) -> None:
        self.logger = logger
        self.session = Session()
        self.token = token if token else GITHUB_TOKEN
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"

    def close(self):
        self.session.close()

    def graphql_post(self, query: str) -> dict:
        headers = {"Authorization": f"token {self.token}"}
        resp = self.session.post(
            url="https://api.github.com/graphql", headers=headers, json={"query": query}
        )
        if not resp.status_code == 200:
            raise GithubRequestException(
                detail=f"could not get response from Github {resp.status_code=}."
            )
        try:
            resp_dict = resp.json()
        except Exception as e:
            raise GithubRequestException(
                detail=f"could not serialized Github response : {type(e)=}, {str(e)=}."
            )
        if not isinstance(resp_dict, dict) or "data" not in resp_dict:
            raise GithubRequestException(
                detail=f"got response without data : {str(resp_dict)=}"
            )
        return resp_dict["data"]

    def get_repository_info(self, name: str, owner: str) -> Repository:
        query = f"""
        query {{
            repository(owner: "{owner}", name: "{name}") {{ 
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
            repo_info = self.graphql_post(query=query)["repository"]
        except GithubRequestException as e:
            raise e
        if not repo_info:
            raise GithubRequestException(
                detail=f"could not retreive any info for {name=}, {owner=}"
            )
        repo_id = repo_info["id"]
        is_private = repo_info["isPrivate"] == "True"
        created_at = datetime.strptime(repo_info["createdAt"], self.date_format)
        owner_id = repo_info["owner"]["id"]
        repo = Repository(
            id=repo_id,
            name=name,
            ownerId=owner_id,
            isPrivate=is_private,
            createdAt=created_at,
        )
        return repo
