import os
import re
from io import BytesIO

import sqlite3

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from mysql.connector import Error

from db import IntegrityError, database_label, execute, fetch_all, fetch_one, is_sqlite
from relatorios import gerar_relatorio_json, gerar_relatorio_pdf


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "sistema-academico-dev")

CPF_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")


def form_value(field_name):
    return request.form.get(field_name, "").strip()


def get_dashboard_counts():
    return {
        "alunos": fetch_one("SELECT COUNT(*) AS total FROM alunos")["total"],
        "professores": fetch_one("SELECT COUNT(*) AS total FROM professores")["total"],
        "disciplinas": fetch_one("SELECT COUNT(*) AS total FROM disciplinas")["total"],
        "matriculas": fetch_one(
            "SELECT COUNT(*) AS total FROM matriculas WHERE ativo = 1"
        )["total"],
    }


def get_dados_relatorio_banco():
    alunos = fetch_all(
        """
        SELECT id, nome, cpf, matricula, curso, criado_em
          FROM alunos
         ORDER BY nome
        """
    )
    professores = fetch_all(
        """
        SELECT id, nome, cpf, registro, area, criado_em
          FROM professores
         ORDER BY nome
        """
    )
    disciplinas = fetch_all(
        """
        SELECT d.id, d.nome, d.codigo, d.carga_horaria,
               COALESCE(p.nome, 'Sem professor') AS professor,
               d.criado_em
          FROM disciplinas d
          LEFT JOIN professores p ON p.id = d.professor_id
         ORDER BY d.nome
        """
    )
    matriculas = fetch_all(
        """
        SELECT m.id, a.nome AS aluno, a.matricula,
               d.nome AS disciplina, d.codigo,
               CASE WHEN m.ativo = 1 THEN 'ativa' ELSE 'removida' END AS status,
               m.criado_em, m.removido_em
          FROM matriculas m
          JOIN alunos a ON a.id = m.aluno_id
          JOIN disciplinas d ON d.id = m.disciplina_id
         ORDER BY d.nome, a.nome
        """
    )

    return {
        "banco": database_label(),
        "alunos": alunos,
        "professores": professores,
        "disciplinas": disciplinas,
        "matriculas": matriculas,
    }


@app.errorhandler(Error)
@app.errorhandler(sqlite3.Error)
def handle_database_error(error):
    return render_template("erro.html", error=error), 500


@app.route("/")
def index():
    counts = get_dashboard_counts()
    disciplinas = fetch_all(
        """
        SELECT d.id, d.nome, d.codigo, d.carga_horaria,
               COALESCE(p.nome, 'Sem professor') AS professor,
               COUNT(m.aluno_id) AS total_alunos
          FROM disciplinas d
          LEFT JOIN professores p ON p.id = d.professor_id
          LEFT JOIN matriculas m ON m.disciplina_id = d.id AND m.ativo = 1
         GROUP BY d.id, d.nome, d.codigo, d.carga_horaria, p.nome
         ORDER BY d.nome
        """
    )
    return render_template(
        "index.html",
        counts=counts,
        database_label=database_label(),
        disciplinas=disciplinas,
    )


@app.get("/relatorios/json")
def baixar_relatorio_json():
    conteudo = gerar_relatorio_json(get_dados_relatorio_banco())
    return send_file(
        BytesIO(conteudo.encode("utf-8")),
        mimetype="application/json",
        as_attachment=True,
        download_name="relatorio_academico.json",
    )


@app.get("/relatorios/pdf")
def baixar_relatorio_pdf():
    conteudo = gerar_relatorio_pdf(get_dados_relatorio_banco())
    return send_file(
        BytesIO(conteudo),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="relatorio_academico.pdf",
    )


