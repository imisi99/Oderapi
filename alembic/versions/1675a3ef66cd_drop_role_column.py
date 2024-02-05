"""Drop role column

Revision ID: 1675a3ef66cd
Revises: 5cab25d5d5c4
Create Date: 2024-02-05 16:39:23.726584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1675a3ef66cd'
down_revision: Union[str, None] = '5cab25d5d5c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user", "role")


def downgrade() -> None:
    pass
