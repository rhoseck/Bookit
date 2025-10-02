"""merge_multiple_heads

Revision ID: 699042eb231a
Revises: 962087997a14, 2367c6ec594f
Create Date: 2025-10-01 19:19:57.050914
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '699042eb231a'
down_revision: Union[str, Sequence[str], None] = ('962087997a14', '2367c6ec594f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Update any NULL created_at values with current timestamp
    op.execute("UPDATE services SET created_at = NOW() WHERE created_at IS NULL")
    
    # Drop the existing created_at column and recreate it with proper defaults
    op.drop_column('services', 'created_at')
    op.add_column('services',
        sa.Column('created_at', 
                  sa.DateTime(timezone=True), 
                  server_default=sa.text('NOW()'),
                  nullable=False)
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('services', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               nullable=True,
               server_default=None)
