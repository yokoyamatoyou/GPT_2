from typing import Optional, Dict, Tuple
import os
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import time

from pydantic import BaseModel, Field

# Shared state protected by _LOCK
_CACHE: Dict[str, Tuple[float, str]] = {}
_CACHE_TTL = int(os.getenv("WEB_SCRAPER_CACHE_TTL", "3600"))
_ROBOTS: Dict[str, RobotFileParser] = {}
_LAST_REQUEST_TIME = 0.0
_DELAY = float(os.getenv("WEB_SCRAPER_DELAY", "1.0"))
_LOCK = threading.RLock()
# Default headers for all HTTP requests
_HEADERS = {"User-Agent": os.getenv("WEB_SCRAPER_USER_AGENT", "Mozilla/5.0")}


def _respect_delay() -> None:
    global _LAST_REQUEST_TIME
    with _LOCK:
        since = time.time() - _LAST_REQUEST_TIME
        if since < _DELAY:
            time.sleep(_DELAY - since)
        _LAST_REQUEST_TIME = time.time()

from .base import Tool


class ScraperInput(BaseModel):
    url: str = Field(description="WebページのURL")
    max_chars: Optional[int] = Field(
        default=1000, description="取得するテキストの最大文字数"
    )


def scrape_website_content(url: str, max_chars: int = 1000) -> str:
    """Fetch a web page and return cleaned text respecting robots.txt."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    with _LOCK:
        # Check robots.txt
        rp = _ROBOTS.get(base)
        if rp is None:
            rp = RobotFileParser()
            robots_url = urljoin(base, "/robots.txt")
            try:
                _respect_delay()
                resp = requests.get(robots_url, headers=_HEADERS, timeout=5)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp = None
            except Exception:
                rp = None
            _ROBOTS[base] = rp
        if rp and not rp.can_fetch("*", parsed.path):
            return "Disallowed by robots.txt"

        # Check cache
        cached = _CACHE.get(url)
        if cached and time.time() - cached[0] < _CACHE_TTL:
            return cached[1][:max_chars]

        try:
            _respect_delay()
            response = requests.get(
                url, headers=_HEADERS, timeout=10
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
        result = text[:max_chars]
        _CACHE[url] = (time.time(), result)
        return result


def get_tool() -> Tool:
    return Tool(
        name="web_scraper",
        description="指定されたURLから主要テキストを抽出するツール。入力はURL。",
        func=scrape_website_content,
        args_schema=ScraperInput,
    )
