from typing import Optional

from sqlalchemy import String
from sqlalchemy import INT, Boolean, true
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class Location(Base, TimestampMixin, TableNameMixin):
    """
    This class represents a location in the application.

    Attributes:
        location_id (Mapped[int]): The unique identifier of the location.
        location_name (Mapped[Optional[str]]): The location_name of the location.
        address (Mapped[str]): The full addresss of the location.
        has_solarium (Mapped[bool]): Indicates whether the location has_solarium or not.

    Methods:
        __repr__(): Returns a string representation of the location object.

    Inherited Attributes:
        Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.

    """
    location_id: Mapped[int] = mapped_column(INT, primary_key=True, autoincrement=False)
    location_name: Mapped[Optional[str]] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(128))
    has_solarium: Mapped[bool] = mapped_column(Boolean, server_default=true())

    def __repr__(self):
        return f"<Location {self.location_id} {self.location_name} {self.address}>"
