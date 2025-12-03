"""add_worker_request_table

Revision ID: 26234d7ab517
Revises: d3e881a2b95c
Create Date: 2025-12-03 17:33:42.220584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26234d7ab517'
down_revision: Union[str, Sequence[str], None] = 'd3e881a2b95c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS worker_request (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            cafe_id VARCHAR(36) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (cafe_id) REFERENCES cafe(id) ON DELETE CASCADE,
            UNIQUE(user_id, cafe_id)
        )
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_worker_request_cafe_status 
        ON worker_request(cafe_id, status)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_worker_request_user 
        ON worker_request(user_id)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_worker_request_user")
    op.execute("DROP INDEX IF EXISTS idx_worker_request_cafe_status")
    op.execute("DROP TABLE IF EXISTS worker_request")
