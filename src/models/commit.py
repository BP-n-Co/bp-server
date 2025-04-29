from sqlalchemy import DATETIME, INTEGER, VARCHAR, Column, ForeignKey

from src._models import BaseModel

from .git_user import GitUser
from .repository import Repository


class Commit(BaseModel):
    __tablename__ = "commit"

    id = Column(VARCHAR(255), primary_key=True)

    repositoryId = Column(VARCHAR(255), ForeignKey(Repository.id), nullable=False)

    addition = Column(INTEGER(), nullable=False, server_default="0")
    deletion = Column(INTEGER(), nullable=False, server_default="0")

    authoredDate = Column(DATETIME(), nullable=False)
    authorAvatarUrl = Column(VARCHAR(4096), nullable=True, server_default=None)
    authorEmail = Column(VARCHAR(255), nullable=False)
    authorId = Column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=True,
        server_default=None,
    )
    authorName = Column(VARCHAR(255), nullable=False)

    committedDate = Column(DATETIME(), nullable=False)
    committerAvatarUrl = Column(VARCHAR(4096), nullable=True, server_default=None)
    committerEmail = Column(VARCHAR(255), nullable=False)
    committerId = Column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=True,
        server_default=None,
    )
    committerName = Column(VARCHAR(255), nullable=False)
