"""views_favorites_remove_unique

Revision ID: 9bf70c1f2e80
Revises: 9d8e33a68675
Create Date: 2024-07-08 00:16:50.165443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bf70c1f2e80'
down_revision: Union[str, None] = '9d8e33a68675'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('favorite_user_id_key', 'favorite', type_='unique')
    op.drop_constraint('view_user_id_key', 'view', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('view_user_id_key', 'view', ['user_id'])
    op.create_unique_constraint('favorite_user_id_key', 'favorite', ['user_id'])
    # ### end Alembic commands ###