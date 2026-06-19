import sqlite3

from google.genai import types


def list_tables(db_path: str) -> str:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not tables:
            return "No tables found in the database."
        return "\n".join(f"- {table}" for table in tables)
    except Exception as e:
        return f"Error listing tables: {e}"


schema_list_tables = types.FunctionDeclaration(
    name="list_tables",
    description="Lists all tables available in the SQLite database, so you know what data exists before querying it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
    ),
)
