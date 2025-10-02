"""fix_created_at_field

Revision ID: 962087997a14
Revises: 2367c6ec594f
Create Date: 2025-10-01

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '962087997a14'
down_revision = '2367c6ec594f'  # Replace with your previous revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First update any NULL names with a default value
    op.execute("UPDATE services SET name = 'Unnamed Service' WHERE name IS NULL")
    
    # Then update any NULL created_at values
    op.execute("UPDATE services SET created_at = NOW() WHERE created_at IS NULL")
    
    # Now we can safely make the columns NOT NULL
    op.alter_column('services', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('services', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               nullable=False)


def downgrade() -> None:
    # Make columns nullable again if needed
    op.alter_column('services', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('services', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               nullable=True)
