from Aluno import Aluno
from Disciplina import Disciplina
from Professor import Professor
from relatorios import gerar_relatorio_json, gerar_relatorio_pdf


class SistemaAcademico:
    def __init__(self):
        self.alunos = []
        self.professores = []
        self.disciplinas = []

    def cadastrar_aluno(self, aluno):
        if self.buscar_aluno_por_matricula(aluno.matricula) is not None:
            print(f"Ja existe aluno com matricula {aluno.matricula}.")
            return False
        if any(existing.cpf == aluno.cpf for existing in self.alunos):
            print(f"Ja existe aluno com CPF {aluno.cpf}.")
            return False

        self.alunos.append(aluno)
        return True

    def remover_aluno(self, matricula):
        aluno = self.buscar_aluno_por_matricula(matricula)
        if aluno is None:
            print("Aluno nao encontrado.")
            return False

        aluno.remover_dados()
        self.alunos.remove(aluno)
        print("Aluno removido do sistema.")
        return True

    def cadastrar_professor(self, professor):
        if self.buscar_professor_por_registro(professor.registro) is not None:
            print(f"Ja existe professor com registro {professor.registro}.")
            return False
        if any(existing.cpf == professor.cpf for existing in self.professores):
            print(f"Ja existe professor com CPF {professor.cpf}.")
            return False

        self.professores.append(professor)
        return True

    def cadastrar_disciplina(self, disciplina):
        if self.buscar_disciplina_por_codigo(disciplina.codigo) is not None:
            print(f"Ja existe disciplina com codigo {disciplina.codigo}.")
            return False

        self.disciplinas.append(disciplina)
        return True

    def buscar_aluno_por_matricula(self, matricula):
        for aluno in self.alunos:
            if aluno.matricula == matricula:
                return aluno
        return None

    def pesquisar_alunos_por_nome(self, nome):
        termo = nome.strip().lower()
        if not termo:
            return self.alunos

        return [aluno for aluno in self.alunos if termo in aluno.nome.lower()]

    def buscar_professor_por_registro(self, registro):
        for professor in self.professores:
            if professor.registro == registro:
                return professor
        return None

    def buscar_disciplina_por_codigo(self, codigo):
        for disciplina in self.disciplinas:
            if disciplina.codigo == codigo:
                return disciplina
        return None

    def matricular_aluno_em_disciplina(self, matricula, codigo_disciplina):
        aluno = self.buscar_aluno_por_matricula(matricula)
        disciplina = self.buscar_disciplina_por_codigo(codigo_disciplina)

        if aluno is None:
            print("Aluno nao encontrado.")
            return

        if disciplina is None:
            print("Disciplina nao encontrada.")
            return

        disciplina.matricular_aluno(aluno)
        print(f"{aluno.nome} foi matriculado em {disciplina.nome}.")

    def editar_aluno(self, matricula, nome=None, cpf=None, nova_matricula=None, curso=None):
        aluno = self.buscar_aluno_por_matricula(matricula)
        if aluno is None:
            print("Aluno nao encontrado.")
            return False

        if nome is not None:
            aluno.nome = nome
        if cpf is not None:
            aluno.cpf = cpf
        if nova_matricula is not None:
            aluno.matricula = nova_matricula
        if curso is not None:
            aluno.curso = curso

        print("Aluno atualizado com sucesso.")
        return True

    def editar_professor(self, registro, nome=None, cpf=None, novo_registro=None, area=None):
        professor = self.buscar_professor_por_registro(registro)
        if professor is None:
            print("Professor nao encontrado.")
            return False

        if nome is not None:
            professor.nome = nome
        if cpf is not None:
            professor.cpf = cpf
        if novo_registro is not None:
            professor.registro = novo_registro
        if area is not None:
            professor.area = area

        print("Professor atualizado com sucesso.")
        return True

    def editar_disciplina(
        self,
        codigo,
        nome=None,
        novo_codigo=None,
        carga_horaria=None,
        professor=None,
    ):
        disciplina = self.buscar_disciplina_por_codigo(codigo)
        if disciplina is None:
            print("Disciplina nao encontrada.")
            return False

        if nome is not None:
            disciplina.nome = nome
        if novo_codigo is not None:
            disciplina.codigo = novo_codigo
        if carga_horaria is not None:
            disciplina.carga_horaria = carga_horaria
        if professor is not None:
            disciplina.definir_professor(professor)

        print("Disciplina atualizada com sucesso.")
        return True

    def listar_alunos(self):
        print("\nALUNOS")
        for aluno in self.alunos:
            print(aluno)
            print(f"Disciplinas: {aluno.listar_disciplinas()}")

    def listar_professores(self):
        print("\nPROFESSORES")
        for professor in self.professores:
            print(professor)
            print(f"Disciplinas: {professor.listar_disciplinas()}")

    def listar_disciplinas(self):
        print("\nDISCIPLINAS")
        for disciplina in self.disciplinas:
            print(disciplina)
            print(f"Alunos: {disciplina.listar_alunos()}")

    def gerar_dados_relatorio(self):
        return {
            "alunos": [
                {
                    "nome": aluno.nome,
                    "cpf": aluno.cpf,
                    "matricula": aluno.matricula,
                    "curso": aluno.curso,
                    "disciplinas": [disciplina.nome for disciplina in aluno.disciplinas],
                }
                for aluno in self.alunos
            ],
            "professores": [
                {
                    "nome": professor.nome,
                    "cpf": professor.cpf,
                    "registro": professor.registro,
                    "area": professor.area,
                    "disciplinas": [
                        disciplina.nome for disciplina in professor.disciplinas
                    ],
                }
                for professor in self.professores
            ],
            "disciplinas": [
                {
                    "nome": disciplina.nome,
                    "codigo": disciplina.codigo,
                    "carga_horaria": disciplina.carga_horaria,
                    "professor": (
                        disciplina.professor.nome
                        if disciplina.professor
                        else "Sem professor"
                    ),
                    "alunos": [aluno.nome for aluno in disciplina.alunos],
                }
                for disciplina in self.disciplinas
            ],
            "matriculas": [
                {
                    "aluno": aluno.nome,
                    "matricula": aluno.matricula,
                    "disciplina": disciplina.nome,
                    "codigo": disciplina.codigo,
                    "status": "ativa",
                }
                for disciplina in self.disciplinas
                for aluno in disciplina.alunos
            ],
        }

    def gerar_relatorio_json(self, caminho="relatorio_academico.json"):
        return gerar_relatorio_json(self.gerar_dados_relatorio(), caminho)

    def gerar_relatorio_pdf(self, caminho="relatorio_academico.pdf"):
        return gerar_relatorio_pdf(self.gerar_dados_relatorio(), caminho)


