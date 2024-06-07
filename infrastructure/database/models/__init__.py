"""Import all models and add them to models_list."""

from .base import Base
from .users import User
from .locations import Location

models_list = [
    Base,
    User,
    Location,
]

__all__ = [
    "models_list",
]
