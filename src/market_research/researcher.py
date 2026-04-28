import asyncio

from .competitor import CompetitorAnalyzer
from .market_sizing import MarketSizingAnalyzer
from .positioning import PositioningAnalyzer
from .report import MarketAnalysisReport
from .trends import TrendAnalyzer
from .web_search import WebSearch


class MarketResearcher:
    def __init__(self, rate_limit_delay: float = 1.0, max_retries: int = 3):
        self.searcher = WebSearch(rate_limit_delay=rate_limit_delay, max_retries=max_retries)
        self.competitor_analyzer = CompetitorAnalyzer(self.searcher)
        self.sizing_analyzer = MarketSizingAnalyzer(self.searcher)
        self.trend_analyzer = TrendAnalyzer(self.searcher)
        self.positioning_analyzer = PositioningAnalyzer()

    async def analyze(self, app_idea: str, target_market: str, regions: list[str] | None = None) -> MarketAnalysisReport:
        report = MarketAnalysisReport(app_idea=app_idea, target_market=target_market)

        try:
            competitor_task = asyncio.create_task(
                self.competitor_analyzer.analyze(app_idea, target_market)
            )
            sizing_task = asyncio.create_task(
                self.sizing_analyzer.analyze(app_idea, target_market)
            )
            trends_task = asyncio.create_task(
                self.trend_analyzer.analyze(app_idea, target_market)
            )

            competitor_result, sizing_result, trends_result = await asyncio.gather(
                competitor_task, sizing_task, trends_task, return_exceptions=True
            )

            if isinstance(competitor_result, Exception):
                report.warning = "Competitor analysis failed, results may be incomplete"
                report.competitors = []
            else:
                report.competitors, competitor_sources = competitor_result
                report.sources.extend(competitor_sources)

            if isinstance(sizing_result, Exception):
                report.warning = report.warning or "Market sizing failed"
            else:
                report.market_sizing = sizing_result

            if isinstance(trends_result, Exception):
                report.warning = report.warning or "Trend analysis failed"
                report.trends = []
            else:
                report.trends = trends_result

            if not report.competitors and not report.trends:
                report.warning = "Limited data found for this market. Consider broadening the target market or app idea."

            report.positioning = self.positioning_analyzer.analyze(
                competitors=report.competitors,
                trends=report.trends,
                app_idea=app_idea,
            )

        except Exception as e:
            report.error = str(e)

        return report
