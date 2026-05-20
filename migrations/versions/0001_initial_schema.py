"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-20 00:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "alunos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("cpf", sa.String(length=20), nullable=False),
        sa.Column("matricula", sa.String(length=30), nullable=False),
        sa.Column("curso", sa.String(length=120), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf"),
        sa.UniqueConstraint("matricula"),
    )
    op.create_table(
        "professores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("cpf", sa.String(length=20), nullable=False),
        sa.Column("registro", sa.String(length=30), nullable=False),
        sa.Column("area", sa.String(length=120), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf"),
        sa.UniqueConstraint("registro"),
    )
    op.create_table(
        "disciplinas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("codigo", sa.String(length=30), nullable=False),
        sa.Column("carga_horaria", sa.Integer(), nullable=False),
        sa.Column("professor_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_table(
        "matriculas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("removido_em", sa.TIMESTAMP(), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["aluno_id"], ["alunos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplinas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aluno_id", "disciplina_id", name="uk_aluno_disciplina"),
    )

    op.execute(
        """
        INSERT IGNORE INTO professores (nome, cpf, registro, area)
        VALUES ('Mariana Souza', '111.222.333-44', 'PROF001', 'Programacao')
        """
    )
    op.execute(
        """
        INSERT IGNORE INTO alunos (nome, cpf, matricula, curso)
        VALUES
          ('Felipe Santos', '555.666.777-88', '2026001', 'Sistemas de Informacao'),
          ('Ana Lima', '999.888.777-66', '2026002', 'Ciencia da Computacao')
        """
    )
    op.execute(
        """
        INSERT IGNORE INTO disciplinas (nome, codigo, carga_horaria, professor_id)
        SELECT 'Programacao Orientada a Objetos', 'POO101', 80, id
          FROM professores
         WHERE registro = 'PROF001'
        """
    )
    op.execute(
        """
        INSERT IGNORE INTO matriculas (aluno_id, disciplina_id)
        SELECT a.id, d.id
          FROM alunos a
          JOIN disciplinas d ON d.codigo = 'POO101'
         WHERE a.matricula IN ('2026001', '2026002')
        """
    )


def downgrade():
    op.drop_table("matriculas")
    op.drop_table("disciplinas")
    op.drop_table("professores")
    op.drop_table("alunos")
