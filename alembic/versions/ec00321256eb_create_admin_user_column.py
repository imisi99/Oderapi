"""Create admin user column

Revision ID: ec00321256eb
Revises: 
Create Date: 2024-02-01 14:57:12.676861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec00321256eb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('User', sa.Column('role', sa.String(), nullable= True))


def downgrade() -> None:
    op.drop_column('User', 'role')
