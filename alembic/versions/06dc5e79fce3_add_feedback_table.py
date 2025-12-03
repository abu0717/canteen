"""add_feedback_table

Revision ID: 06dc5e79fce3
Revises: aebb53ef0ac0
Create Date: 2025-12-03 17:04:25.273108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06dc5e79fce3'
down_revision: Union[str, Sequence[str], None] = 'aebb53ef0ac0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE feedback (
            id VARCHAR(36) PRIMARY KEY,
            student_id INTEGER NOT NULL,
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
    op.execute("DROP TABLE feedback")
