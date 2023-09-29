"""upd user_avatar

Revision ID: 1041a64bd025
Revises: bff426e22fbf
Create Date: 2023-09-28 14:14:10.807667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '1041a64bd025'
down_revision: Union[str, None] = 'bff426e22fbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('user_avatar_link_key', 'user', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('user_avatar_link_key', 'user', ['avatar_link'])
    # ### end Alembic commands ###