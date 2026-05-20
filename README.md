# Sistema Academico Web

Interface web em Flask para cadastrar alunos, professores, disciplinas e
matriculas usando MySQL.

Se o MySQL nao estiver instalado ou iniciado, a aplicacao usa automaticamente
um banco SQLite local chamado `sistema_academico.sqlite3`, para permitir testar
a interface sem travar na conexao.

## 1. Criar o banco

No MySQL, execute:

```bash
mysql -u root -p < schema.sql
```

O script cria o banco `sistema_academico`, as tabelas e alguns dados iniciais.

Em um RDS MySQL, configure as variaveis de ambiente e rode:

```bash
python scripts/init_mysql.py
```

Para controlar alteracoes futuras no schema, o projeto tambem possui Alembic:

```bash
python scripts/run_migrations.py
```

As migrations usam `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD` e `MYSQL_DATABASE`.

## 2. Instalar dependencias

```bash
python3 -m pip install -r requirements.txt
```

## 3. Configurar conexao

Por padrao, a aplicacao usa:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=sistema_academico
FLASK_SECRET_KEY=defina-uma-chave-segura
```

Se precisar, defina as variaveis antes de iniciar:

```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=sua_senha
export MYSQL_DATABASE=sistema_academico
export FLASK_SECRET_KEY=sua_chave_secreta
```

A aplicacao nao possui chave secreta padrao. Se `FLASK_SECRET_KEY` nao estiver
definida, o Flask nao inicia.

## 4. Rodar a interface

```bash
python3 app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

> Nota: o relatório em PDF é gerado usando codificação Latin-1. Caracteres fora dessa faixa de codificação podem ser substituídos ou perdidos no arquivo PDF. Para garantir suporte total a UTF-8, use o relatório JSON.

Para obrigar o uso do MySQL e desativar o modo SQLite local:

```bash
MYSQL_REQUIRED=1 python3 app.py
```

> Aviso: a detecção de banco de dados é feita apenas na primeira conexão. Se o MySQL estiver indisponível ao iniciar a aplicação, ela passará a usar SQLite e não voltará automaticamente para MySQL até que o servidor seja reiniciado.

## 5. Variaveis no Elastic Beanstalk

No Elastic Beanstalk, configure as variaveis de ambiente no ambiente da
aplicacao, nunca dentro do codigo:

```text
MYSQL_HOST=endpoint-do-rds
MYSQL_PORT=3306
MYSQL_USER=usuario_do_banco
MYSQL_PASSWORD=senha_do_banco
MYSQL_DATABASE=sistema_academico
MYSQL_REQUIRED=1
FLASK_SECRET_KEY=chave_aleatoria_segura
FLASK_DEBUG=0
```

Uma chave segura pode ser gerada localmente com:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Para credenciais de banco em producao, prefira AWS Secrets Manager quando a
equipe ja tiver IAM configurado. Nesse caso, armazene `MYSQL_USER` e
`MYSQL_PASSWORD` no Secrets Manager e injete os valores no ambiente do Elastic
Beanstalk durante o deploy ou por automacao da AWS. O repositorio deve guardar
apenas nomes de variaveis e exemplos, nunca valores reais.

## Arquivos adicionados

- `app.py`: rotas da aplicacao Flask.
- `db.py`: conexao e funcoes simples para consultar o MySQL.
- `schema.sql`: criacao do banco e tabelas.
- `templates/`: telas HTML.
- `static/styles.css`: estilo visual da interface.
