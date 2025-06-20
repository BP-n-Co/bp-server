from pydantic import BaseModel


class RepositoryTrackInput(BaseModel):
    owner: str
    name: str
    branch: str
