"""add_scheduled_fields_to_order_item

Revision ID: 1c00d30f3393
Revises: 7d74b8ff6990
Create Date: 2025-12-03 14:08:17.870349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c00d30f3393'
down_revision: Union[str, Sequence[str], None] = '7d74b8ff6990'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
