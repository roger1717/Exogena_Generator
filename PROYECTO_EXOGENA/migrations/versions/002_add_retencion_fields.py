"""Agregar campos de retención a mapping_rules

Revision ID: 002_add_retencion_fields
Revises: 1ed6953c0420
Create Date: 2026-08-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_retencion_fields'
down_revision: Union[str, None] = '1ed6953c0420'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar campos de retención a la tabla mapping_rules"""
    
    # Agregar columnas para retenciones
    op.add_column('mapping_rules', 
        sa.Column('concepto_retencion', sa.String(10), nullable=True)
    )
    op.add_column('mapping_rules', 
        sa.Column('tarifa_retencion', sa.Numeric(10, 4), nullable=True)
    )
    op.add_column('mapping_rules', 
        sa.Column('tope_minimo', sa.Numeric(15, 2), nullable=True)
    )
    op.add_column('mapping_rules', 
        sa.Column('aplica_iva', sa.Boolean, nullable=True, server_default='false')
    )
    op.add_column('mapping_rules', 
        sa.Column('tipo_retencion', sa.String(20), nullable=True)
    )
    op.add_column('mapping_rules', 
        sa.Column('activo', sa.Boolean, nullable=True, server_default='true')
    )


def downgrade() -> None:
    """Eliminar campos de retención"""
    op.drop_column('mapping_rules', 'concepto_retencion')
    op.drop_column('mapping_rules', 'tarifa_retencion')
    op.drop_column('mapping_rules', 'tope_minimo')
    op.drop_column('mapping_rules', 'aplica_iva')
    op.drop_column('mapping_rules', 'tipo_retencion')
    op.drop_column('mapping_rules', 'activo')