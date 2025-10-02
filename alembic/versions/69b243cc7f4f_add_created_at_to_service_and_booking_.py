"""add created_at to service and booking; standardize role values

Revision ID: 69b243cc7f4f
Revises: d3b4a690817d
Create Date: 2025-09-29 19:26:21.127543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '69b243cc7f4f'
down_revision: Union[str, Sequence[str], None] = 'd3b4a690817d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add created_at to services and bookings only (safe if exists)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_service_cols = {col['name'] for col in inspector.get_columns('services')}
    if 'created_at' not in existing_service_cols:
        op.add_column(
            'services',
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
        )
        op.alter_column('services', 'created_at', server_default=None)

    existing_booking_cols = {col['name'] for col in inspector.get_columns('bookings')}
    if 'created_at' not in existing_booking_cols:
        op.add_column(
            'bookings',
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
        )
        op.alter_column('bookings', 'created_at', server_default=None)


def downgrade() -> None:
    """Downgrade schema: drop created_at columns we added."""
    op.drop_column('bookings', 'created_at')
    op.drop_column('services', 'created_at')
