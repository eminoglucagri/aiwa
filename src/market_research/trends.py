from .report import Trend
from .web_search import WebSearch


class TrendAnalyzer:
    def __init__(self, searcher: WebSearch):
        self.searcher = searcher

    async def analyze(self, app_idea: str, target_market: str) -> list[Trend]:
        trends = []

        trend_query = f"{target_market} trends 2025 2026"
        results = self.searcher.search_with_retry(trend_query)

        for r in results[:8]:
            title = r.get("title", "").strip()
            snippet = r.get("snippet", "").strip()
            if title and snippet:
                relevance = self._classify_relevance(title + " " + snippet)
                trends.append(Trend(
                    title=title,
                    description=snippet,
                    relevance=relevance,
                    source=r.get("url", ""),
                ))

        self.searcher.rate_limit()

        category_query = f"{app_idea} industry news 2025"
        category_results = self.searcher.search_with_retry(category_query)

        for r in category_results[:5]:
            title = r.get("title", "").strip()
            snippet = r.get("snippet", "").strip()
            if title and snippet and not any(t.title == title for t in trends):
                relevance = self._classify_relevance(title + " " + snippet)
                trends.append(Trend(
                    title=title,
                    description=snippet,
                    relevance=relevance,
                    source=r.get("url", ""),
                ))

        trends.sort(key=lambda t: {"high": 0, "medium": 1, "low": 2}.get(t.relevance, 1))
        return trends

    def _classify_relevance(self, text: str) -> str:
        text_lower = text.lower()
        high_keywords = ["ai", "automation", "growth", "expanding", "adoption", "surge", "boom"]
        low_keywords = ["decline", "shrink", "stagnant", "outdated", "legacy"]

        high_count = sum(1 for kw in high_keywords if kw in text_lower)
        low_count = sum(1 for kw in low_keywords if kw in text_lower)

        if high_count >= 2:
            return "high"
        elif low_count >= 1:
            return "low"
        return "medium"
