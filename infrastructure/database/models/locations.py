from sqlalchemy import BIGINT, Boolean, ForeignKey, Integer, String, true
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin, TableNameMixin, int_pk, str_128


class Location(Base, TimestampMixin, TableNameMixin):
    """
    Represents a location in the application.

    Attributes:
        location_id (Mapped[int]): The unique identifier of the location.
        location_name (Mapped[str]): The location_name of the location.
        address (Mapped[str]): The full addresss of the location.
        has_solarium (Mapped[bool]): Indicates whether the location has_solarium or not.

    Methods:
        __repr__(): Returns a string representation of the location object.

    Inherited Attributes:
        Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.

    """

    location_id: Mapped[int_pk]
    location_name: Mapped[str] = mapped_column(String(128), unique=True)
    address: Mapped[str_128]
    has_solarium: Mapped[bool] = mapped_column(Boolean, server_default=true())

    users: Mapped[list["UserLocation"]] = relationship(back_populates="location")

    def __repr__(self):
        return f"<Location {self.location_id} {self.location_name} {self.address}>"


class UserLocation(Base, TableNameMixin):
    """
    Represents a Association Table for Many-to-Many relationship between roles and locations.

    Attributes:
        location_id (Mapped[int]): The unique identifier of the location.
        user_id (Mapped[int])

    Methods:
        __repr__(): Returns a string representation of the object.

    Inherited Attributes:
        Inherits from Base and TableNameMixin classes, which provide additional attributes and functionality.

    """

    user_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    location_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("locations.location_id", ondelete="RESTRICT"),
    )

    user: Mapped["User"] = relationship()
    location: Mapped["Location"] = relationship()

    def __repr__(self):
        return f"<UserLocation user_id={self.user_id} location_id={self.location_id}>"
