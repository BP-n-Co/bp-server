from pydantic import BaseModel


class RepositoryTrackInput(BaseModel):
    owner_login: str
    name: str
    branch_name: str
