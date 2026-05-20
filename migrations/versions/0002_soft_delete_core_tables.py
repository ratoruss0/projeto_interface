"""soft delete core tables

Revision ID: 0002_soft_delete_core_tables
Revises: 0001_initial_schema
Create Date: 2026-05-20 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "0002_soft_delete_core_tables"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    for table_name in ("alunos", "professores", "disciplinas"):
        op.add_column(
            table_name,
            sa.Column(
                "ativo",
                sa.Boolean(),
                server_default=sa.text("1"),
                nullable=False,
            ),
        )
        op.add_column(table_name, sa.Column("removido_em", sa.TIMESTAMP(), nullable=True))


def downgrade():
    for table_name in ("disciplinas", "professores", "alunos"):
        op.drop_column(table_name, "removido_em")
        op.drop_column(table_name, "ativo")
