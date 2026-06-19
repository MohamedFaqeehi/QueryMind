import re
import sqlite3

from google.genai import types

MAX_ROWS = 100
QUERY_TIMEOUT_SECONDS = 5.0

# Only a single, read-only SELECT statement is allowed. This blocks writes,
# schema changes, and stacked/chained statements (e.g. "SELECT 1; DROP TABLE x").
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|"
    r"PRAGMA|VACUUM|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def _is_safe_select(query: str) -> tuple[bool, str]:
    stripped = query.strip().rstrip(";")

    if not stripped:
        return False, "Query is empty."

    if ";" in stripped:
        return False, "Only a single statement is allowed (no semicolons / chained statements)."

    if not stripped.lstrip().upper().startswith("SELECT"):
        return False, "Only SELECT statements are allowed."

    if _FORBIDDEN_KEYWORDS.search(stripped):
        return False, "Query contains a disallowed keyword (only read-only SELECT queries are permitted)."

    return True, ""


def run_sql_query(db_path: str, query: str) -> str:
    is_safe, reason = _is_safe_select(query)
    if not is_safe:
        return f"Error: query rejected - {reason}"

    try:
        # Open the connection read-only so even a bypassed check can't mutate data.
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=QUERY_TIMEOUT_SECONDS)
        cursor = conn.cursor()

        # Enforce a row cap regardless of whether the model included LIMIT itself.
        capped_query = f"SELECT * FROM ({query.strip().rstrip(';')}) LIMIT {MAX_ROWS}"
        cursor.execute(capped_query)

        rows = cursor.fetchall()
        col_names = [description[0] for description in cursor.description]
        conn.close()

        if not rows:
            return "Query executed successfully but returned no rows."

        lines = [", ".join(col_names)]
        for row in rows:
            lines.append(", ".join(str(v) for v in row))

        result = "\n".join(lines)
        if len(rows) == MAX_ROWS:
            result += f"\n\n(Results capped at {MAX_ROWS} rows.)"
        return result
    except Exception as e:
        return f"Error executing query: {e}"


schema_run_sql_query = types.FunctionDeclaration(
    name="run_sql_query",
    description=(
        "Executes a single read-only SELECT query against the database and returns the results. "
        "Only SELECT statements are permitted; results are automatically capped at "
        f"{MAX_ROWS} rows. Call list_tables and get_table_schema first to confirm table/column names."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="A single SQL SELECT statement to run, e.g. 'SELECT name FROM customers WHERE country = \"USA\"'.",
            ),
        },
        required=["query"],
    ),
)
