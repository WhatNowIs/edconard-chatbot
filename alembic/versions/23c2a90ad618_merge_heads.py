"""Merge heads

Revision ID: 23c2a90ad618
Revises: a3b4a915521d
Create Date: 2024-07-24 19:07:18.205576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23c2a90ad618'
down_revision = ('9a16c5791d86', 'a3b4a915521d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
