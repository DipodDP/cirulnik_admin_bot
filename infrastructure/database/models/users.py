from typing import Annotated, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy import text, BIGINT, Boolean, true
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from infrastructure.database.models.locations import Location

from .base import Base, TimestampMixin, TableNameMixin, str_128

# Users ForeignKey
user_fk = Annotated[
    int, mapped_column(BIGINT, ForeignKey("users.user_id", ondelete="CASCADE"))
]


class User(Base, TimestampMixin, TableNameMixin):
    """
    Represents a User in the application.

    Attributes:
        user_id (Mapped[int]): The unique identifier of the user.
        username (Mapped[Optional[str]]): The username of the user.
        full_name (Mapped[str]): The full name of the user.
        active (Mapped[bool]): Indicates whether the user is active or not.
        language (Mapped[str]): The language preference of the user.

    Methods:
        __repr__(): Returns a string representation of the User object.

    Inherited Attributes:
        Inherits from Base, TimestampMixin, and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base, TimestampMixin, and TableNameMixin classes, which provide additional functionality.

    """

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str_128]]
    full_name: Mapped[str_128]
    language: Mapped[str] = mapped_column(String(10), server_default=text("'en'"))
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    logged_as: Mapped[Optional[str_128]]

    locations: Mapped[Optional[list['Location']]] = relationship()

    def __repr__(self):
        return f"<User {self.user_id} {self.username} {self.full_name}>"
