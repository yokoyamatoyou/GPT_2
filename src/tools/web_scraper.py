from typing import Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from .base import Tool


class ScraperInput(BaseModel):
    url: str = Field(description="WebページのURL")
    max_chars: Optional[int] = Field(
        default=1000, description="取得するテキストの最大文字数"
    )


def scrape_website_content(url: str, max_chars: int = 1000) -> str:
    """Fetch a web page and return cleaned text."""
    try:
        response = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching {url}: {e}"

    soup = BeautifulSoup(response.content, "html.parser")

    main = soup.find("main") or soup.find("article") or soup.find("body")
    if not main:
        return "No content"

    for tag in main.find_all(["script", "style", "header", "footer", "nav"]):
        tag.decompose()

    text = main.get_text(separator=" ", strip=True)
    return text[:max_chars]


def get_tool() -> Tool:
    return Tool(
        name="web_scraper",
        description="指定されたURLから主要テキストを抽出するツール。入力はURL。",
        func=scrape_website_content,
        args_schema=ScraperInput,
    )
