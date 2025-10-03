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
    # This migration is a no-op because the columns were already added in a6563a8da2d3
    # Keeping this migration to maintain consistency in the migration chain
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # This migration is a no-op because the columns were already added in a6563a8da2d3
    # Keeping this migration to maintain consistency in the migration chain
    pass