@app.route("/alunos", methods=["GET", "POST"])
def alunos():
    if request.method == "POST":
        nome = form_value("nome")
        cpf = form_value("cpf")
        matricula = form_value("matricula")
        curso = form_value("curso")

        if not nome:
            flash("Nome obrigatório.", "warning")
            return redirect(url_for("alunos"))
        if len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
            return redirect(url_for("alunos"))
        if not cpf:
            flash("CPF obrigatório.", "warning")
            return redirect(url_for("alunos"))
        if not CPF_PATTERN.fullmatch(cpf):
            flash("CPF deve estar no formato 000.000.000-00.", "warning")
            return redirect(url_for("alunos"))
        if not matricula:
            flash("Matrícula obrigatória.", "warning")
            return redirect(url_for("alunos"))
        if not curso:
            flash("Curso obrigatório.", "warning")
            return redirect(url_for("alunos"))

        try:
            execute(
                """
                INSERT INTO alunos (nome, cpf, matricula, curso)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    nome,
                    cpf,
                    matricula,
                    curso,
                ),
            )
            flash("Aluno cadastrado com sucesso.", "success")
        except IntegrityError:
            flash("Ja existe aluno com este CPF ou matricula.", "warning")
        return redirect(url_for("alunos"))

    pesquisa = request.args.get("pesquisa", "").strip()
    filtro_nome = ""
    params = ()
    if pesquisa:
        if is_sqlite():
            filtro_nome = "WHERE LOWER(a.nome) LIKE LOWER(?)"
        else:
            filtro_nome = "WHERE a.nome COLLATE utf8mb4_general_ci LIKE %s"
        params = (f"%{pesquisa}%",)

    group_concat = "GROUP_CONCAT(d.nome, ', ')" if is_sqlite() else "GROUP_CONCAT(d.nome ORDER BY d.nome SEPARATOR ', ')"
    lista = fetch_all(
        f"""
        SELECT a.*,
               {group_concat} AS disciplinas
          FROM alunos a
          LEFT JOIN matriculas m ON m.aluno_id = a.id AND m.ativo = 1
          LEFT JOIN disciplinas d ON d.id = m.disciplina_id
         {filtro_nome}
         GROUP BY a.id
         ORDER BY a.nome
        """,
        params,
    )
    return render_template("alunos.html", alunos=lista, pesquisa=pesquisa)


@app.route("/alunos/<int:aluno_id>/editar", methods=["GET", "POST"])
def editar_aluno(aluno_id):
    aluno = fetch_one("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
    if not aluno:
        flash("Aluno nao encontrado.", "warning")
        return redirect(url_for("alunos"))

    if request.method == "POST":
        nome = form_value("nome")
        cpf = form_value("cpf")
        matricula = form_value("matricula")
        curso = form_value("curso")

        if not nome:
            flash("Nome obrigatório.", "warning")
        elif len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
        elif not cpf:
            flash("CPF obrigatório.", "warning")
        elif not CPF_PATTERN.fullmatch(cpf):
            flash("CPF deve estar no formato 000.000.000-00.", "warning")
        elif not matricula:
            flash("Matrícula obrigatória.", "warning")
        elif not curso:
            flash("Curso obrigatório.", "warning")
        else:
            try:
                execute(
                    """
                    UPDATE alunos
                       SET nome = %s, cpf = %s, matricula = %s, curso = %s
                     WHERE id = %s
                    """,
                    (
                        nome,
                        cpf,
                        matricula,
                        curso,
                        aluno_id,
                    ),
                )
                flash("Aluno atualizado com sucesso.", "success")
                return redirect(url_for("alunos"))
            except IntegrityError:
                flash("Ja existe aluno com este CPF ou matricula.", "warning")

    return render_template("editar_aluno.html", aluno=aluno)


@app.route("/professores", methods=["GET", "POST"])
def professores():
    if request.method == "POST":
        nome = form_value("nome")
        cpf = form_value("cpf")
        registro = form_value("registro")
        area = form_value("area")

        if not nome:
            flash("Nome obrigatório.", "warning")
            return redirect(url_for("professores"))
        if len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
            return redirect(url_for("professores"))
        if not cpf:
            flash("CPF obrigatório.", "warning")
            return redirect(url_for("professores"))
        if not CPF_PATTERN.fullmatch(cpf):
            flash("CPF deve estar no formato 000.000.000-00.", "warning")
            return redirect(url_for("professores"))
        if not registro:
            flash("Registro obrigatório.", "warning")
            return redirect(url_for("professores"))
        if not area:
            flash("Área obrigatória.", "warning")
            return redirect(url_for("professores"))

        try:
            execute(
                """
                INSERT INTO professores (nome, cpf, registro, area)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    nome,
                    cpf,
                    registro,
                    area,
                ),
            )
            flash("Professor cadastrado com sucesso.", "success")
        except IntegrityError:
            flash("Ja existe professor com este CPF ou registro.", "warning")
        return redirect(url_for("professores"))

    group_concat = "GROUP_CONCAT(d.nome, ', ')" if is_sqlite() else "GROUP_CONCAT(d.nome ORDER BY d.nome SEPARATOR ', ')"
    lista = fetch_all(
        f"""
        SELECT p.*,
               {group_concat} AS disciplinas
          FROM professores p
          LEFT JOIN disciplinas d ON d.professor_id = p.id
         GROUP BY p.id
         ORDER BY p.nome
        """
    )
    return render_template("professores.html", professores=lista)


