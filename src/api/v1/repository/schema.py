from pydantic import BaseModel


class RepositoryTrackInput(BaseModel):
    owner: str
    name: str
    branch_name: str


class CommitsFetchInput(BaseModel):
    owner: str
    name: str
