"""add_created_at_to_feedback

Revision ID: d3e881a2b95c
Revises: 0cd5d07afe31
Create Date: 2025-12-03 17:29:09.941235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e881a2b95c'
down_revision: Union[str, Sequence[str], None] = '0cd5d07afe31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ADD COLUMN with constraints easily, so recreate table
    op.execute("DROP TABLE IF EXISTS feedback")
    
    op.execute("""
        CREATE TABLE feedback (
            id VARCHAR(36) PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            order_id INTEGER NOT NULL UNIQUE,
            comment TEXT NOT NULL,
            rating REAL DEFAULT 1.0,
            cafe_id VARCHAR(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS feedback")
    
    op.execute("""
        CREATE TABLE feedback (
            id VARCHAR(36) PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            order_id INTEGER NOT NULL UNIQUE,
            comment TEXT NOT NULL,
            rating REAL DEFAULT 1.0,
            cafe_id VARCHAR(36) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE
        )
    """)
