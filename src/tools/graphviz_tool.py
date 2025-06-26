import os
import subprocess
import tempfile
from pydantic import BaseModel, Field
from .base import Tool

class GraphvizInput(BaseModel):
    code: str = Field(description="DOT言語のコード")


def create_graphviz_diagram(dot_code: str) -> str:
    """Generate a diagram PNG from Graphviz DOT code."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".dot") as src:
        src.write(dot_code)
        src_path = src.name
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    out_file.close()
    try:
        subprocess.run(
            ["dot", "-Tpng", src_path, "-o", out_file.name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        os.unlink(src_path)
        return "graphviz 'dot' command not found."
    except subprocess.CalledProcessError as exc:
        os.unlink(src_path)
        return f"Failed to generate diagram: {exc.stderr.decode().strip()}"
    os.unlink(src_path)
    return out_file.name


def get_tool() -> Tool:
    return Tool(
        name="create_graphviz_diagram",
        description="DOT言語から図を生成する。フローチャート等に適している。",
        func=create_graphviz_diagram,
        args_schema=GraphvizInput,
    )
