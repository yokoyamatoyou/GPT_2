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

### 4. Launch the application

Run the GUI with Python:

```bash
python -m src.ui.main
```

The window should open allowing you to chat with the model and upload supported files.

## Running Tests

Install the development requirements:

```bash
pip install -r requirements-dev.txt
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
from src.tools import get_web_scraper

def call_llm(prompt: str) -> str:
    # integrate with your favourite LLM here
    ...

agent = ReActAgent(call_llm, [get_web_scraper()])
result = agent.run("東京の天気を教えて")
```


## License

This project is licensed under the [MIT License](LICENSE).
