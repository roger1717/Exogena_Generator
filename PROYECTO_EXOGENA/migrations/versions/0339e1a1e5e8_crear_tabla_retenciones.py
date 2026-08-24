"""Crear tabla retenciones

Revision ID: 0339e1a1e5e8
Revises: 8b0214c204c0
Create Date: 2026-08-21 11:08:50.639397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0339e1a1e5e8'  # Reemplazar con el ID generado
down_revision: Union[str, None] = '002_add_retencion_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear la tabla retenciones"""
    
    op.create_table(
        'retenciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.Column('comprobante', sa.String(length=50), nullable=False),
        sa.Column('nit_tercero', sa.String(length=20), nullable=False),
        sa.Column('nombre_tercero', sa.String(length=255), nullable=False),
        sa.Column('perfil_tributario', sa.String(length=50), nullable=True),
        sa.Column('concepto_contable', sa.String(length=100), nullable=False),
        sa.Column('concepto_dian', sa.String(length=10), nullable=False),
        sa.Column('base_gravable', sa.Numeric(15, 2), nullable=False),
        sa.Column('tarifa', sa.Numeric(10, 4), nullable=False),
        sa.Column('valor_retenido', sa.Numeric(15, 2), nullable=False),
        sa.Column('cuenta_pasivo', sa.String(length=20), nullable=False),
        sa.Column('formato_asignado', sa.String(length=10), nullable=True),
        sa.Column('concepto_exogena', sa.String(length=10), nullable=True),
        sa.Column('periodo', sa.String(length=7), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=True, server_default='procesado'),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices
    op.create_index(op.f('ix_retenciones_id'), 'retenciones', ['id'], unique=False)
    op.create_index(op.f('ix_retenciones_nit_tercero'), 'retenciones', ['nit_tercero'], unique=False)
    op.create_index(op.f('ix_retenciones_periodo'), 'retenciones', ['periodo'], unique=False)
    op.create_index('ix_retenciones_periodo_nit', 'retenciones', ['periodo', 'nit_tercero'], unique=False)
    op.create_index('ix_retenciones_fecha_comprobante', 'retenciones', ['fecha', 'comprobante'], unique=False)


def downgrade() -> None:
    """Eliminar la tabla retenciones"""
    op.drop_index('ix_retenciones_fecha_comprobante', table_name='retenciones')
    op.drop_index('ix_retenciones_periodo_nit', table_name='retenciones')
    op.drop_index(op.f('ix_retenciones_periodo'), table_name='retenciones')
    op.drop_index(op.f('ix_retenciones_nit_tercero'), table_name='retenciones')
    op.drop_index(op.f('ix_retenciones_id'), table_name='retenciones')
    op.drop_table('retenciones')