def ler_campo(rotulo):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if valor:
            return valor
        print(f"{rotulo} e obrigatorio.")


def cadastrar_aluno_menu(sistema):
    aluno = Aluno(
        nome=ler_campo("Nome"),
        cpf=ler_campo("CPF"),
        matricula=ler_campo("Matricula"),
        curso=ler_campo("Curso"),
    )
    if sistema.cadastrar_aluno(aluno):
        print("Aluno cadastrado com sucesso.")


def cadastrar_professor_menu(sistema):
    professor = Professor(
        nome=ler_campo("Nome"),
        cpf=ler_campo("CPF"),
        registro=ler_campo("Registro"),
        area=ler_campo("Area"),
    )
    if sistema.cadastrar_professor(professor):
        print("Professor cadastrado com sucesso.")


def cadastrar_disciplina_menu(sistema):
    professor = None
    registro_professor = input("Registro do professor (opcional): ").strip()
    if registro_professor:
        professor = sistema.buscar_professor_por_registro(registro_professor)
        if professor is None:
            print("Professor nao encontrado. A disciplina sera cadastrada sem professor.")

    while True:
        carga_horaria_raw = ler_campo("Carga horaria")
        try:
            carga_horaria = int(carga_horaria_raw)
            break
        except ValueError:
            print("Carga horaria deve ser um numero.")

    disciplina = Disciplina(
        nome=ler_campo("Nome"),
        codigo=ler_campo("Codigo"),
        carga_horaria=carga_horaria,
        professor=professor,
    )
    if sistema.cadastrar_disciplina(disciplina):
        print("Disciplina cadastrada com sucesso.")


def matricular_aluno_menu(sistema):
    matricula = ler_campo("Matricula do aluno")
    codigo_disciplina = ler_campo("Codigo da disciplina")
    sistema.matricular_aluno_em_disciplina(matricula, codigo_disciplina)


def listar_todos(sistema):
    sistema.listar_alunos()
    sistema.listar_professores()
    sistema.listar_disciplinas()


def menu():
    sistema = SistemaAcademico()

    while True:
        print("\n1. Cadastrar aluno")
        print("2. Cadastrar professor")
        print("3. Cadastrar disciplina")
        print("4. Matricular aluno")
        print("5. Listar todos")
        print("0. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar_aluno_menu(sistema)
        elif opcao == "2":
            cadastrar_professor_menu(sistema)
        elif opcao == "3":
            cadastrar_disciplina_menu(sistema)
        elif opcao == "4":
            matricular_aluno_menu(sistema)
        elif opcao == "5":
            listar_todos(sistema)
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opcao invalida.")


def main():
    menu()


if __name__ == "__main__":
    main()
