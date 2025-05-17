from datetime import datetime

from sqlalchemy import DATETIME, INTEGER, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from _models import BaseModel

from .git_user import GitUser
from .repository import Repository


class Commit(BaseModel):
    __tablename__ = "commit"

    id: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)
    oldId: Mapped[str] = mapped_column(VARCHAR(255), nullable=True, server_default=None)

    repositoryId: Mapped[str] = mapped_column(
        VARCHAR(255), ForeignKey(Repository.id), nullable=False
    )

    additions: Mapped[int] = mapped_column(
        INTEGER(), nullable=False, server_default="0"
    )
    deletions: Mapped[int] = mapped_column(
        INTEGER(), nullable=False, server_default="0"
    )

    authoredDate: Mapped[datetime] = mapped_column(DATETIME(), nullable=False)
    authorAvatarUrl: Mapped[str] = mapped_column(
        VARCHAR(4096), nullable=True, server_default=None
    )
    authorEmail: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    authorId: Mapped[str] = mapped_column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=True,
        server_default=None,
    )
    authorName: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    committedDate: Mapped[datetime] = mapped_column(DATETIME(), nullable=False)
    committerAvatarUrl: Mapped[str] = mapped_column(
        VARCHAR(4096), nullable=True, server_default=None
    )
    committerEmail: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    committerId: Mapped[str] = mapped_column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=True,
        server_default=None,
    )
    committerName: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
