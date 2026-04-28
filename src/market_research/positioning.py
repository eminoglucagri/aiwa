from .report import CompetitorProfile, Trend, PositioningAnalysis


class PositioningAnalyzer:
    def analyze(
        self,
        competitors: list[CompetitorProfile],
        trends: list[Trend],
        app_idea: str,
    ) -> PositioningAnalysis:
        opportunities = self._identify_opportunities(competitors, trends)
        gaps = self._identify_gaps(competitors)
        swot = self._build_swot(competitors, trends, opportunities, gaps)
        recommendation = self._generate_recommendation(app_idea, competitors, opportunities, gaps)

        return PositioningAnalysis(
            opportunities=opportunities,
            gaps=gaps,
            swot=swot,
            recommendation=recommendation,
        )

    def _identify_opportunities(self, competitors: list[CompetitorProfile], trends: list[Trend]) -> list[str]:
        opportunities = []
        high_trends = [t for t in trends if t.relevance == "high"]
        for t in high_trends:
            opportunities.append(f"Capitalize on trend: {t.title}")

        common_weaknesses = set()
        for c in competitors:
            for w in c.weaknesses:
                common_weaknesses.add(w.lower())
        if common_weaknesses:
            opportunities.append(f"Differentiate by addressing common competitor weaknesses: {', '.join(list(common_weaknesses)[:3])}")

        pricing_white_space = True
        for c in competitors:
            if c.pricing and "free" in c.pricing.lower():
                pricing_white_space = False
        if pricing_white_space:
            opportunities.append("Pricing white space: no competitor offers a compelling free tier")

        return opportunities[:5]

    def _identify_gaps(self, competitors: list[CompetitorProfile]) -> list[str]:
        gaps = []
        all_features: set[str] = set()
        for c in competitors:
            for f in c.key_features:
                all_features.add(f.lower())

        common_features = {"api access", "integrations", "calendar sync", "sms/email reminders", "recurring appointments", "online payments"}
        missing = [f for f in common_features if f not in all_features]
        if missing:
            gaps.append(f"Underserved features: {', '.join(missing[:3])}")

        mobile_only = all("mobile" in c.market_position.lower() or "ios" in c.market_position.lower() or "android" in c.market_position.lower() for c in competitors if c.market_position)
        if not mobile_only:
            gaps.append("Desktop/web-first experience may be underserved")

        return gaps[:4]

    def _build_swot(
        self,
        competitors: list[CompetitorProfile],
        trends: list[Trend],
        opportunities: list[str],
        gaps: list[str],
    ) -> dict[str, list[str]]:
        strengths = []
        for c in competitors:
            for s in c.strengths:
                if s not in strengths:
                    strengths.append(s)
        strengths = strengths[:4] or ["AI-powered automation", "Modern web platform"]

        weaknesses = []
        for c in competitors:
            for w in c.weaknesses:
                if w not in weaknesses:
                    weaknesses.append(w)
        weaknesses = weaknesses[:4] or ["Limited free tier", "Complex setup for non-technical users"]

        threats = []
        for c in competitors:
            if c.name:
                threats.append(f"{c.name} entrenched market position")
        threats = threats[:3]

        if len(trends) > 3:
            threats.append("Rapid AI advancement may lower barrier to entry")

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities[:4],
            "threats": threats[:4],
        }

    def _generate_recommendation(
        self,
        app_idea: str,
        competitors: list[CompetitorProfile],
        opportunities: list[str],
        gaps: list[str],
    ) -> str:
        if not competitors:
            return (
                f"The market for \"{app_idea}\" appears uncrowded. "
                "Conduct primary research to validate demand before heavy investment. "
                "A first-mover advantage is possible if the market is verified."
            )

        rec = f"\"{app_idea}\" has market potential with {len(competitors)} identified competitor(s). "
        if opportunities:
            rec += f"Key opportunity: {opportunities[0]}. "
        if gaps:
            rec += f"Key gap to address: {gaps[0]}. "
        rec += "Recommendation: focus on a differentiated angle (e.g., AI automation, pricing disruption, or underserved vertical) and validate with user interviews before full build."
        return rec
