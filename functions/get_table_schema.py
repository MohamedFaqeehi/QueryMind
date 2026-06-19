import sqlite3

from google.genai import types


def get_table_schema(db_path: str, table_name: str) -> str:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Confirm the table actually exists before describing it
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        if cursor.fetchone() is None:
            conn.close()
            return f'Error: table "{table_name}" does not exist'

        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)

        cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
        foreign_keys = cursor.fetchall()  # (id, seq, table, from, to, on_update, on_delete, match)

        cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3;")
        sample_rows = cursor.fetchall()
        col_names = [description[0] for description in cursor.description]

        conn.close()

        lines = [f"Schema for '{table_name}':"]
        for _, name, col_type, notnull, _, is_pk in columns:
            flags = []
            if is_pk:
                flags.append("PRIMARY KEY")
            if notnull:
                flags.append("NOT NULL")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            lines.append(f"  - {name}: {col_type}{flag_str}")

        if foreign_keys:
            lines.append("Foreign keys:")
            for fk in foreign_keys:
                lines.append(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")

        if sample_rows:
            lines.append("Sample rows:")
            lines.append("  " + ", ".join(col_names))
            for row in sample_rows:
                lines.append("  " + ", ".join(str(v) for v in row))

        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving schema for '{table_name}': {e}"


schema_get_table_schema = types.FunctionDeclaration(
    name="get_table_schema",
    description="Returns the column names, types, primary/foreign keys, and a few sample rows for a given table. Call this before writing a query so you know the exact column names and how tables relate.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "table_name": types.Schema(
                type=types.Type.STRING,
                description="The name of the table to describe (must match a table returned by list_tables).",
            ),
        },
        required=["table_name"],
    ),
)
