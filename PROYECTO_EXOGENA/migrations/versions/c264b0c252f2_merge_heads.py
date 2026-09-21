"""merge_heads

Revision ID: c264b0c252f2
Revises: 0001_add_calcula_base_sobre_and_cliente, 2cbd3c8f65a5
Create Date: 2026-09-18 12:49:54.216702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c264b0c252f2'
down_revision: Union[str, Sequence[str], None] = ('0001_add_calcula_base_sobre_and_cliente', '2cbd3c8f65a5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
