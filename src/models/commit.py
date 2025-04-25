from sqlalchemy import VARCHAR, Column

from src._models import BaseModel


class Commit(BaseModel):
    __tablename__ = "commit"

    id = Column(VARCHAR(38), primary_key=True)
