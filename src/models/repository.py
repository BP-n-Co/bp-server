from sqlalchemy import BOOLEAN, DATETIME, VARCHAR, Column, ForeignKey

from src._models import BaseModel

from .git_user import GitUser


class Repository(BaseModel):
    __tablename__ = "repository"

    id = Column(VARCHAR(255), primary_key=True)

    createdAt = Column(DATETIME(), nullable=False)
    defaultBranchName = Column(VARCHAR(255), nullable=False)
    defaultBranchPrefix = Column(VARCHAR(255), nullable=False)
    isPrivate = Column(BOOLEAN(), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    ownerId = Column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=True,
        server_default=None,
    )
