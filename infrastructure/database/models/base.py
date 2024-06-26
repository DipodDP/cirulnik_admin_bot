import datetime

from sqlalchemy import BIGINT, TIMESTAMP, ForeignKey, Integer, String
# from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import func
from typing_extensions import Annotated

# integer primary key
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

# string column with length 128
str_128 = Annotated[str, mapped_column(String(128))]

# Users ForeignKey
user_fk = Annotated[
    int, mapped_column(BIGINT, ForeignKey("users.user_id", ondelete="CASCADE"))
]


class Base(DeclarativeBase):
    pass


class TableNameMixin(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
