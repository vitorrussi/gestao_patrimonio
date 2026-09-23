"""cria entidades do mvp de imoveis

Revision ID: c4db296b64d7
Revises: 227f21e32f86
Create Date: 2026-09-22 23:10:34.842580

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4db296b64d7"
down_revision: str | Sequence[str] | None = "227f21e32f86"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=False),
        sa.Column(
            "property_type",
            sa.Enum(
                "casa",
                "casa_condominio",
                "apartamento",
                "terreno",
                "terreno_condominio",
                "sala_comercial",
                "loja",
                "galpao",
                "predio",
                "chacara_sitio",
                "fazenda",
                "vaga_garagem",
                "box",
                "outro",
                name="property_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "usage",
            sa.Enum(
                "moradia_propria",
                "alugado",
                "vazio",
                "comercial_proprio",
                "em_construcao",
                name="property_usage",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("street", sa.String(length=200), nullable=True),
        sa.Column("number", sa.String(length=20), nullable=True),
        sa.Column("complement", sa.String(length=100), nullable=True),
        sa.Column("neighborhood", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("zip_code", sa.String(length=9), nullable=True),
        sa.Column("registration_number", sa.String(length=50), nullable=True),
        sa.Column("registry_office", sa.String(length=150), nullable=True),
        sa.Column("municipal_registration", sa.String(length=50), nullable=True),
        sa.Column(
            "ownership_percentage_x10000", sa.Integer(), server_default="1000000", nullable=False
        ),
        sa.Column("acquisition_date", sa.Date(), nullable=True),
        sa.Column(
            "acquisition_method",
            sa.Enum(
                "compra",
                "heranca",
                "doacao",
                "construcao",
                "outro",
                name="acquisition_method",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=True,
        ),
        sa.Column("purchase_price_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("itbi_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deed_registration_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint(
            "ownership_percentage_x10000 BETWEEN 0 AND 1000000",
            name=op.f("ck_properties_ownership_range"),
        ),
        sa.CheckConstraint(
            "purchase_price_cents >= 0 AND itbi_cents >= 0 AND deed_registration_cents >= 0",
            name=op.f("ck_properties_acquisition_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_properties_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_properties")),
    )
    with op.batch_alter_table("properties", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_properties_user_id"), ["user_id"], unique=False)

    op.create_table(
        "financings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("lender", sa.String(length=100), nullable=False),
        sa.Column("contract_number", sa.String(length=50), nullable=True),
        sa.Column("financed_amount_cents", sa.Integer(), nullable=False),
        sa.Column(
            "amortization_system",
            sa.Enum(
                "sac",
                "price",
                "outro",
                name="amortization_system",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("annual_interest_rate_x10000", sa.Integer(), nullable=False),
        sa.Column(
            "interest_index",
            sa.Enum(
                "tr",
                "ipca",
                "prefixado",
                "outro",
                name="interest_index",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("term_months", sa.Integer(), nullable=False),
        sa.Column("first_installment_date", sa.Date(), nullable=False),
        sa.Column("due_day", sa.Integer(), nullable=False),
        sa.Column("current_installment_cents", sa.Integer(), nullable=False),
        sa.Column("is_paid_off", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("due_day BETWEEN 1 AND 31", name=op.f("ck_financings_due_day_range")),
        sa.CheckConstraint(
            "financed_amount_cents >= 0 AND current_installment_cents >= 0 "
            "AND annual_interest_rate_x10000 >= 0",
            name=op.f("ck_financings_values_non_negative"),
        ),
        sa.CheckConstraint("term_months > 0", name=op.f("ck_financings_term_positive")),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_financings_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_financings")),
    )
    with op.batch_alter_table("financings", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_financings_property_id"), ["property_id"], unique=False
        )

    op.create_table(
        "market_valuations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("valuation_date", sa.Date(), nullable=False),
        sa.Column("value_cents", sa.Integer(), nullable=False),
        sa.Column(
            "source",
            sa.Enum(
                "estimativa_propria",
                "corretor",
                "laudo",
                "anuncio_similar",
                "outro",
                name="valuation_source",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.CheckConstraint(
            "value_cents >= 0", name=op.f("ck_market_valuations_value_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_market_valuations_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_market_valuations")),
    )
    with op.batch_alter_table("market_valuations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_market_valuations_property_id"), ["property_id"], unique=False
        )

    op.create_table(
        "recurring_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column(
            "expense_type",
            sa.Enum(
                "iptu",
                "condominio",
                "cota_extra",
                "seguro",
                "agua",
                "luz",
                "gas",
                "internet",
                "taxa_lixo",
                "itr",
                "laudemio_foro",
                "manutencao",
                "outro",
                name="expense_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column(
            "frequency",
            sa.Enum(
                "mensal",
                "bimestral",
                "trimestral",
                "semestral",
                "anual",
                "unica",
                name="frequency",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("due_day", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("installment_count", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint(
            "amount_cents >= 0", name=op.f("ck_recurring_expenses_amount_non_negative")
        ),
        sa.CheckConstraint(
            "due_day BETWEEN 1 AND 31", name=op.f("ck_recurring_expenses_due_day_range")
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name=op.f("ck_recurring_expenses_end_after_start"),
        ),
        sa.CheckConstraint(
            "installment_count IS NULL OR installment_count > 0",
            name=op.f("ck_recurring_expenses_installments_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("fk_recurring_expenses_property_id_properties"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recurring_expenses")),
    )
    with op.batch_alter_table("recurring_expenses", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_recurring_expenses_property_id"), ["property_id"], unique=False
        )

    op.create_table(
        "debt_balances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("financing_id", sa.Integer(), nullable=False),
        sa.Column("balance_date", sa.Date(), nullable=False),
        sa.Column("balance_cents", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "balance_cents >= 0", name=op.f("ck_debt_balances_balance_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["financing_id"],
            ["financings.id"],
            name=op.f("fk_debt_balances_financing_id_financings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_debt_balances")),
    )
    with op.batch_alter_table("debt_balances", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_debt_balances_financing_id"), ["financing_id"], unique=False
        )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recurring_expense_id", sa.Integer(), nullable=True),
        sa.Column("financing_id", sa.Integer(), nullable=True),
        sa.Column("reference_due_date", sa.Date(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount_paid_cents", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "(recurring_expense_id IS NULL) <> (financing_id IS NULL)",
            name=op.f("ck_payments_exactly_one_source"),
        ),
        sa.CheckConstraint("amount_paid_cents >= 0", name=op.f("ck_payments_amount_non_negative")),
        sa.ForeignKeyConstraint(
            ["financing_id"],
            ["financings.id"],
            name=op.f("fk_payments_financing_id_financings"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recurring_expense_id"],
            ["recurring_expenses.id"],
            name=op.f("fk_payments_recurring_expense_id_recurring_expenses"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
        sa.UniqueConstraint(
            "financing_id", "reference_due_date", name=op.f("uq_payments_financing_id")
        ),
        sa.UniqueConstraint(
            "recurring_expense_id",
            "reference_due_date",
            name=op.f("uq_payments_recurring_expense_id"),
        ),
    )
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_payments_financing_id"), ["financing_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_payments_recurring_expense_id"), ["recurring_expense_id"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_payments_recurring_expense_id"))
        batch_op.drop_index(batch_op.f("ix_payments_financing_id"))

    op.drop_table("payments")
    with op.batch_alter_table("debt_balances", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_debt_balances_financing_id"))

    op.drop_table("debt_balances")
    with op.batch_alter_table("recurring_expenses", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_recurring_expenses_property_id"))

    op.drop_table("recurring_expenses")
    with op.batch_alter_table("market_valuations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_market_valuations_property_id"))

    op.drop_table("market_valuations")
    with op.batch_alter_table("financings", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_financings_property_id"))

    op.drop_table("financings")
    with op.batch_alter_table("properties", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_properties_user_id"))

    op.drop_table("properties")
