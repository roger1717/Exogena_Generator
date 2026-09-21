"""Agregar tipo_regla a mapping_rules

Revision ID: 0003_add_tipo_regla
Revises: c264b0c252f2
Create Date: 2026-09-21

Clasifica las reglas existentes según el prefijo del PUC:
  - 2365xx / 2368xx  → 'retencion'
  - 5xxxxx           → 'gasto'
  - resto            → 'exogena'
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '0003_add_tipo_regla'
down_revision: Union[str, None] = 'c264b0c252f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agregar columna
    op.add_column(
        'mapping_rules',
        sa.Column(
            'tipo_regla',
            sa.String(20),
            nullable=True,
            server_default='retencion',
        )
    )

    # 2. Índice para búsquedas por tipo
    op.create_index(
        'ix_mapping_rules_tipo_regla',
        'mapping_rules',
        ['tipo_regla'],
    )

    # 3. Backfill: clasificar reglas existentes según prefijo del PUC
    op.execute("""
        UPDATE mapping_rules
        SET tipo_regla = CASE
            WHEN puc_code LIKE '2365%' THEN 'retencion'
            WHEN puc_code LIKE '2368%' THEN 'retencion'
            WHEN puc_code LIKE '5%'    THEN 'gasto'
            ELSE 'exogena'
        END
    """)


def downgrade() -> None:
    op.drop_index('ix_mapping_rules_tipo_regla', table_name='mapping_rules')
    op.drop_column('mapping_rules', 'tipo_regla')