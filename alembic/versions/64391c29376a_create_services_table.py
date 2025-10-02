"""create services table

Revision ID: 64391c29376a
Revises: a6563a8da2d3
Create Date: 2025-09-28 09:52:50.990004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64391c29376a'
down_revision: Union[str, Sequence[str], None] = 'a6563a8da2d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns with safe defaults so migration doesn't fail on existing rows
    op.add_column(
        'services',
        sa.Column(
            'title',
            sa.String(length=100),
            nullable=False,
            server_default="Unnamed Service"
        )
    )
    op.add_column(
        'services',
        sa.Column(
            'price',
            sa.Float(),
            nullable=False,
            server_default="0.0"
        )
    )
    op.add_column(
        'services',
        sa.Column(
            'duration_minutes',
            sa.Integer(),
            nullable=False,
            server_default="30"
        )
    )
    op.add_column(
        'services',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("true")
        )
    )
    op.add_column(
        'services',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        )
    )

    # Drop the old column
    op.drop_column('services', 'name')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'services',
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.drop_column('services', 'created_at')
    op.drop_column('services', 'is_active')
    op.drop_column('services', 'duration_minutes')
    op.drop_column('services', 'price')
    op.drop_column('services', 'title')
