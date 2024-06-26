"""Added users.logged_as

Revision ID: 54a4e7811a89
Revises: 29b3114580d8
Create Date: 2024-06-01 16:10:22.112265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "54a4e7811a89"
down_revision: Union[str, None] = "29b3114580d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("logged_as", sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "logged_as")
    # ### end Alembic commands ###
