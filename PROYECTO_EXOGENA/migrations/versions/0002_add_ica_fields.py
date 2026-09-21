
from alembic import op
import sqlalchemy as sa

# Manten los identificadores que Alembic generó en tu archivo
revision = '0001_add_calcula_base_sobre_and_cliente'
down_revision = '0339e1a1e5e8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'mapping_rules',
        sa.Column(
            'calcula_base_sobre',
            sa.String(10),
            nullable=True,
            server_default='valor',
        ),
    )
    op.add_column(
        'mapping_rules',
        sa.Column('cliente', sa.String(50), nullable=True),
    )
    op.create_index('ix_mapping_rules_cliente', 'mapping_rules', ['cliente'])


def downgrade():
    op.drop_index('ix_mapping_rules_cliente', table_name='mapping_rules')
    op.drop_column('mapping_rules', 'cliente')
    op.drop_column('mapping_rules', 'calcula_base_sobre')