@app.route("/professores/<int:professor_id>/editar", methods=["GET", "POST"])
def editar_professor(professor_id):
    professor = fetch_one("SELECT * FROM professores WHERE id = %s", (professor_id,))
    if not professor:
        flash("Professor nao encontrado.", "warning")
        return redirect(url_for("professores"))

    if request.method == "POST":
        nome = form_value("nome")
        cpf = form_value("cpf")
        registro = form_value("registro")
        area = form_value("area")

        if not nome:
            flash("Nome obrigatório.", "warning")
        elif len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
        elif not cpf:
            flash("CPF obrigatório.", "warning")
        elif not CPF_PATTERN.fullmatch(cpf):
            flash("CPF deve estar no formato 000.000.000-00.", "warning")
        elif not registro:
            flash("Registro obrigatório.", "warning")
        elif not area:
            flash("Área obrigatória.", "warning")
        else:
            try:
                execute(
                    """
                    UPDATE professores
                       SET nome = %s, cpf = %s, registro = %s, area = %s
                     WHERE id = %s
                    """,
                    (
                        nome,
                        cpf,
                        registro,
                        area,
                        professor_id,
                    ),
                )
                flash("Professor atualizado com sucesso.", "success")
                return redirect(url_for("professores"))
            except IntegrityError:
                flash("Ja existe professor com este CPF ou registro.", "warning")

    return render_template("editar_professor.html", professor=professor)


