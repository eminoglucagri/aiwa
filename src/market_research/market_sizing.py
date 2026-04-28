import re

from .report import MarketSizing
from .web_search import WebSearch


class MarketSizingAnalyzer:
    def __init__(self, searcher: WebSearch):
        self.searcher = searcher

    async def analyze(self, app_idea: str, target_market: str) -> MarketSizing:
        sizing = MarketSizing()

        size_query = f"{target_market} market size 2024 2025"
        size_results = self.searcher.search_with_retry(size_query)
        sizing = self._extract_sizing(size_results)

        self.searcher.rate_limit()

        growth_query = f"{target_market} growth rate CAGR 2025"
        growth_results = self.searcher.search_with_retry(growth_query)
        growth_rate = self._extract_growth_rate(growth_results)
        if growth_rate:
            sizing.growth_rate = growth_rate

        if sizing.tam:
            sizing = self._derive_sam_som(sizing)

        if size_results:
            for r in size_results:
                if r.get("url"):
                    sizing.source = r["url"]
                    break

        return sizing

    def _extract_sizing(self, results: list[dict]) -> MarketSizing:
        sizing = MarketSizing()
        text = " ".join(r.get("snippet", "") for r in results)

        tam_patterns = [
            r"(?:total|tam|market)[^\$]*\$([0-9.,]+)\s*[bB]",
            r"\$\s*([0-9.,]+)\s*[bB](?:illion)?\s*(?:market|global|industry)",
            r"global[^\$]*\$([0-9.,]+)\s*[bB]",
        ]
        for pattern in tam_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                figure = match.group(1).replace(",", "")
                sizing.tam = f"${figure}B"
                break

        if not sizing.tam:
            short_patterns = [
                r"\$\s*([0-9.,]+)\s*[bB]",
                r"([0-9.,]+)\s*[bB](?:illion)?",
            ]
            for pattern in short_patterns:
                match = re.search(pattern, text)
                if match:
                    figure = match.group(1).replace(",", "")
                    try:
                        val = float(figure)
                        if val >= 1:
                            sizing.tam = f"${figure}B"
                            break
                    except ValueError:
                        pass

        return sizing

    def _extract_growth_rate(self, results: list[dict]) -> str:
        text = " ".join(r.get("snippet", "") for r in results)
        patterns = [
            r"([0-9.,]+)\s*%(?:\s*/\s*year|\s*CAGR)",
            r"CAGR[^\d]*([0-9.,]+)\s*%",
            r"grow(?:s|th)?[^\d]*([0-9.,]+)\s*%",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"~{match.group(1)}%/year"
        return ""

    def _derive_sam_som(self, sizing: MarketSizing) -> MarketSizing:
        try:
            tam_val = float(sizing.tam.replace("$", "").replace("B", "").replace(",", ""))
            sam = tam_val * 0.40
            som = tam_val * 0.40 * 0.10
            sizing.sam = f"${sam:.1f}B"
            sizing.som = f"${som:.1f}B"
        except (ValueError, AttributeError):
            pass
        return sizing
