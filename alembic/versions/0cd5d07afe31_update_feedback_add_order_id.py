"""update_feedback_add_order_id

Revision ID: 0cd5d07afe31
Revises: 06dc5e79fce3
Create Date: 2025-12-03 17:08:08.835814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cd5d07afe31'
down_revision: Union[str, Sequence[str], None] = '06dc5e79fce3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing feedback table
    op.execute("DROP TABLE IF EXISTS feedback")
    
    # Recreate with order_id column
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


def downgrade() -> None:
    """Downgrade schema."""
    # Drop and recreate without order_id
    op.execute("DROP TABLE IF EXISTS feedback")
    
    op.execute("""
        CREATE TABLE feedback (
            id VARCHAR(36) PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            comment TEXT NOT NULL,
            rating REAL DEFAULT 1.0,
            cafe_id VARCHAR(36) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE
        )
    """)
