"""empty message

Revision ID: e6fe48981b7d
Revises: 9cc52d49ac0e
Create Date: 2024-03-17 19:05:58.812720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6fe48981b7d'
down_revision: Union[str, None] = '9cc52d49ac0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
