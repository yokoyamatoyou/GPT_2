# GPT_2

This repository contains a simple desktop interface for ChatGPT built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). The `src/ui/main.py` script provides a GUI for interacting with OpenAI models and supports uploading files such as Word documents, PDFs, images and Excel spreadsheets.

## Getting Started

Follow the steps below to run the application locally.

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: .\\venv\\Scripts\\activate
```

### 2. Install dependencies

Install all required Python packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

-`create_llm` reads additional variables if present:

- `OPENAI_MODEL` – default model to use (defaults to `gpt-3.5-turbo`).
  The GUI also uses this value as the initial model selection and includes
  `gpt-3.5-turbo` in the drop-down menu.
- `OPENAI_TOKEN_PRICE` – price per token for usage cost logging

### 4. Launch the application

Run the GUI with Python:

```bash
python -m src.ui.main
```

On Windows you can also start the application with the included batch file:

```batch
run_gui.bat
```

The window should open allowing you to chat with the model and upload supported files.

### 5. Install diagram tools

The optional diagram helpers `create_graphviz_diagram` and
`create_mermaid_diagram` rely on external CLI programs. `Graphviz`
provides the `dot` command and the `Mermaid CLI` ships the `mmdc`
command. Both tools must be installed and available in your `PATH`
for diagram generation to work. On Debian/Ubuntu you can install
Graphviz with:

```bash
apt install graphviz
```

And install the Mermaid CLI globally using npm:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## Running Tests

Install the runtime and development requirements:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Then execute the test suite with:

```bash
pytest
```

## Simple ReAct Agent

The project includes a minimal implementation of the ReAct agent pattern. To run
the agent programmatically:

```python
from src.agent import ReActAgent
from src.tools import get_web_scraper, get_sqlite_tool

def call_llm(prompt: str) -> str:
    # integrate with your favourite LLM here
    ...

agent = ReActAgent(call_llm, [get_web_scraper(), get_sqlite_tool()])
result = agent.run("東京の天気を教えて")
```
The agent includes a web scraping tool and a SQLite query tool.

You can also try the agent from the command line using the built in runner:

```bash
python -m src.main
```
The command line runner loads both tools by default. You can pass `--memory vector`
to enable the `VectorMemory` store instead of the default conversation memory:

```bash
python -m src.main --memory vector
```
To run the experimental Tree-of-Thoughts agent instead of ReAct:

```bash
python -m src.main --agent tot
```

You can adjust the search parameters for the ToT agent using `--depth` and
`--breadth`:

```bash
python -m src.main --agent tot --depth 3 --breadth 4
```
You can persist the conversation across runs by specifying `--memory-file` with a
path to a JSON file. The memory will be loaded at startup and saved when the
program exits:

```bash
python -m src.main --memory-file chat.json
```
Logs are written to the console by default. Use `--log-file` to also save them
to a file (or set the `AGENT_LOG_FILE` environment variable):

```bash
python -m src.main --log-file agent.log
```
Enable debug logging and verbose agent output with `--verbose`:

```bash
python -m src.main --verbose
```

Display each reasoning step as it happens with `--stream`:

```bash
python -m src.main --stream
```

## Experimental ToT Agent

The repository also ships with a tiny Tree-of-Thoughts agent. It explores
multiple branches and chooses the one with the highest evaluation score.

```python
from src.agent import ToTAgent

def llm(prompt: str) -> str:
    ...

def evaluate(history: str) -> float:
    ...

agent = ToTAgent(llm, evaluate)
answer = agent.run("質問")

# Stream intermediate reasoning steps
for step in agent.run_iter("質問"):
    print(step)
```

This implementation is intentionally simple but shows how an LLM can be used in
a branch-and-bound style search loop.
## Verbose Logging

Set `verbose=True` when creating `ReActAgent` to enable debug output using Python's `logging` module.

```python
agent = ReActAgent(call_llm, [get_web_scraper(), get_sqlite_tool()], verbose=True)
```

## Token Usage Tracking

The `create_llm` helper can log the number of tokens consumed and estimate the
cost of each OpenAI API call. Set `OPENAI_TOKEN_PRICE` in your environment to the
price per token (e.g. `0.000002`) and pass `log_usage=True` when creating the
LLM. The cost is calculated as `token_count * OPENAI_TOKEN_PRICE`. The model used
for completion defaults to `gpt-3.5-turbo` but can be overridden with
`OPENAI_MODEL`:

```python
llm = create_llm(log_usage=True)
```

Log records will include the token count and calculated cost.

## Web Scraper Settings

The built-in web scraping tool caches pages and waits between requests. You can
adjust these values with environment variables:

- `WEB_SCRAPER_CACHE_TTL` – cache duration in seconds (default `3600`)
- `WEB_SCRAPER_DELAY` – delay between HTTP requests in seconds (default `1.0`)
- `WEB_SCRAPER_USER_AGENT` – value for the `User-Agent` header (default `Mozilla/5.0`)

Example:

```bash
export WEB_SCRAPER_USER_AGENT="Mozilla/5.0 (compatible; MyAgent/1.0)"
```

## Configuring Logging

Use `setup_logging` to send logs to both the console and optionally a file.
Set the `AGENT_LOG_FILE` environment variable to define a default log path.

```python
from src import setup_logging
setup_logging(level=logging.DEBUG)  # uses AGENT_LOG_FILE if set
```

## License

This project is licensed under the [MIT License](LICENSE).
