"""Crear tabla retenciones

Revision ID: 8b0214c204c0
Revises: 002_add_retencion_fields
Create Date: 2026-08-21 09:49:18.675022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b0214c204c0'
down_revision: Union[str, Sequence[str], None] = '002_add_retencion_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
