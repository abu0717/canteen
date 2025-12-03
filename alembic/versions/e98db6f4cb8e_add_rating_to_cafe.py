"""add_rating_to_cafe

Revision ID: e98db6f4cb8e
Revises: 6122040f3967
Create Date: 2025-12-03 15:15:41.756599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e98db6f4cb8e'
down_revision: Union[str, Sequence[str], None] = '6122040f3967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add rating column to cafe table with default value of 4.0
    op.add_column('cafe', sa.Column('rating', sa.Float(), nullable=True, server_default='4.0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove rating column from cafe table
    op.drop_column('cafe', 'rating')
