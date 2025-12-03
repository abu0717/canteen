"""add_image_to_cafe

Revision ID: 6122040f3967
Revises: ab5972282077
Create Date: 2025-12-03 14:51:54.396441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6122040f3967'
down_revision: Union[str, Sequence[str], None] = 'ab5972282077'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cafe', sa.Column('image', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('cafe', 'image')
