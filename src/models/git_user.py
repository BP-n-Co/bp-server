from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from _models import BaseModel


class GitUser(BaseModel):
    __tablename__ = "git_user"

    id: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)
    oldId: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=True, server_default=None, index=True
    )

    avatarUrl: Mapped[str] = mapped_column(
        VARCHAR(4096), nullable=True, server_default=None
    )
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=True, server_default=None)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    login: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, index=True)
