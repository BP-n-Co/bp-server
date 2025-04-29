from sqlalchemy import VARCHAR, Column

from src._models import BaseModel


class GitUser(BaseModel):
    __tablename__ = "git_user"

    id = Column(VARCHAR(255), primary_key=True)

    avatarUrl = Column(VARCHAR(4096), nullable=True, server_default=None)
    email = Column(VARCHAR(255), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    login = Column(VARCHAR(255), nullable=False)
    oldId = Column(VARCHAR(255), nullable=True, server_default=None)
