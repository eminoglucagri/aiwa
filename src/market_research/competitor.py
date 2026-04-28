import re

from .report import CompetitorProfile
from .web_search import WebSearch


class CompetitorAnalyzer:
    def __init__(self, searcher: WebSearch):
        self.searcher = searcher

    async def analyze(self, app_idea: str, target_market: str) -> tuple[list[CompetitorProfile], list[str]]:
        competitors = []
        sources = []

        seed_query = f"{app_idea} {target_market} competitors software"
        seed_results = self.searcher.search_with_retry(seed_query)
        sources.extend(r["url"] for r in seed_results if r.get("url") and r["url"].startswith("http"))

        competitor_names = self._extract_competitor_names(seed_results, app_idea)

        for name in competitor_names[:5]:
            self.searcher.rate_limit()
            profile = self._profile_competitor(name, target_market)
            if profile:
                competitors.append(profile)

        return competitors, sources

    def _extract_competitor_names(self, results: list[dict], app_idea: str) -> list[str]:
        names = []
        seen = set()
        for r in results:
            text = r.get("snippet", "") + " " + r.get("title", "")
            text = text.lower()
            common_names = [
                "Calendly", "Acuity", "Square Appointments", "Setmore", "Apptoto",
                "BookWhen", "Simply Book Me", "10to8", "HubSpot", "Zoho",
                "Mindbody", "Vagaro", "Aloe", "Doodle", "Calendly", "OnceHub",
            ]
            for name in common_names:
                if name.lower() in text and name.lower() not in seen:
                    names.append(name)
                    seen.add(name.lower())
                    if len(names) >= 5:
                        return names
        return names

    def _profile_competitor(self, name: str, target_market: str) -> CompetitorProfile | None:
        try:
            profile_query = f"{name} pricing features"
            results = self.searcher.search_with_retry(profile_query)

            features = []
            pricing = ""
            strengths = []
            weaknesses = []
            website = ""

            for r in results:
                url = r.get("url", "")
                if url and not website:
                    if "crunchbase" not in url and "owler" not in url:
                        website = url.split("?")[0].split("#")[0]

            snippet = " ".join(r.get("snippet", "") for r in results[:3])

            pricing_match = re.search(r"\$\d+[/\\-]?\w*", snippet)
            if pricing_match:
                pricing = pricing_match.group(0)

            if "free" in snippet.lower() or "free plan" in snippet.lower():
                features.append("Free plan available")

            if "api" in snippet.lower():
                features.append("API access")
            if "integrat" in snippet.lower():
                features.append("Integrations")
            if "calendar" in snippet.lower() or "calendar sync" in snippet.lower():
                features.append("Calendar sync")
            if "sms" in snippet.lower() or "text" in snippet.lower():
                features.append("SMS/email reminders")
            if "recurring" in snippet.lower():
                features.append("Recurring appointments")
            if "payment" in snippet.lower():
                features.append("Online payments")

            if "easy" in snippet.lower() or "simple" in snippet.lower():
                strengths.append("Ease of use")
            if "popular" in snippet.lower() or "widely used" in snippet.lower():
                strengths.append("Strong user base")
            if "affordable" in snippet.lower() or "cheap" in snippet.lower():
                strengths.append("Affordable pricing")

            if "limit" in snippet.lower():
                weaknesses.append("Limited features in base plan")
            if "complex" in snippet.lower():
                weaknesses.append("Complex setup")
            if "expensive" in snippet.lower():
                weaknesses.append("Expensive at scale")

            if not website:
                return None

            return CompetitorProfile(
                name=name,
                website=website,
                pricing=pricing,
                key_features=features[:5],
                strengths=strengths[:3],
                weaknesses=weaknesses[:3],
                market_position=f"Competitor in {target_market} space",
            )
        except Exception:
            return None
