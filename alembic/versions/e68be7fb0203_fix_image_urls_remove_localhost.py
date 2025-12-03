"""fix_image_urls_remove_localhost

Revision ID: e68be7fb0203
Revises: e98db6f4cb8e
Create Date: 2025-12-03 15:36:29.101014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e68be7fb0203'
down_revision: Union[str, Sequence[str], None] = 'e98db6f4cb8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update cafe table - remove localhost prefix from image URLs
    op.execute("""
        UPDATE cafe 
        SET image = REPLACE(image, 'http://localhost:8000', '')
        WHERE image LIKE 'http://localhost:8000%'
    """)
    
    # Update menu_item table - remove localhost prefix from image URLs
    op.execute("""
        UPDATE menu_item 
        SET image = REPLACE(image, 'http://localhost:8000', '')
        WHERE image LIKE 'http://localhost:8000%'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Add localhost prefix back to image URLs
    op.execute("""
        UPDATE cafe 
        SET image = 'http://localhost:8000' || image
        WHERE image LIKE '/uploads/%'
    """)
    
    op.execute("""
        UPDATE menu_item 
        SET image = 'http://localhost:8000' || image
        WHERE image LIKE '/uploads/%'
    """)
