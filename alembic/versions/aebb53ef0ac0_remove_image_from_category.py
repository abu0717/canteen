"""remove_image_from_category

Revision ID: aebb53ef0ac0
Revises: 9f95edba6137
Create Date: 2025-12-03 16:28:46.552296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aebb53ef0ac0'
down_revision: Union[str, Sequence[str], None] = '9f95edba6137'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support DROP COLUMN, so we need to:
    # 1. Create a new table without the image column
    # 2. Copy data from old table to new table
    # 3. Drop old table
    # 4. Rename new table to old table name
    
    op.execute("""
        CREATE TABLE category_new (
            id VARCHAR(36) PRIMARY KEY,
            cafe_id VARCHAR(36) NOT NULL,
            name VARCHAR NOT NULL,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE
        )
    """)
    
    op.execute("""
        INSERT INTO category_new (id, cafe_id, name)
        SELECT id, cafe_id, name FROM category
    """)
    
    op.execute("DROP TABLE category")
    op.execute("ALTER TABLE category_new RENAME TO category")


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the image column
    op.execute("""
        CREATE TABLE category_new (
            id VARCHAR(36) PRIMARY KEY,
            cafe_id VARCHAR(36) NOT NULL,
            name VARCHAR NOT NULL,
            image VARCHAR,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE
        )
    """)
    
    op.execute("""
        INSERT INTO category_new (id, cafe_id, name, image)
        SELECT id, cafe_id, name, NULL FROM category
    """)
    
    op.execute("DROP TABLE category")
    op.execute("ALTER TABLE category_new RENAME TO category")
