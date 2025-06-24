# GPT_2

This repository contains a simple desktop interface for ChatGPT built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). The `GPT.py` script provides a GUI for interacting with OpenAI models and supports uploading files such as Word documents, PDFs, images and Excel spreadsheets.

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

### 3. Set your OpenAI API key

The script expects the environment variable `OPENAI_API_KEY` to be set with your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key_here  # On Windows use: set OPENAI_API_KEY=your_key_here
```

### 4. Launch the application

Run the GUI with Python:

```bash
python GPT.py
```

The window should open allowing you to chat with the model and upload supported files.