@app.route("/disciplinas", methods=["GET", "POST"])
def disciplinas():
    if request.method == "POST":
        nome = form_value("nome")
        codigo = form_value("codigo")
        carga_horaria_raw = form_value("carga_horaria")
        professor_id = request.form.get("professor_id") or None

        if not nome:
            flash("Nome obrigatório.", "warning")
            return redirect(url_for("disciplinas"))
        if len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
            return redirect(url_for("disciplinas"))
        if not codigo:
            flash("Código obrigatório.", "warning")
            return redirect(url_for("disciplinas"))
        if not carga_horaria_raw:
            flash("Carga horária obrigatória.", "warning")
            return redirect(url_for("disciplinas"))

        try:
            carga_horaria = int(carga_horaria_raw)
        except ValueError:
            flash("Carga horária deve ser um número.", "warning")
            return redirect(url_for("disciplinas"))

        try:
            execute(
                """
                INSERT INTO disciplinas (nome, codigo, carga_horaria, professor_id)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    nome,
                    codigo,
                    carga_horaria,
                    professor_id,
                ),
            )
            flash("Disciplina cadastrada com sucesso.", "success")
        except IntegrityError:
            flash("Ja existe disciplina com este codigo.", "warning")
        return redirect(url_for("disciplinas"))

    professores_lista = fetch_all("SELECT id, nome FROM professores ORDER BY nome")
    lista = fetch_all(
        """
        SELECT d.*, COALESCE(p.nome, 'Sem professor') AS professor,
               COUNT(m.aluno_id) AS total_alunos
          FROM disciplinas d
          LEFT JOIN professores p ON p.id = d.professor_id
          LEFT JOIN matriculas m ON m.disciplina_id = d.id AND m.ativo = 1
         GROUP BY d.id, p.nome
         ORDER BY d.nome
        """
    )
    return render_template(
        "disciplinas.html", disciplinas=lista, professores=professores_lista
    )


@app.route("/disciplinas/<int:disciplina_id>/editar", methods=["GET", "POST"])
def editar_disciplina(disciplina_id):
    disciplina = fetch_one("SELECT * FROM disciplinas WHERE id = %s", (disciplina_id,))
    if not disciplina:
        flash("Disciplina nao encontrada.", "warning")
        return redirect(url_for("disciplinas"))

    professores_lista = fetch_all("SELECT id, nome FROM professores ORDER BY nome")

    if request.method == "POST":
        nome = form_value("nome")
        codigo = form_value("codigo")
        carga_horaria_raw = form_value("carga_horaria")
        professor_id = request.form.get("professor_id") or None

        if not nome:
            flash("Nome obrigatório.", "warning")
        elif len(nome) < 2:
            flash("Nome deve ter pelo menos 2 caracteres.", "warning")
        elif not codigo:
            flash("Código obrigatório.", "warning")
        elif not carga_horaria_raw:
            flash("Carga horária obrigatória.", "warning")
        else:
            try:
                carga_horaria = int(carga_horaria_raw)
            except ValueError:
                flash("Carga horária deve ser um número.", "warning")
            else:
                try:
                    execute(
                        """
                        UPDATE disciplinas
                           SET nome = %s, codigo = %s, carga_horaria = %s, professor_id = %s
                         WHERE id = %s
                        """,
                        (
                            nome,
                            codigo,
                            carga_horaria,
                            professor_id,
                            disciplina_id,
                        ),
                    )
                    flash("Disciplina atualizada com sucesso.", "success")
                    return redirect(url_for("disciplinas"))
                except IntegrityError:
                    flash("Ja existe disciplina com este codigo.", "warning")

    return render_template(
        "editar_disciplina.html",
        disciplina=disciplina,
        professores=professores_lista,
    )


@app.route("/matriculas", methods=["GET", "POST"])
def matriculas():
    if request.method == "POST":
        aluno_id = form_value("aluno_id")
        disciplina_id = form_value("disciplina_id")

        if not aluno_id:
            flash("Aluno obrigatório.", "warning")
            return redirect(url_for("matriculas"))
        if not disciplina_id:
            flash("Disciplina obrigatória.", "warning")
            return redirect(url_for("matriculas"))

        matricula_existente = fetch_one(
            """
            SELECT id, ativo
              FROM matriculas
             WHERE aluno_id = %s AND disciplina_id = %s
            """,
            (aluno_id, disciplina_id),
        )

        if matricula_existente and matricula_existente["ativo"]:
            flash("Este aluno ja esta matriculado nessa disciplina.", "warning")
        elif matricula_existente:
            execute(
                """
                UPDATE matriculas
                   SET ativo = 1, removido_em = NULL
                 WHERE id = %s
                """,
                (matricula_existente["id"],),
            )
            flash("Matricula reativada com sucesso.", "success")
        else:
            try:
                execute(
                    """
                    INSERT INTO matriculas (aluno_id, disciplina_id, ativo)
                    VALUES (%s, %s, 1)
                    """,
                    (aluno_id, disciplina_id),
                )
                flash("Aluno matriculado com sucesso.", "success")
            except IntegrityError:
                flash("Este aluno ja esta matriculado nessa disciplina.", "warning")
        return redirect(url_for("matriculas"))

    alunos_lista = fetch_all("SELECT id, nome, matricula FROM alunos ORDER BY nome")
    disciplinas_lista = fetch_all("SELECT id, nome, codigo FROM disciplinas ORDER BY nome")
    lista = fetch_all(
        """
        SELECT m.id, a.nome AS aluno, a.matricula, d.nome AS disciplina, d.codigo
          FROM matriculas m
          JOIN alunos a ON a.id = m.aluno_id
          JOIN disciplinas d ON d.id = m.disciplina_id
         WHERE m.ativo = 1
         ORDER BY d.nome, a.nome
        """
    )
    return render_template(
        "matriculas.html",
        alunos=alunos_lista,
        disciplinas=disciplinas_lista,
        matriculas=lista,
    )


@app.route("/matriculas/<int:matricula_id>/editar", methods=["GET", "POST"])
def editar_matricula(matricula_id):
    matricula = fetch_one("SELECT * FROM matriculas WHERE id = %s", (matricula_id,))
    if not matricula:
        flash("Matricula nao encontrada.", "warning")
        return redirect(url_for("matriculas"))

    alunos_lista = fetch_all("SELECT id, nome, matricula FROM alunos ORDER BY nome")
    disciplinas_lista = fetch_all("SELECT id, nome, codigo FROM disciplinas ORDER BY nome")

    if request.method == "POST":
        aluno_id = form_value("aluno_id")
        disciplina_id = form_value("disciplina_id")

        if not aluno_id:
            flash("Aluno obrigatório.", "warning")
            return redirect(url_for("matriculas"))
        if not disciplina_id:
            flash("Disciplina obrigatória.", "warning")
            return redirect(url_for("matriculas"))

        try:
            execute(
                """
                UPDATE matriculas
                   SET aluno_id = %s, disciplina_id = %s, ativo = 1, removido_em = NULL
                 WHERE id = %s
                """,
                (
                    aluno_id,
                    disciplina_id,
                    matricula_id,
                ),
            )
            flash("Matricula atualizada com sucesso.", "success")
            return redirect(url_for("matriculas"))
        except IntegrityError:
            flash("Este aluno ja esta matriculado nessa disciplina.", "warning")

    return render_template(
        "editar_matricula.html",
        matricula=matricula,
        alunos=alunos_lista,
        disciplinas=disciplinas_lista,
    )


@app.post("/matriculas/<int:matricula_id>/excluir")
def excluir_matricula(matricula_id):
    execute(
        """
        UPDATE matriculas
           SET ativo = 0, removido_em = CURRENT_TIMESTAMP
         WHERE id = %s
        """,
        (matricula_id,),
    )
    flash("Matricula removida da interface. O registro continua no banco.", "success")
    return redirect(url_for("matriculas"))


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
