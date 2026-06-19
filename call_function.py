from collections.abc import Callable

from google.genai import types

from config import DB_PATH, WORKING_DIR
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_table_schema import get_table_schema, schema_get_table_schema
from functions.list_tables import list_tables, schema_list_tables
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.run_sql_query import run_sql_query, schema_run_sql_query
from functions.write_file import schema_write_file, write_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
        schema_list_tables,
        schema_get_table_schema,
        schema_run_sql_query,
    ]
)

function_map: dict[str, Callable[..., str]] = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
    "list_tables": list_tables,
    "get_table_schema": get_table_schema,
    "run_sql_query": run_sql_query,
}

# Functions that need the database path injected instead of the file working directory
_DB_FUNCTIONS = {"list_tables", "get_table_schema", "run_sql_query"}


def call_function(
    function_call: types.FunctionCall, verbose: bool = False
) -> types.Content:
    if verbose:
        print(f" - Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    function_name = function_call.name or ""
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    args = dict(function_call.args) if function_call.args else {}
    if function_name in _DB_FUNCTIONS:
        args["db_path"] = DB_PATH
    else:
        args["working_directory"] = WORKING_DIR
    result = function_map[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )
