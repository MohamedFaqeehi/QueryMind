# QueryMind

QueryMind is an AI data assistant powered by Google's Gemini API. You ask it questions in plain English, and it autonomously inspects a SQLite database, figures out the right queries, and gives you an answer — looping until it produces a final response or hits a max iteration limit.

## Features

QueryMind exposes the following tools to the Gemini model:

- **`list_tables`** — list tables in the SQLite database
- **`get_table_schema`** — inspect a table's schema
- **`run_sql_query`** — run a SQL query against the database

The model decides which tools to call based on your prompt, and QueryMind executes them and feeds the results back until the task is done — so you can ask questions about your data without writing SQL yourself.

## Requirements

- Python (version pinned in `.python-version`)
- [uv](https://github.com/astral-sh/uv) for dependency management
- A [Gemini API key](https://ai.google.dev/)

## Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/MohamedFaqeehi/QueryMind.git
   cd QueryMind
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Create a `.env` file in the project root with your Gemini API key:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

   > ⚠️ Never commit your `.env` file. It's already covered by `.gitignore`.

## Usage

Run the assistant with a prompt:

```bash
uv run main.py "your prompt here"
```

Add `--verbose` to see token usage and detailed function call output:

```bash
uv run main.py "your prompt here" --verbose
```

### Example

```bash
uv run main.py "What are the top 5 customers by total order value?"
```

## Project Structure

```
QueryMind/
├── functions/              # Tool implementations (database inspection and SQL execution)
├── call_function.py        # Dispatches Gemini's function calls to the right tool
├── config.py                # Configuration (database path, max iterations)
├── main.py                  # Entry point — CLI arg parsing and the agent loop
├── prompts.py                # System prompt sent to Gemini
├── pyproject.toml            # Project dependencies
└── uv.lock                   # Locked dependency versions
```

## Running Tests

```bash
uv run pytest
```

## License

No license specified.
