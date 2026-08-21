"""Fusionar migraciones de retenciones

Revision ID: e3aae226076d
Revises: xxx_crear_tabla_retenciones, 8b0214c204c0
Create Date: 2026-08-21 11:12:15.747398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3aae226076d'
down_revision: Union[str, Sequence[str], None] = ('xxx_crear_tabla_retenciones', '8b0214c204c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
