"""renomeia colunas de app_meta para ingles

Revision ID: 2f49924cd16d
Revises: 18ff5718e626
Create Date: 2026-09-22 22:53:29.850109

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f49924cd16d"
down_revision: str | Sequence[str] | None = "18ff5718e626"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Dois blocos batch: criar a constraint no mesmo bloco do rename faz o Alembic descartá-la.
def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("app_meta") as batch_op:
        batch_op.drop_constraint("uq_app_meta_chave", type_="unique")
        batch_op.alter_column("chave", new_column_name="key")
        batch_op.alter_column("valor", new_column_name="value")
    with op.batch_alter_table("app_meta") as batch_op:
        batch_op.create_unique_constraint(op.f("uq_app_meta_key"), ["key"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("app_meta") as batch_op:
        batch_op.drop_constraint("uq_app_meta_key", type_="unique")
        batch_op.alter_column("key", new_column_name="chave")
        batch_op.alter_column("value", new_column_name="valor")
    with op.batch_alter_table("app_meta") as batch_op:
        batch_op.create_unique_constraint(op.f("uq_app_meta_chave"), ["chave"])
