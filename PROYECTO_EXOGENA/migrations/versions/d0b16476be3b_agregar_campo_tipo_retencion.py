"""Agregar campo tipo_retencion

Revision ID: d0b16476be3b
Revises: 0339e1a1e5e8
Create Date: 2026-08-22 11:56:43.400392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0b16476be3b'
down_revision: Union[str, Sequence[str], None] = '0339e1a1e5e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar campo tipo_retencion a la tabla retenciones"""
    op.add_column('retenciones', sa.Column('tipo_retencion', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Eliminar campo tipo_retencion de la tabla retenciones"""
    op.drop_column('retenciones', 'tipo_retencion')
