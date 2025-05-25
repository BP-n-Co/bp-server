from datetime import datetime

from sqlalchemy import BOOLEAN, DATETIME, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from _models import BaseModel

from .git_user import GitUser


class Repository(BaseModel):
    __tablename__ = "repository"

    id: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)
    oldId: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=True, server_default=None, index=True
    )
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    createdAt: Mapped[datetime] = mapped_column(DATETIME(), nullable=False, index=True)
    rootCommitIsReached: Mapped[bool] = mapped_column(
        BOOLEAN(), nullable=False, server_default="0", index=True
    )
    isPrivate: Mapped[bool] = mapped_column(BOOLEAN(), nullable=False)

    trackedBranchName: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    trackedBranchRef: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    ownerId: Mapped[str] = mapped_column(
        VARCHAR(255),
        ForeignKey(GitUser.id),
        index=True,
        nullable=False,
        server_default=None,
    )
