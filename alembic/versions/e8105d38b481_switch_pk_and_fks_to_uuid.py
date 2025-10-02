"""switch pk and fks to uuid

Revision ID: e8105d38b481
Revises: db3350a37923
Create Date: 2025-09-29 22:27:13.196768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e8105d38b481'
down_revision: Union[str, Sequence[str], None] = 'db3350a37923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Destructive upgrade: rebuild tables with UUID primary/foreign keys."""
    # Drop FKs first if exist
    conn = op.get_bind()
    # Drop tables (cascade)
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS bookings CASCADE")
    op.execute("DROP TABLE IF EXISTS services CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    # Ensure pgcrypto for gen_random_uuid if needed
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Create users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.VARCHAR(length=255), nullable=False),
        sa.Column('email', sa.VARCHAR(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=False),
        sa.Column('role', sa.VARCHAR(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Create services
    op.create_table(
        'services',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.VARCHAR(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Create bookings
    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('services.id'), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Create reviews
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('booking_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bookings.id'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Drop all tables (no safe downgrade)."""
    op.execute("DROP TABLE IF EXISTS reviews CASCADE")
    op.execute("DROP TABLE IF EXISTS bookings CASCADE")
    op.execute("DROP TABLE IF EXISTS services CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
