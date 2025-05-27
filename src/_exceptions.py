from fastapi import HTTPException
from pydantic import BaseModel

from _config import ENV, ServiceEnv


class HTTPSNotFoundException(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=404, detail=detail)


class WrongAttributesException(Exception):
    pass


class NotFoundException(Exception):
    def __init__(self, table_name: str, detail: str | None = None):
        super().__init__(f"Not found in {table_name=}, {detail}")


class AlreadyExistsException(Exception):
    def __init__(self, table_name: str, detail: str | None = None):
        super().__init__(f"Already exists in {table_name=}, {detail}")


class HTTPSqlmodelAlreadyExistsException(HTTPException):
    def __init__(
        self, entity_name: str, entity_bm: BaseModel, detail: str | None = None
    ):
        message = f"{entity_name} already exists"
        entity = entity_bm.model_dump(exclude_unset=True)
        details = {"message": message, "entity": entity}
        if ENV != ServiceEnv.production and detail:
            details.update({"detail": detail})
        super().__init__(status_code=409, detail=str(details))


class HTTPWrongAttributesException(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(status_code=400, detail=detail)


class HTTPServerException(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=500, detail=detail if ENV != ServiceEnv.production else None
        )
