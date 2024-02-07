"""Fixing phone column

Revision ID: e694b4417292
Revises: e9f916cfb6db
Create Date: 2024-02-07 16:54:26.708711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData

# revision identifiers, used by Alembic.
revision: str = 'e694b4417292'
down_revision: Union[str, None] = 'e9f916cfb6db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("PRAGMA foreign_keys=OFF")

    op.execute("BEGIN TRANSACTION")

    meta = MetaData()
    meta.reflect(bind=op.get_bind())

    op.execute("ALTER TABLE user RENAME TO Backup")

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key= True, index= True),
        sa.Column('first_name', sa.String(), nullable= False),
        sa.Column('last_name', sa.String(), nullable= False),
        sa.Column('email', sa.String(), nullable= False, unique= True),
        sa.Column('username', sa.String(15), nullable= False, unique= True),
        sa.Column('password', sa.String(), nullable= False),
        sa.Column('phone_number', sa.String(20), nullable= False, unique= True)
    )

    op.execute("INSERT INTO users SELECT * FROM Backup")

    op.execute("DROP TABLE Backup")

    op.execute("COMMIT")

    op.execute("PRAGMA foreign_keys=OFF")



def downgrade() -> None:
    pass
