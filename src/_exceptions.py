from fastapi import HTTPException
from pydantic import BaseModel

from src._config import ENV, ServiceEnv


class HTTPSNotFoundException(HTTPException):
    def __init__(self, error: Exception | None = None):
        detail = f"{type(error)=}, {str(error)=}" if error else None
        super().__init__(status_code=404, detail=detail)


class WrongAttributesException(Exception):
    def __init__(self, table_name: str, error: Exception | None = None):
        detail = f"{type(error)=}, {str(error)=}" if error else None
        super().__init__(f"Invalid data for {table_name=}, {detail}")


class NotFoundException(Exception):
    def __init__(self, table_name: str, error: Exception | None = None):
        detail = f"{type(error)=}, {str(error)=}" if error else None
        super().__init__(f"Not found in {table_name=}, {detail}")


class AlreadyExistsException(Exception):
    def __init__(self, table_name: str, error: Exception | None = None):
        detail = f"{type(error)=}, {str(error)=}" if error else None
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
        super().__init__(status_code=409, detail=details)


class HTTPWrongAttributesException(HTTPException):
    def __init__(self, error: Exception | None = None):
        detail = f"{type(error)=}, {str(error)=}" if error else None
        super().__init__(status_code=400, detail=detail)


class HTTPServerException(HTTPException):
    def __init__(self, error: Exception | None = None):
        detail = None
        if ENV != ServiceEnv.production and error:
            detail = f"{type(error)}, {str(error)}"
        super().__init__(status_code=500, detail=detail)
