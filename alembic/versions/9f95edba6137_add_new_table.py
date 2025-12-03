"""add_new_table

Revision ID: 9f95edba6137
Revises: d202f1409c6f
Create Date: 2025-12-03 16:04:32.969846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f95edba6137'
down_revision: Union[str, Sequence[str], None] = 'd202f1409c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Auto-generated migration had issues with SQLite
    # Skipping problematic ALTER COLUMN and DROP TABLE operations
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Auto-generated migration had issues with SQLite
    pass
