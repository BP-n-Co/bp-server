from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    def to_dict(
        self,
        exclude_null: bool = False,
        exclude_field: set[str] = set(),
        exclude_id: bool = False,
    ) -> dict[str, object]:
        """
        Convert model attributes to a dictionary.

        Parameters
        ----------
        exclude_null : bool, optional
            If True, exclude attributes with null values. Default is False.
        exclude_field : set[str], optional
            Set of field names to exclude from the dictionary. Default is empty set.
        exclude_id : bool, optional
            If True, exclude the id field from the dictionary. Default is False.

        Returns
        -------
        dict
            A dictionary representation of the model's attributes.
        """
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if (
                not exclude_null
                or getattr(self, c.key) is not None
                and c.key not in exclude_field
                and (c.key != "id" or not exclude_id)
            )
        }
