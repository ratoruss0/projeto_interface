import json

import db


def test_index_carrega_dashboard(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Alunos" in response.data
    assert b"Disciplinas" in response.data


def test_cadastro_aluno_salva_no_banco(client):
    response = client.post(
        "/alunos",
        data={
            "nome": "Joao Teste",
            "cpf": "123.456.789-00",
            "matricula": "2026999",
            "curso": "Sistemas de Informacao",
        },
        follow_redirects=True,
    )

    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026999",))

    assert response.status_code == 200
    assert aluno is not None
    assert aluno["nome"] == "Joao Teste"


def test_edita_aluno_com_put(client):
    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026001",))

    response = client.put(
        f"/alunos/{aluno['id']}",
        json={
            "nome": "Felipe Atualizado",
            "cpf": aluno["cpf"],
            "matricula": aluno["matricula"],
            "curso": aluno["curso"],
        },
    )
    atualizado = db.fetch_one("SELECT * FROM alunos WHERE id = %s", (aluno["id"],))

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert atualizado["nome"] == "Felipe Atualizado"


def test_cadastro_aluno_rejeita_cpf_invalido(client):
    response = client.post(
        "/alunos",
        data={
            "nome": "Joao Teste",
            "cpf": "12345678900",
            "matricula": "2026999",
            "curso": "Sistemas de Informacao",
        },
        follow_redirects=True,
    )

    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026999",))

    assert response.status_code == 200
    assert aluno is None


def test_exclusao_logica_aluno_remove_da_interface_e_preserva_banco(client):
    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026001",))

    response = client.post(f"/alunos/{aluno['id']}/excluir", follow_redirects=True)
    removido = db.fetch_one("SELECT * FROM alunos WHERE id = %s", (aluno["id"],))
    matriculas_ativas = db.fetch_one(
        "SELECT COUNT(*) AS total FROM matriculas WHERE aluno_id = %s AND ativo = 1",
        (aluno["id"],),
    )

    assert response.status_code == 200
    assert removido["ativo"] == 0
    assert removido["removido_em"] is not None
    assert matriculas_ativas["total"] == 0
    assert b"Felipe Santos" not in response.data


def test_cadastro_professor_disciplina_e_matricula(client):
    client.post(
        "/professores",
        data={
            "nome": "Carlos Silva",
            "cpf": "222.333.444-55",
            "registro": "PROF999",
            "area": "Banco de Dados",
        },
    )
    professor = db.fetch_one(
        "SELECT * FROM professores WHERE registro = %s", ("PROF999",)
    )

    client.post(
        "/disciplinas",
        data={
            "nome": "Banco de Dados",
            "codigo": "BD999",
            "carga_horaria": "60",
            "professor_id": str(professor["id"]),
        },
    )
    disciplina = db.fetch_one("SELECT * FROM disciplinas WHERE codigo = %s", ("BD999",))
    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026001",))

    response = client.post(
        "/matriculas",
        data={"aluno_id": str(aluno["id"]), "disciplina_id": str(disciplina["id"])},
        follow_redirects=True,
    )
    matricula = db.fetch_one(
        """
        SELECT * FROM matriculas
         WHERE aluno_id = %s AND disciplina_id = %s
        """,
        (aluno["id"], disciplina["id"]),
    )

    assert response.status_code == 200
    assert matricula is not None
    assert matricula["ativo"] == 1


def test_edita_professor_com_patch(client):
    professor = db.fetch_one("SELECT * FROM professores WHERE registro = %s", ("PROF001",))

    response = client.patch(
        f"/professores/{professor['id']}",
        json={
            "nome": "Mariana Atualizada",
            "cpf": professor["cpf"],
            "registro": professor["registro"],
            "area": "Engenharia de Software",
        },
    )
    atualizado = db.fetch_one("SELECT * FROM professores WHERE id = %s", (professor["id"],))

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert atualizado["area"] == "Engenharia de Software"


def test_exclusao_logica_disciplina_desativa_matriculas(client):
    disciplina = db.fetch_one("SELECT * FROM disciplinas WHERE codigo = %s", ("POO101",))

    response = client.post(
        f"/disciplinas/{disciplina['id']}/excluir", follow_redirects=True
    )
    removida = db.fetch_one("SELECT * FROM disciplinas WHERE id = %s", (disciplina["id"],))
    matriculas_ativas = db.fetch_one(
        """
        SELECT COUNT(*) AS total
          FROM matriculas
         WHERE disciplina_id = %s AND ativo = 1
        """,
        (disciplina["id"],),
    )

    assert response.status_code == 200
    assert removida["ativo"] == 0
    assert removida["removido_em"] is not None
    assert matriculas_ativas["total"] == 0
    assert b"POO101" not in response.data


def test_matricula_duplicada_nao_cria_novo_registro(client):
    aluno = db.fetch_one("SELECT * FROM alunos WHERE matricula = %s", ("2026001",))
    disciplina = db.fetch_one("SELECT * FROM disciplinas WHERE codigo = %s", ("POO101",))

    client.post(
        "/matriculas",
        data={"aluno_id": str(aluno["id"]), "disciplina_id": str(disciplina["id"])},
    )
    client.post(
        "/matriculas",
        data={"aluno_id": str(aluno["id"]), "disciplina_id": str(disciplina["id"])},
    )

    total = db.fetch_one(
        """
        SELECT COUNT(*) AS total
          FROM matriculas
         WHERE aluno_id = %s AND disciplina_id = %s
        """,
        (aluno["id"], disciplina["id"]),
    )

    assert total["total"] == 1


def test_relatorios_json_e_pdf(client):
    json_response = client.get("/relatorios/json")
    pdf_response = client.get("/relatorios/pdf")

    payload = json.loads(json_response.data.decode("utf-8"))

    assert json_response.status_code == 200
    assert json_response.mimetype == "application/json"
    assert "alunos" in payload
    assert "disciplinas" in payload
    assert pdf_response.status_code == 200
    assert pdf_response.mimetype == "application/pdf"
    assert pdf_response.data.startswith(b"%PDF")
