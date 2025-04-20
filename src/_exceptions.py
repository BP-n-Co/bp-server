from logging import Logger

from fastapi import HTTPException
from pydantic import BaseModel


class HTTPSNotFoundException(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=404, detail=detail)


class WrongAttributesException(Exception):
    def __init__(self, table_name: str, detail: str = ""):
        super().__init__(f"Invalid data for {table_name=}, {detail}")


class NotFoundException(Exception):
    def __init__(self, table_name: str, detail: str = ""):
        super().__init__(f"Not found in {table_name=}, {detail}")


class HTTPSqlmodelAlreadyExistsException(HTTPException):
    def __init__(self, entity_name: str, entity_bm: BaseModel):
        message = f"{entity_name} already exists"
        entity = entity_bm.model_dump(exclude_unset=True)
        detail = {"message": message, "entity": entity}
        super().__init__(status_code=409, detail=detail)


class HTTPWrongAttributesException(HTTPException):
    def __init__(self, detail: str = ""):
        super().__init__(status_code=400, detail=detail)
