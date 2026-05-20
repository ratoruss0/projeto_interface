from Aluno import Aluno
from Disciplina import Disciplina
from Professor import Professor
from Sistema_academico import SistemaAcademico


def test_disciplina_matricula_aluno_nos_dois_lados():
    aluno = Aluno("Ana Lima", "999.888.777-66", "2026002", "Computacao")
    disciplina = Disciplina("Programacao", "PROG101", 80)

    disciplina.matricular_aluno(aluno)
    disciplina.matricular_aluno(aluno)

    assert disciplina.alunos == [aluno]
    assert aluno.disciplinas == [disciplina]


def test_disciplina_define_professor_nos_dois_lados():
    professor = Professor("Mariana Souza", "111.222.333-44", "PROF001", "Programacao")
    disciplina = Disciplina("POO", "POO101", 80, professor=professor)

    assert disciplina.professor == professor
    assert professor.disciplinas == [disciplina]


def test_sistema_bloqueia_aluno_duplicado_por_matricula_e_cpf():
    sistema = SistemaAcademico()
    aluno = Aluno("Felipe Santos", "555.666.777-88", "2026001", "Sistemas")
    mesma_matricula = Aluno("Outro Aluno", "555.666.777-99", "2026001", "Sistemas")
    mesmo_cpf = Aluno("Mais Um", "555.666.777-88", "2026003", "Sistemas")

    assert sistema.cadastrar_aluno(aluno) is True
    assert sistema.cadastrar_aluno(mesma_matricula) is False
    assert sistema.cadastrar_aluno(mesmo_cpf) is False
    assert sistema.alunos == [aluno]


def test_sistema_remove_aluno_da_lista_e_das_disciplinas():
    sistema = SistemaAcademico()
    aluno = Aluno("Felipe Santos", "555.666.777-88", "2026001", "Sistemas")
    disciplina = Disciplina("POO", "POO101", 80)

    sistema.cadastrar_aluno(aluno)
    sistema.cadastrar_disciplina(disciplina)
    sistema.matricular_aluno_em_disciplina("2026001", "POO101")

    assert sistema.remover_aluno("2026001") is True
    assert aluno not in sistema.alunos
    assert aluno not in disciplina.alunos
