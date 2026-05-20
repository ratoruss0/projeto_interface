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
```

Se precisar, defina as variaveis antes de iniciar:

```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=sua_senha
export MYSQL_DATABASE=sistema_academico
```

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

## Arquivos adicionados

- `app.py`: rotas da aplicacao Flask.
- `db.py`: conexao e funcoes simples para consultar o MySQL.
- `schema.sql`: criacao do banco e tabelas.
- `templates/`: telas HTML.
- `static/styles.css`: estilo visual da interface.
