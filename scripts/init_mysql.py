import os
from pathlib import Path

import mysql.connector


def split_sql(script):
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False

    for char in script:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        if char == ";" and not in_single_quote and not in_double_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def main():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
    )
    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"
    cursor = connection.cursor()

    try:
        for statement in split_sql(schema_path.read_text(encoding="utf-8")):
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    print("Banco MySQL inicializado com schema.sql.")


if __name__ == "__main__":
    main()
