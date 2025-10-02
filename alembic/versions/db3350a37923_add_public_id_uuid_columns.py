"""add public_id uuid columns

Revision ID: db3350a37923
Revises: 69b243cc7f4f
Create Date: 2025-09-29 20:35:04.493623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db3350a37923'
down_revision: Union[str, Sequence[str], None] = '69b243cc7f4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add public_id UUID columns with defaults and backfill safely."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # users
    user_cols = {c['name'] for c in inspector.get_columns('users')}
    if 'public_id' not in user_cols:
        op.add_column('users', sa.Column('public_id', postgresql.UUID(as_uuid=True), nullable=True))
        # backfill
        op.execute("UPDATE users SET public_id = gen_random_uuid() WHERE public_id IS NULL")
        # enforce not null and unique + index
        op.alter_column('users', 'public_id', nullable=False)
        op.create_index(op.f('ix_users_public_id'), 'users', ['public_id'], unique=True)

    # services
    service_cols = {c['name'] for c in inspector.get_columns('services')}
    if 'public_id' not in service_cols:
        op.add_column('services', sa.Column('public_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.execute("UPDATE services SET public_id = gen_random_uuid() WHERE public_id IS NULL")
        op.alter_column('services', 'public_id', nullable=False)
        op.create_index(op.f('ix_services_public_id'), 'services', ['public_id'], unique=True)

    # bookings
    booking_cols = {c['name'] for c in inspector.get_columns('bookings')}
    if 'public_id' not in booking_cols:
        op.add_column('bookings', sa.Column('public_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.execute("UPDATE bookings SET public_id = gen_random_uuid() WHERE public_id IS NULL")
        op.alter_column('bookings', 'public_id', nullable=False)
        op.create_index(op.f('ix_bookings_public_id'), 'bookings', ['public_id'], unique=True)

    # reviews
    review_cols = {c['name'] for c in inspector.get_columns('reviews')}
    if 'public_id' not in review_cols:
        op.add_column('reviews', sa.Column('public_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.execute("UPDATE reviews SET public_id = gen_random_uuid() WHERE public_id IS NULL")
        op.alter_column('reviews', 'public_id', nullable=False)
        op.create_index(op.f('ix_reviews_public_id'), 'reviews', ['public_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema: drop public_id UUIDs."""
    with op.batch_alter_table('reviews') as b:
        b.drop_index(op.f('ix_reviews_public_id'))
        b.drop_column('public_id')
    with op.batch_alter_table('bookings') as b:
        b.drop_index(op.f('ix_bookings_public_id'))
        b.drop_column('public_id')
    with op.batch_alter_table('services') as b:
        b.drop_index(op.f('ix_services_public_id'))
        b.drop_column('public_id')
    with op.batch_alter_table('users') as b:
        b.drop_index(op.f('ix_users_public_id'))
        b.drop_column('public_id')
