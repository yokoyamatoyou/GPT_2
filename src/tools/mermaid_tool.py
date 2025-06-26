import os
import subprocess
import tempfile
from pydantic import BaseModel, Field
from .base import Tool

class MermaidInput(BaseModel):
    code: str = Field(description="Mermaid記法のコード")


def create_mermaid_diagram(mermaid_code: str) -> str:
    """Generate a diagram PNG from Mermaid code using the mmdc CLI."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".mmd") as src:
        src.write(mermaid_code)
        src_path = src.name
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    out_file.close()
    try:
        subprocess.run(
            ["mmdc", "-i", src_path, "-o", out_file.name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        os.unlink(src_path)
        return "mmdc command not found. Install @mermaid-js/mermaid-cli."
    except subprocess.CalledProcessError as exc:
        os.unlink(src_path)
        return f"Failed to generate diagram: {exc.stderr.decode().strip()}"
    os.unlink(src_path)
    return out_file.name


def get_tool() -> Tool:
    """Return a Tool for generating diagrams from Mermaid code."""
    return Tool(
        name="create_mermaid_diagram",
        description="Mermaid markdown-like codeから図を生成する。シーケンス図、ガントチャート等に適している。",
        func=create_mermaid_diagram,
        args_schema=MermaidInput,
    )
