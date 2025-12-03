"""added image for category

Revision ID: d202f1409c6f
Revises: e68be7fb0203
Create Date: 2025-12-03 15:56:18.820719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd202f1409c6f'
down_revision: Union[str, Sequence[str], None] = 'e68be7fb0203'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add image column to category table
    op.add_column('category', sa.Column('image', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove image column from category table
    op.drop_column('category', 'image')
