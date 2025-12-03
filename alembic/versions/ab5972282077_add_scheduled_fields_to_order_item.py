"""add_scheduled_fields_to_order_item

Revision ID: ab5972282077
Revises: 1c00d30f3393
Create Date: 2025-12-03 14:08:51.085842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab5972282077'
down_revision: Union[str, Sequence[str], None] = '1c00d30f3393'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('order_item', sa.Column('scheduled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('order_item', sa.Column('scheduled_time', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('order_item', 'scheduled_time')
    op.drop_column('order_item', 'scheduled')
