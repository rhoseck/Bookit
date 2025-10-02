"""add duration_minutes

Revision ID: <generated_id>
Revises: 2367c6ec594f
Create Date: 2025-10-01
"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic
revision: str = '<generated_id>'
down_revision: Union[str, None] = '2367c6ec594f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add duration_minutes column
    op.add_column('services', sa.Column('duration_minutes', sa.Integer(), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE services SET duration_minutes = 60 WHERE duration_minutes IS NULL")
    
    # Make it not nullable
    op.alter_column('services', 'duration_minutes',
               existing_type=sa.Integer(),
               nullable=False)

def downgrade() -> None:
    op.drop_column('services', 'duration_minutes')
