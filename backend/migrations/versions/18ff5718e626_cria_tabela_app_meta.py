"""cria tabela app_meta

Revision ID: 18ff5718e626
Revises: 
Create Date: 2026-09-22 20:03:19.669461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18ff5718e626'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


app_meta_table = sa.table(
    "app_meta",
    sa.column("chave", sa.String),
    sa.column("valor", sa.String),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('app_meta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chave', sa.String(length=100), nullable=False),
    sa.Column('valor', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_app_meta')),
    sa.UniqueConstraint('chave', name=op.f('uq_app_meta_chave'))
    )
    op.bulk_insert(app_meta_table, [{"chave": "status", "valor": "ok"}])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('app_meta')
