"""Web search abstraction layer for market research."""
from __future__ import annotations

import time
from typing import Optional


class WebSearch:
    """Web search using DuckDuckGo HTML (no API key required)."""

    def __init__(self, rate_limit_delay: float = 1.0, max_retries: int = 3):
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def search(self, query: str, num_results: int = 10) -> list[dict]:
        """Search the web and return results as list of {title, url, snippet}."""
        import requests

        self._rate_limit()

        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        }
        params = {"q": query, "kl": "us-en"}

        for attempt in range(self.max_retries):
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=15)
                if resp.status_code == 429:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue
                if resp.status_code != 200:
                    return []
                break
            except Exception:
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)

        results = []
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "html.parser")
        for result in soup.select("a.result__a")[:num_results]:
            href = result.get("href", "")
            snippet_elem = result.find_parent("li").select_one(".result__snippet") if result.find_parent("li") else None
            results.append(
                {
                    "title": result.get_text(strip=True),
                    "url": href,
                    "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                }
            )
        return results

    def search_with_retry(self, query: str, num_results: int = 10) -> list[dict]:
        """Search with built-in retries and rate limiting."""
        results = self.search(query, num_results)
        if not results:
            # retry once after backoff
            import time
            time.sleep(2)
            results = self.search(query, num_results)
        return results

    def rate_limit(self) -> None:
        """Apply rate limiting delay (alias for _rate_limit)."""
        self._rate_limit()

    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch a single page and return its text content."""
        import requests

        self._rate_limit()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(resp.text, "html.parser")
                # Remove script/style/nav elements
                for tag in soup(["script", "style", "nav", "header", "footer"]):
                    tag.decompose()
                text = soup.get_text(separator=" ", strip=True)
                # Collapse whitespace
                import re

                return re.sub(r"\s+", " ", text)
        except Exception:
            pass
        return None
