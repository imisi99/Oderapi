"""Adding a phone_number Column

Revision ID: 5cab25d5d5c4
Revises: ec00321256eb
Create Date: 2024-02-05 16:28:03.125678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cab25d5d5c4'
down_revision: Union[str, None] = 'ec00321256eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("User", "role")
def downgrade() -> None:
    pass
