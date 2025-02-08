"""Add constraints on phone_number column

Revision ID: e9f916cfb6db
Revises: 1675a3ef66cd
Create Date: 2024-02-05 17:05:01.254679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9f916cfb6db'
down_revision: Union[str, None] = '1675a3ef66cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint


def downgrade() -> None:
    pass
